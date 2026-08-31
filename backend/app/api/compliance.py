"""Compliance evaluation API."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.responses import ComplianceSummaryResponse
from app.services.audit_service import AuditService, AuditAction, AuditCategory

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/compliance")


@router.post("/bids/{bid_id}/evaluate", response_model=ComplianceSummaryResponse)
async def evaluate_bid_compliance(
    request: Request,
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ANALYST", "ADMIN")),
):
    """
    Run deterministic compliance evaluation for a bid.
    CRITICAL: No LLM involved — pure Python rule evaluation.
    """
    from app.repositories.bids import BidRepository
    from app.repositories.tenders import TenderRequirementRepository
    from app.engines.compliance_engine.engine import ComplianceEngine
    from datetime import UTC, datetime

    bid_repo = BidRepository(db)
    audit = AuditService(db)
    request_id = getattr(request.state, "request_id", None)

    bid = await bid_repo.get_by_id(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")

    # Get approved rules for this tender
    req_repo = TenderRequirementRepository(db)
    requirements = await req_repo.get_approved_rules(bid.tender_id)

    if not requirements:
        # Return a manual review result if no rules are configured
        return ComplianceSummaryResponse(
            bid_id=bid_id,
            overall_result="MANUAL_REVIEW",
            compliance_score=0.0,
            total_rules=0,
            mandatory_rules=0,
            mandatory_passes=0,
            mandatory_fails=0,
            warnings=["No approved compliance rules found for this tender. Manual review required."],
            rule_results=[],
            evaluated_at=datetime.now(UTC),
        )

    # Build extracted data from bid/documents (simplified for Phase 1)
    extracted_data = {}
    if bid.compliance_summary and "extracted_data" in bid.compliance_summary:
        extracted_data = bid.compliance_summary["extracted_data"]

    engine = ComplianceEngine()
    rule_defs = [r.rule_definition for r in requirements if r.rule_definition]
    summary = engine.evaluate_all_rules(rule_defs, extracted_data)

    # Persist compliance summary to bid
    from datetime import UTC, datetime
    summary["evaluated_at"] = datetime.now(UTC).isoformat()
    await bid_repo.update(bid, {
        "compliance_result": summary["overall_result"],
        "compliance_summary": summary,
        "compliance_score": 100.0 - summary["compliance_score"],  # Convert to risk score
        "status": "COMPLIANCE_EVALUATED",
    })

    await audit.log(
        AuditAction.RULE_EVALUATION, AuditCategory.COMPLIANCE,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="BID", entity_id=bid_id, bid_id=bid_id,
        new_value={
            "overall_result": summary["overall_result"],
            "rules_evaluated": summary["total_rules"],
            "mandatory_fails": summary["mandatory_fails"],
        },
        rule_version="1.0",
        source="COMPLIANCE_API", request_id=request_id,
    )

    return ComplianceSummaryResponse(
        bid_id=bid_id,
        **summary,
    )
