"""Officer Decision Workflow API Router."""
from typing import List, Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.bid import Bid
from app.models.decision import OfficerDecision
from app.models.audit import AuditEvent
from app.services.decision_workflow import DecisionWorkflowService, DecisionState, DecisionType, RejectReasonCategory
from app.services.decision_readiness import decision_readiness

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/bids")

class DecisionSubmitRequest(BaseModel):
    decision: DecisionType
    justification: str = Field(..., min_length=10, description="Mandatory written justification")
    reason_category: Optional[RejectReasonCategory] = None
    evidence_ids: Optional[List[str]] = None
    override: bool = False
    override_reason: Optional[str] = None

class StateTransitionRequest(BaseModel):
    new_state: DecisionState
    notes: Optional[str] = None

@router.post("/{bid_id}/review")
async def transition_review_state(
    bid_id: str,
    payload: StateTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "PROCUREMENT_OFFICER")),
):
    service = DecisionWorkflowService(db)
    return await service.transition_state(bid_id, payload.new_state, officer_id=current_user.id, notes=payload.notes)

@router.post("/{bid_id}/decision")
async def submit_bid_decision(
    bid_id: str,
    payload: DecisionSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "PROCUREMENT_OFFICER")),
):
    service = DecisionWorkflowService(db)
    return await service.submit_officer_decision(
        bid_id=bid_id,
        officer_id=current_user.id,
        decision_type=payload.decision,
        justification=payload.justification,
        reason_category=payload.reason_category,
        evidence_ids=payload.evidence_ids,
        is_override=payload.override,
        override_reason=payload.override_reason,
    )

@router.post("/{bid_id}/clarification")
async def request_clarification(
    bid_id: str,
    payload: StateTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "PROCUREMENT_OFFICER")),
):
    service = DecisionWorkflowService(db)
    return await service.transition_state(bid_id, DecisionState.CLARIFICATION_REQUIRED, officer_id=current_user.id, notes=payload.notes)

@router.post("/{bid_id}/escalate")
async def escalate_review(
    bid_id: str,
    payload: StateTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "PROCUREMENT_OFFICER")),
):
    service = DecisionWorkflowService(db)
    return await service.transition_state(bid_id, DecisionState.ESCALATED, officer_id=current_user.id, notes=payload.notes)

@router.post("/{bid_id}/reopen-review")
async def reopen_review(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "PROCUREMENT_OFFICER")),
):
    res = await db.execute(select(Bid).where(Bid.id == bid_id))
    bid = res.scalar_one_or_none()
    if not bid:
        raise HTTPException(404, "Bid not found.")
    bid.status = DecisionState.UNDER_REVIEW.value
    await db.commit()
    return {"bid_id": bid_id, "status": "UNDER_REVIEW", "message": "Review reopened by officer."}

@router.get("/{bid_id}/decision-history")
async def get_decision_history(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(
        select(AuditEvent)
        .where(AuditEvent.bid_id == bid_id)
        .order_by(asc(AuditEvent.timestamp))
    )
    events = res.scalars().all()
    timeline = []
    for ev in events:
        timeline.append({
            "event_id": ev.id,
            "action": ev.action,
            "user_email": ev.user_email or "SYSTEM",
            "timestamp": ev.timestamp.isoformat(),
            "summary": ev.change_summary,
            "details": ev.new_value,
            "hash": ev.event_hash,
        })
    return {"bid_id": bid_id, "timeline": timeline, "total_events": len(timeline)}

@router.get("/{bid_id}/decision")
async def get_current_decision(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Bid).where(Bid.id == bid_id))
    bid = res.scalar_one_or_none()
    if not bid:
        raise HTTPException(404, "Bid not found.")

    dec_res = await db.execute(select(OfficerDecision).where(OfficerDecision.bid_id == bid_id).order_by(OfficerDecision.decided_at.desc()))
    latest_decision = dec_res.scalars().first()

    return {
        "bid_id": bid_id,
        "status": bid.status,
        "latest_decision": {
            "id": latest_decision.id,
            "decision": latest_decision.decision,
            "reason": latest_decision.reason,
            "override_justification": latest_decision.override_justification,
            "decided_at": latest_decision.decided_at.isoformat(),
        } if latest_decision else None,
    }

@router.get("/{bid_id}/decision-snapshot")
async def get_decision_snapshot(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snapshot = await decision_readiness.calculate_readiness(db, bid_id)
    return {"bid_id": bid_id, "snapshot": snapshot, "snapshot_timestamp": snapshot.get("evaluated_at")}
