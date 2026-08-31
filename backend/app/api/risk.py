"""Risk calculation API."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.responses import RiskScoreResponse
from app.services.audit_service import AuditService, AuditAction, AuditCategory

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/risk")


@router.post("/bids/{bid_id}/calculate", response_model=RiskScoreResponse)
async def calculate_risk(
    request: Request,
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ANALYST", "ADMIN")),
):
    """Calculate comprehensive risk score for a bid using the 5-component risk engine."""
    from app.repositories.bids import BidRepository
    from app.repositories.misc import RiskRepository
    from app.services.risk_service import recalculate_bid_risk

    bid_repo = BidRepository(db)
    bid = await bid_repo.get_by_id(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")

    await recalculate_bid_risk(db, bid_id, source="RISK_API")

    risk_repo = RiskRepository(db)
    risk_with_factors = await risk_repo.get_latest_for_bid(bid_id)
    return risk_with_factors

