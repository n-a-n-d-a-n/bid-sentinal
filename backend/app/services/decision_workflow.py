"""
Officer Decision Workflow & Decision Governance Service.

Formal State Machine:
PENDING_REVIEW -> UNDER_REVIEW -> CLARIFICATION_REQUIRED | READY_FOR_DECISION | ESCALATED -> APPROVED | REJECTED

Governing Principles:
1. AI/ML system NEVER makes final procurement decisions autonomously.
2. System recommendation vs Officer decision are explicitly separated.
3. Every final decision requires written justification.
4. Overrides are explicitly flagged and recorded with justifications.
5. Decision snapshots preserve exact information available to officer at decision time.
"""
from enum import Enum
import structlog
from typing import Dict, Any, List, Optional
from datetime import UTC, datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bid import Bid
from app.models.decision import OfficerDecision
from app.engines.audit.ledger import AuditLedgerService
from app.services.decision_readiness import decision_readiness

logger = structlog.get_logger(__name__)

class DecisionState(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    READY_FOR_DECISION = "READY_FOR_DECISION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RETURNED = "RETURNED"
    ESCALATED = "ESCALATED"
    WITHDRAWN = "WITHDRAWN"

class DecisionType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    RETURN_FOR_CLARIFICATION = "RETURN_FOR_CLARIFICATION"
    ESCALATE = "ESCALATE"

class RejectReasonCategory(str, Enum):
    NON_COMPLIANCE = "NON_COMPLIANCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    VERIFICATION_MISMATCH = "VERIFICATION_MISMATCH"
    DOCUMENTATION_ISSUE = "DOCUMENTATION_ISSUE"
    POLICY_REQUIREMENT = "POLICY_REQUIREMENT"
    OTHER = "OTHER"

VALID_TRANSITIONS = {
    DecisionState.PENDING_REVIEW: [DecisionState.UNDER_REVIEW],
    DecisionState.UNDER_REVIEW: [DecisionState.CLARIFICATION_REQUIRED, DecisionState.READY_FOR_DECISION, DecisionState.ESCALATED],
    DecisionState.CLARIFICATION_REQUIRED: [DecisionState.UNDER_REVIEW],
    DecisionState.READY_FOR_DECISION: [DecisionState.APPROVED, DecisionState.REJECTED, DecisionState.UNDER_REVIEW],
    DecisionState.ESCALATED: [DecisionState.UNDER_REVIEW],
}

class DecisionWorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ledger = AuditLedgerService(db)

    def validate_transition(self, current_state: str, new_state: str):
        curr_enum = DecisionState(current_state)
        new_enum = DecisionState(new_state)
        allowed = VALID_TRANSITIONS.get(curr_enum, [])
        if new_enum not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Illegal decision state transition from '{current_state}' to '{new_state}'. Allowed: {[s.value for s in allowed]}",
            )

    async def transition_state(
        self,
        bid_id: str,
        new_state: DecisionState,
        officer_id: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        res = await self.db.execute(select(Bid).where(Bid.id == bid_id))
        bid = res.scalar_one_or_none()
        if not bid:
            raise HTTPException(404, "Bid not found.")

        current_state = bid.status if bid.status in DecisionState.__members__ else DecisionState.PENDING_REVIEW.value
        self.validate_transition(current_state, new_state.value)

        bid.status = new_state.value
        await self.db.commit()

        await self.ledger.append_event(
            action="DECISION_STATE_CHANGED",
            action_category="DECISION",
            entity_type="BID",
            entity_id=bid_id,
            user_id=officer_id,
            bid_id=bid_id,
            old_value={"status": current_state},
            new_value={"status": new_state.value, "notes": notes},
            change_summary=f"Decision state transitioned from {current_state} to {new_state.value}.",
        )

        return {"bid_id": bid_id, "previous_state": current_state, "new_state": new_state.value}

    async def submit_officer_decision(
        self,
        bid_id: str,
        officer_id: str,
        decision_type: DecisionType,
        justification: str,
        reason_category: Optional[RejectReasonCategory] = None,
        evidence_ids: Optional[List[str]] = None,
        is_override: bool = False,
        override_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        # 1. Mandatory Justification Check
        if not justification or len(justification.strip()) < 10:
            raise HTTPException(400, "Mandatory written justification of at least 10 characters is required.")

        # 2. Reject Reason Category Check
        if decision_type == DecisionType.REJECT and not reason_category:
            raise HTTPException(400, "Structured reason_category is mandatory for REJECT decisions.")

        res = await self.db.execute(select(Bid).where(Bid.id == bid_id))
        bid = res.scalar_one_or_none()
        if not bid:
            raise HTTPException(404, "Bid not found.")

        # Calculate system recommendation & readiness
        sys_readiness = await decision_readiness.calculate_readiness(self.db, bid_id)
        sys_rec = sys_readiness["status"]

        # Map DecisionType to new state
        if decision_type == DecisionType.APPROVE:
            new_state = "APPROVED"
        elif decision_type == DecisionType.REJECT:
            new_state = "REJECTED"
        elif decision_type == DecisionType.RETURN_FOR_CLARIFICATION:
            new_state = "CLARIFICATION_REQUIRED"
        else:
            new_state = "ESCALATED"

        # Check for Override (e.g. system recommended BLOCKED or MANUAL_REVIEW, but officer APPROVED)
        if sys_rec in ("BLOCKED", "MANUAL_REVIEW_REQUIRED") and decision_type == DecisionType.APPROVE:
            is_override = True
            if not override_reason:
                override_reason = justification

        # Save OfficerDecision record
        decision_record = OfficerDecision(
            bid_id=bid_id,
            officer_id=officer_id,
            decision=decision_type.value,
            previous_result=bid.status,
            new_result=new_state,
            reason=justification,
            evidence_reviewed={"evidence_ids": evidence_ids or []},
            override_justification=override_reason if is_override else None,
            risk_score_snapshot=sys_readiness,
            is_final=True,
        )
        self.db.add(decision_record)

        bid.status = new_state
        await self.db.commit()

        # Audit Event
        await self.ledger.append_event(
            action="DECISION_SUBMITTED",
            action_category="DECISION",
            entity_type="BID",
            entity_id=bid_id,
            user_id=officer_id,
            bid_id=bid_id,
            new_value={
                "decision_type": decision_type.value,
                "system_recommendation": sys_rec,
                "officer_decision": new_state,
                "is_override": is_override,
                "justification": justification,
                "reason_category": reason_category.value if reason_category else None,
                "evidence_ids": evidence_ids or [],
            },
            change_summary=f"Officer recorded final decision ({decision_type.value}) for bid.",
        )

        return {
            "decision_id": decision_record.id,
            "bid_id": bid_id,
            "system_recommendation": sys_rec,
            "officer_decision": new_state,
            "is_override": is_override,
            "justification": justification,
            "reason_category": reason_category.value if reason_category else None,
            "status": new_state,
        }

decision_workflow = DecisionWorkflowService
