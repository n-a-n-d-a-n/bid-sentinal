"""Tamper-Evident Audit Ledger API Router."""
from typing import Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.audit import AuditEvent
from app.engines.audit.verifier import AuditVerifierService
from app.repositories.misc import AuditRepository
from app.schemas.responses import AuditEventResponse
from app.schemas.common import PaginatedResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/audit")

@router.get("", response_model=PaginatedResponse[AuditEventResponse])
async def list_audit_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    bid_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = AuditRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_paginated(
        offset=offset, limit=page_size,
        action=action, category=category,
        user_id=user_id, bid_id=bid_id,
    )
    total = await repo.count_filtered()
    return PaginatedResponse.create(
        items=[AuditEventResponse.model_validate(e) for e in items],
        total=total, page=page, page_size=page_size,
    )

@router.get("/verify")
async def verify_global_audit_chain(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Verifies global audit ledger cryptographic hash chain integrity.
    """
    verifier = AuditVerifierService(db)
    return await verifier.verify_chain()

@router.get("/verify/{entity_type}/{entity_id}")
async def verify_entity_audit_chain(
    entity_type: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Verifies entity-specific audit ledger cryptographic hash chain integrity.
    """
    verifier = AuditVerifierService(db)
    return await verifier.verify_chain(entity_id=entity_id)

@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_audit_events(
    entity_type: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(
        select(AuditEvent)
        .where(AuditEvent.entity_type == entity_type.upper(), AuditEvent.entity_id == entity_id)
        .order_by(desc(AuditEvent.timestamp))
    )
    events = res.scalars().all()
    return {"entity_type": entity_type, "entity_id": entity_id, "events": events, "count": len(events)}
