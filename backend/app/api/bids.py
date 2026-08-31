"""Bids API router — bid creation, analysis, verification, compliance, risk, decisions, consistency, contradictions, readiness."""
from typing import Optional, List, Dict, Any
import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.bid import Bid
from app.models.document import Document, ExtractedField
from app.models.verification import VerificationResult
from app.models.bidder import Bidder
from app.models.user import User
from app.repositories.bids import BidRepository
from app.repositories.misc import (
    AuditRepository, DecisionRepository, RiskRepository, VerificationRepository,
)
from app.schemas.bid import BidCreate, BidUpdate, BidResponse, DecisionCreate, DecisionResponse
from app.schemas.responses import ComplianceSummaryResponse, RiskScoreResponse, AuditEventResponse
from app.schemas.common import PaginatedResponse
from app.schemas.verification import VerificationSummary, VerifyRequest
from app.services.audit_service import AuditService, AuditAction, AuditCategory
from app.engines.consistency import contradiction_engine
from app.services.decision_readiness import decision_readiness

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/bids")


@router.post("", response_model=BidResponse, status_code=201)
async def create_bid(
    request: Request,
    payload: BidCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ANALYST", "ADMIN")),
):
    from app.repositories.tenders import TenderRepository
    from app.repositories.bidders import BidderRepository

    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    # Validate foreign keys
    if not await TenderRepository(db).get_by_id(payload.tender_id):
        raise HTTPException(404, "Tender not found.")
    if not await BidderRepository(db).get_by_id(payload.bidder_id):
        raise HTTPException(404, "Bidder not found.")

    bid = Bid(
        tender_id=payload.tender_id,
        bidder_id=payload.bidder_id,
        bid_reference_number=payload.bid_reference_number,
        quoted_price_inr=payload.quoted_price_inr,
        quoted_price_currency=payload.quoted_price_currency,
        bid_validity_days=payload.bid_validity_days,
        submission_timestamp=payload.submission_timestamp,
        status="UPLOADED",
    )
    await BidRepository(db).create(bid)

    await audit.log(
        AuditAction.BID_CREATE, AuditCategory.DOCUMENT,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="BID", entity_id=bid.id,
        bid_id=bid.id, tender_id=payload.tender_id,
        new_value={"bidder_id": payload.bidder_id, "tender_id": payload.tender_id},
        source="BID_API", request_id=request_id,
    )
    return bid


@router.get("", response_model=PaginatedResponse[BidResponse])
async def list_bids(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tender_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = BidRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_paginated(offset=offset, limit=page_size, tender_id=tender_id, status=status, risk_level=risk_level)
    total = await repo.count_filtered(tender_id=tender_id, status=status, risk_level=risk_level)
    return PaginatedResponse.create(
        items=[BidResponse.model_validate(b) for b in items],
        total=total, page=page, page_size=page_size,
    )


@router.get("/{bid_id}", response_model=BidResponse)
async def get_bid(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = await BidRepository(db).get_with_relations(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")
    return bid


@router.post("/{bid_id}/analyze")
async def analyze_bid(
    request: Request,
    bid_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ANALYST", "ADMIN")),
):
    """Trigger full bid analysis pipeline (async)."""
    from app.workers.tasks import analyze_bid_task
    repo = BidRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    bid = await repo.get_by_id(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")

    # Create processing job
    from app.models.job import ProcessingJob
    job = ProcessingJob(
        job_type="BID_ANALYSIS",
        entity_type="BID",
        entity_id=bid_id,
        status="QUEUED",
        total_steps=7,
        created_by=current_user.id,
    )
    db.add(job)
    await db.flush()

    await repo.update(bid, {"status": "PROCESSING", "processing_job_id": job.id})

    await audit.log(
        AuditAction.BID_ANALYSIS_START, AuditCategory.COMPLIANCE,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="BID", entity_id=bid_id, bid_id=bid_id,
        new_value={"job_id": job.id},
        source="BID_API", request_id=request_id,
    )

    background_tasks.add_task(analyze_bid_task, bid_id=bid_id, job_id=job.id)
    return {"job_id": job.id, "status": "QUEUED", "message": "Bid analysis started."}


@router.post("/{bid_id}/reanalyze")
async def reanalyze_bid(
    request: Request,
    bid_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ANALYST", "ADMIN")),
):
    """Idempotently reanalyzes a bid."""
    return await analyze_bid(request, bid_id, background_tasks, db, current_user)


@router.get("/{bid_id}/compliance", response_model=ComplianceSummaryResponse)
async def get_bid_compliance(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = await BidRepository(db).get_by_id(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")
    if not bid.compliance_summary:
        raise HTTPException(404, "Compliance evaluation not yet available. Run /analyze first.")
    return ComplianceSummaryResponse(
        bid_id=bid_id,
        **bid.compliance_summary,
    )


@router.get("/{bid_id}/contradictions")
async def get_bid_contradictions(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Evaluates cross-document and cross-source contradictions for a bid."""
    bid = await BidRepository(db).get_by_id(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")

    # Fetch extractions & verifications
    ef_res = await db.execute(select(ExtractedField).where(ExtractedField.bid_id == bid_id))
    ef_list = [{"field_name": f.field_name, "field_value": f.field_value, "document_id": f.document_id, "page_number": f.page_number} for f in ef_res.scalars().all()]

    vr_res = await db.execute(select(VerificationResult).where(VerificationResult.bid_id == bid_id))
    vr_list = [{"provider": v.provider, "status": v.status, "queried_identifier": v.queried_identifier, "conflict_details": v.conflict_details} for v in vr_res.scalars().all()]

    contradictions = contradiction_engine.evaluate_contradictions(ef_list, vr_list, {})
    return {"bid_id": bid_id, "contradictions": contradictions, "count": len(contradictions)}


@router.get("/{bid_id}/decision-readiness")
async def get_bid_decision_readiness(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculates decision readiness status for Procurement Officer."""
    bid = await BidRepository(db).get_by_id(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")

    comp_summary = bid.compliance_summary or {}

    ef_res = await db.execute(select(ExtractedField).where(ExtractedField.bid_id == bid_id))
    ef_list = [{"field_name": f.field_name, "field_value": f.field_value, "document_id": f.document_id, "page_number": f.page_number} for f in ef_res.scalars().all()]

    vr_res = await db.execute(select(VerificationResult).where(VerificationResult.bid_id == bid_id))
    vr_list = [{"provider": v.provider, "status": v.status, "queried_identifier": v.queried_identifier, "conflict_details": v.conflict_details} for v in vr_res.scalars().all()]

    contradictions = contradiction_engine.evaluate_contradictions(ef_list, vr_list, {})
    readiness = decision_readiness.calculate_readiness(comp_summary, contradictions, vr_list)

    return {"bid_id": bid_id, **readiness}


@router.get("/{bid_id}/risk", response_model=RiskScoreResponse)
async def get_bid_risk(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    risk_repo = RiskRepository(db)
    risk = await risk_repo.get_latest_for_bid(bid_id)
    if not risk:
        raise HTTPException(404, "Risk score not yet calculated. Run /analyze first.")
    return risk


@router.get("/{bid_id}/verification", response_model=VerificationSummary)
async def get_bid_verification(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    v_repo = VerificationRepository(db)
    results = await v_repo.get_by_bid(bid_id)
    if not results:
        raise HTTPException(404, "Verification results not yet available.")

    from app.schemas.verification import VerificationResultResponse
    statuses = [r.status for r in results]
    return VerificationSummary(
        bid_id=bid_id,
        total=len(results),
        verified=statuses.count("VERIFIED"),
        conflicts=statuses.count("CONFLICT"),
        unavailable=statuses.count("UNAVAILABLE"),
        not_found=statuses.count("NOT_FOUND"),
        unauthorized=statuses.count("UNAUTHORIZED"),
        pending=statuses.count("PENDING"),
        results=[VerificationResultResponse.model_validate(r) for r in results],
        has_blocking_unavailable="UNAVAILABLE" in statuses,
        can_auto_pass=all(s == "VERIFIED" for s in statuses) and len(statuses) > 0,
    )


@router.get("/{bid_id}/audit", response_model=list[AuditEventResponse])
async def get_bid_audit(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    audit_repo = AuditRepository(db)
    events = await audit_repo.get_for_bid(bid_id)
    return [AuditEventResponse.model_validate(e) for e in events]


@router.post("/{bid_id}/decision", response_model=DecisionResponse, status_code=201)
async def record_decision(
    request: Request,
    bid_id: str,
    payload: DecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ADMIN")),
):
    """Officer records final procurement decision. Reason is mandatory."""
    from app.models.decision import OfficerDecision
    from datetime import UTC, datetime

    bid_repo = BidRepository(db)
    decision_repo = DecisionRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    bid = await bid_repo.get_by_id(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")

    if not payload.reason or len(payload.reason.strip()) < 10:
        raise HTTPException(422, "Decision reason is mandatory and must be at least 10 characters.")

    risk_repo = RiskRepository(db)
    latest_risk = await risk_repo.get_latest_for_bid(bid_id)
    risk_snapshot = None
    if latest_risk:
        risk_snapshot = {
            "overall_risk_score": latest_risk.overall_risk_score,
            "risk_level": latest_risk.risk_level,
            "compliance_score": latest_risk.compliance_score,
        }

    decision = OfficerDecision(
        bid_id=bid_id,
        officer_id=current_user.id,
        decision=payload.decision,
        previous_result=bid.decision,
        new_result=payload.decision,
        reason=payload.reason.strip(),
        override_justification=payload.override_justification,
        evidence_reviewed=payload.evidence_reviewed,
        rule_version="1.0",
        model_version="risk_engine_v1",
        risk_score_snapshot=risk_snapshot,
        is_final=True,
        decided_at=datetime.now(UTC),
    )
    await decision_repo.create(decision)

    await bid_repo.update(bid, {
        "decision": payload.decision,
        "decision_by": current_user.id,
        "decision_at": datetime.now(UTC),
        "decision_reason": payload.reason,
        "status": "DECIDED",
    })

    await audit.log(
        AuditAction.OFFICER_DECISION, AuditCategory.DECISION,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="BID", entity_id=bid_id, bid_id=bid_id,
        old_value={"decision": bid.decision},
        new_value={"decision": payload.decision, "reason_length": len(payload.reason)},
        rule_version="1.0", model_version="risk_engine_v1",
        source="BID_API", request_id=request_id,
    )

    return decision
