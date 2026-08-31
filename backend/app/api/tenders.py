"""Tenders API router."""
from typing import Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.tender import Tender, TenderRequirement
from app.models.document import Document, DocumentPage
from app.models.user import User
from app.repositories.tenders import TenderRepository, TenderRequirementRepository
from app.schemas.common import PaginatedResponse, IDResponse
from app.schemas.tender import (
    TenderCreate, TenderUpdate, TenderResponse,
    TenderRequirementCreate, TenderRequirementUpdate, TenderRequirementResponse,
)
from app.services.audit_service import AuditService, AuditAction, AuditCategory
from app.engines.requirements.orchestrator import RequirementOrchestratorService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/tenders")


@router.post("", response_model=TenderResponse, status_code=201)
async def create_tender(
    request: Request,
    payload: TenderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ADMIN")),
):
    repo = TenderRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    if payload.gem_bid_number:
        existing = await repo.get_by_gem_bid_number(payload.gem_bid_number)
        if existing:
            raise HTTPException(409, f"Tender with GeM Bid Number '{payload.gem_bid_number}' already exists.")

    tender = Tender(
        title=payload.title,
        gem_bid_number=payload.gem_bid_number,
        description=payload.description,
        department=payload.department,
        ministry=payload.ministry,
        category=payload.category,
        estimated_value_inr=payload.estimated_value_inr,
        bid_submission_deadline=payload.bid_submission_deadline,
        technical_bid_opening=payload.technical_bid_opening,
        financial_bid_opening=payload.financial_bid_opening,
        published_date=payload.published_date,
        msme_applicable=payload.msme_applicable,
        startup_applicable=payload.startup_applicable,
        make_in_india=payload.make_in_india,
        local_content_min_pct=payload.local_content_min_pct,
        status="DRAFT",
        created_by=current_user.id,
    )
    await repo.create(tender)

    await audit.log(
        AuditAction.TENDER_CREATE, AuditCategory.DOCUMENT,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="TENDER", entity_id=tender.id, tender_id=tender.id,
        new_value={"title": tender.title, "gem_bid_number": tender.gem_bid_number},
        source="TENDER_API", request_id=request_id,
    )
    return tender


@router.get("", response_model=PaginatedResponse[TenderResponse])
async def list_tenders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TenderRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_paginated(offset=offset, limit=page_size, status=status)
    total = await repo.count_by_status(status=status)
    return PaginatedResponse.create(
        items=[TenderResponse.model_validate(t) for t in items],
        total=total, page=page, page_size=page_size,
    )


@router.get("/{tender_id}", response_model=TenderResponse)
async def get_tender(
    tender_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TenderRepository(db)
    tender = await repo.get_by_id(tender_id)
    if not tender:
        raise HTTPException(404, "Tender not found.")
    return tender


@router.patch("/{tender_id}", response_model=TenderResponse)
async def update_tender(
    request: Request,
    tender_id: str,
    payload: TenderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ADMIN")),
):
    repo = TenderRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    tender = await repo.get_by_id(tender_id)
    if not tender:
        raise HTTPException(404, "Tender not found.")

    old_vals = {"title": tender.title, "status": tender.status}
    update_data = payload.model_dump(exclude_none=True)
    tender = await repo.update(tender, update_data)

    await audit.log(
        AuditAction.TENDER_UPDATE, AuditCategory.DOCUMENT,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="TENDER", entity_id=tender_id, tender_id=tender_id,
        old_value=old_vals, new_value=update_data,
        source="TENDER_API", request_id=request_id,
    )
    return tender


@router.post("/{tender_id}/analyze")
async def analyze_tender(
    tender_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ADMIN")),
):
    """
    Extracts & normalizes tender requirements from uploaded tender documents.
    """
    trepo = TenderRepository(db)
    tender = await trepo.get_by_id(tender_id)
    if not tender:
        raise HTTPException(404, "Tender not found.")

    # Find pages of documents associated with this tender
    doc_res = await db.execute(select(Document).where(Document.entity_type == "tender", Document.entity_id == tender_id))
    docs = doc_res.scalars().all()

    pages_text = []
    for d in docs:
        p_res = await db.execute(select(DocumentPage).where(DocumentPage.document_id == d.id).order_by(DocumentPage.page_number))
        for p in p_res.scalars().all():
            pages_text.append({"page_number": p.page_number, "text": p.text or ""})

    if not pages_text:
        # Fallback default description requirement if no document pages uploaded
        pages_text = [{"page_number": 1, "text": f"{tender.title}\n{tender.description or ''}"}]

    orchestrator = RequirementOrchestratorService(db)
    saved_reqs = await orchestrator.extract_and_save_requirements(tender_id, pages_text)

    tender.status = "REQUIREMENTS_EXTRACTED"
    await db.commit()

    return {
        "tender_id": tender_id,
        "status": "REQUIREMENTS_EXTRACTED",
        "requirements_extracted": len(saved_reqs),
    }


# ── Requirements ────────────────────────────────────────────────────────────────

@router.get("/{tender_id}/requirements", response_model=list[TenderRequirementResponse])
async def get_requirements(
    tender_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trepo = TenderRepository(db)
    if not await trepo.get_by_id(tender_id):
        raise HTTPException(404, "Tender not found.")
    req_repo = TenderRequirementRepository(db)
    return await req_repo.get_by_tender(tender_id)


@router.post("/{tender_id}/requirements", response_model=TenderRequirementResponse, status_code=201)
async def add_requirement(
    request: Request,
    tender_id: str,
    payload: TenderRequirementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ADMIN")),
):
    trepo = TenderRepository(db)
    if not await trepo.get_by_id(tender_id):
        raise HTTPException(404, "Tender not found.")

    req_repo = TenderRequirementRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    req = TenderRequirement(
        tender_id=tender_id,
        requirement_id=payload.requirement_id,
        category=payload.category,
        description=payload.description,
        mandatory=payload.mandatory,
        rule_definition=payload.rule_definition,
        source_document=payload.source_document,
        source_page=payload.source_page,
        confidence=payload.confidence,
        effective_from=payload.effective_from,
        effective_until=payload.effective_until,
    )
    await req_repo.create(req)

    await audit.log(
        AuditAction.REQUIREMENT_CREATE, AuditCategory.COMPLIANCE,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="REQUIREMENT", entity_id=req.id, tender_id=tender_id,
        new_value={"category": req.category, "description": req.description[:100]},
        source="TENDER_API", request_id=request_id,
    )
    return req


@router.patch("/{tender_id}/requirements/{req_id}/approve", response_model=TenderRequirementResponse)
async def approve_requirement(
    request: Request,
    tender_id: str,
    req_id: str,
    payload: TenderRequirementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ADMIN")),
):
    req_repo = TenderRequirementRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    req = await req_repo.get_by_id(req_id)
    if not req or req.tender_id != tender_id:
        raise HTTPException(404, "Requirement not found.")

    from datetime import UTC, datetime
    update_data = {
        "is_approved": True,
        "approved_by": current_user.id,
        "approved_at": datetime.now(UTC),
    }
    if payload.officer_notes:
        update_data["officer_notes"] = payload.officer_notes
    if payload.rule_definition:
        update_data["rule_definition"] = payload.rule_definition
    if payload.description:
        update_data["description"] = payload.description

    req = await req_repo.update(req, update_data)

    await audit.log(
        AuditAction.REQUIREMENT_APPROVE, AuditCategory.COMPLIANCE,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="REQUIREMENT", entity_id=req_id, tender_id=tender_id,
        new_value={"approved": True, "approved_by": current_user.username},
        source="TENDER_API", request_id=request_id,
    )
    return req
