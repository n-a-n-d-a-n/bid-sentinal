"""Bidders API router."""
from typing import Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.bidder import Bidder, BidderIdentifier
from app.models.user import User
from app.repositories.bidders import BidderRepository
from app.schemas.common import PaginatedResponse
from app.schemas.bidder import BidderCreate, BidderUpdate, BidderResponse
from app.services.audit_service import AuditService, AuditAction, AuditCategory

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/bidders")


@router.post("", response_model=BidderResponse, status_code=201)
async def create_bidder(
    request: Request,
    payload: BidderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ANALYST", "ADMIN")),
):
    repo = BidderRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    # Deduplication by PAN (strongest identifier)
    if payload.pan:
        existing = await repo.get_by_pan(payload.pan.upper())
        if existing:
            raise HTTPException(409, f"Bidder with PAN {payload.pan} already exists (id: {existing.id}).")

    bidder = Bidder(
        canonical_name=payload.canonical_name,
        legal_name=payload.legal_name,
        trade_name=payload.trade_name,
        entity_type=payload.entity_type,
        pan=payload.pan.upper() if payload.pan else None,
        gstin=payload.gstin.upper() if payload.gstin else None,
        cin=payload.cin.upper() if payload.cin else None,
        udyam_number=payload.udyam_number,
        gem_seller_id=payload.gem_seller_id,
        registered_address=payload.registered_address,
        state=payload.state,
        pincode=payload.pincode,
        phone=payload.phone,
        email=str(payload.email) if payload.email else None,
        website=payload.website,
        incorporation_date=payload.incorporation_date,
        directors=payload.directors,
        msme_category=payload.msme_category,
        is_startup=payload.is_startup,
    )
    await repo.create(bidder)

    # Create additional identifiers if provided
    if payload.additional_identifiers:
        for ident_data in payload.additional_identifiers:
            ident = BidderIdentifier(
                bidder_id=bidder.id,
                identifier_type=ident_data.identifier_type,
                identifier_value=ident_data.identifier_value,
                is_primary=ident_data.is_primary,
                state=ident_data.state,
            )
            db.add(ident)
        await db.flush()

    await audit.log(
        AuditAction.BID_CREATE, AuditCategory.DOCUMENT,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="BIDDER", entity_id=bidder.id,
        new_value={"canonical_name": bidder.canonical_name, "pan": bidder.pan},
        source="BIDDER_API", request_id=request_id,
    )

    # Reload with identifiers
    bidder_with_ids = await repo.get_with_identifiers(bidder.id)
    return bidder_with_ids


@router.get("", response_model=PaginatedResponse[BidderResponse])
async def list_bidders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="Search by name, PAN, GSTIN, CIN"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = BidderRepository(db)
    offset = (page - 1) * page_size

    if q:
        items = await repo.search(q, limit=page_size)
        total = len(items)
    else:
        items = await repo.list_paginated(offset=offset, limit=page_size)
        total = await repo.count()

    return PaginatedResponse.create(
        items=[BidderResponse.model_validate(b) for b in items],
        total=total, page=page, page_size=page_size,
    )


@router.get("/{bidder_id}", response_model=BidderResponse)
async def get_bidder(
    bidder_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = BidderRepository(db)
    bidder = await repo.get_with_identifiers(bidder_id)
    if not bidder:
        raise HTTPException(404, "Bidder not found.")
    return bidder


@router.patch("/{bidder_id}", response_model=BidderResponse)
async def update_bidder(
    request: Request,
    bidder_id: str,
    payload: BidderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ADMIN")),
):
    repo = BidderRepository(db)
    bidder = await repo.get_by_id(bidder_id)
    if not bidder:
        raise HTTPException(404, "Bidder not found.")
    update_data = payload.model_dump(exclude_none=True)
    await repo.update(bidder, update_data)
    return await repo.get_with_identifiers(bidder_id)
