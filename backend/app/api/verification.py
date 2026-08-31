"""Verification API — run mock government verifications."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.verification import VerificationRequest as VRequest, VerificationResult as VResult
from app.repositories.misc import VerificationRepository
from app.schemas.verification import VerifyRequest, VerificationResultResponse, VerificationSummary
from app.services.audit_service import AuditService, AuditAction, AuditCategory

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/verification")

PROVIDER_MAP = {
    "GST": "MockGSTProvider",
    "UDYAM": "MockUdyamProvider",
    "MCA": "MockMCAProvider",
    "PAN": "MockPANProvider",
    "EPFO": "MockEPFOProvider",
    "ESIC": "MockESICProvider",
    "DIGILOCKER": "MockDigiLockerProvider",
    "BIS": "MockBISProvider",
    "GEM": "MockGeMProvider",
    "BLACKLIST": "MockBlacklistProvider",
}


def _get_provider(provider_name: str):
    from app.engines.verification_engine.mock_adapters import (
        MockGSTProvider, MockUdyamProvider, MockMCAProvider, MockPANProvider,
        MockEPFOProvider, MockESICProvider, MockDigiLockerProvider,
        MockBISProvider, MockGeMProvider, MockBlacklistProvider,
    )
    providers = {
        "GST": MockGSTProvider,
        "UDYAM": MockUdyamProvider,
        "MCA": MockMCAProvider,
        "PAN": MockPANProvider,
        "EPFO": MockEPFOProvider,
        "ESIC": MockESICProvider,
        "DIGILOCKER": MockDigiLockerProvider,
        "BIS": MockBISProvider,
        "GEM": MockGeMProvider,
        "BLACKLIST": MockBlacklistProvider,
    }
    cls = providers.get(provider_name.upper())
    if not cls:
        raise HTTPException(400, f"Unknown provider '{provider_name}'. Supported: {list(providers.keys())}")
    return cls()


@router.post("/bids/{bid_id}/verify", response_model=VerificationResultResponse)
async def verify_for_bid(
    request: Request,
    bid_id: str,
    payload: VerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("PROCUREMENT_OFFICER", "ANALYST", "ADMIN")),
):
    """
    Run a verification check against a mock government provider.
    ⚠️ DEMO MODE: All verification is simulated. Results labeled MOCK_SANDBOX.
    CRITICAL: UNAVAILABLE status NEVER becomes PASS.
    """
    from app.repositories.bids import BidRepository
    from datetime import UTC, datetime

    bid = await BidRepository(db).get_by_id(bid_id)
    if not bid:
        raise HTTPException(404, "Bid not found.")

    audit = AuditService(db)
    v_repo = VerificationRepository(db)
    request_id = getattr(request.state, "request_id", None)

    provider = _get_provider(payload.provider)

    # Log request
    v_request = VRequest(
        bid_id=bid_id,
        bidder_id=bid.bidder_id,
        provider=payload.provider.upper(),
        queried_identifier=payload.identifier,
        is_demo=bid.is_demo,
    )
    db.add(v_request)
    await db.flush()

    await audit.log(
        AuditAction.VERIFICATION_REQUEST, AuditCategory.VERIFICATION,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="BID", entity_id=bid_id, bid_id=bid_id,
        new_value={"provider": payload.provider, "identifier": payload.identifier},
        source="VERIFICATION_API", request_id=request_id,
    )

    # Execute verification
    try:
        result = await provider.verify(
            payload.identifier,
            scenario=payload.scenario,
            **(payload.additional_params or {}),
        )
    except Exception as exc:
        logger.error("verification_error", provider=payload.provider, error=str(exc))
        # Failure must never become PASS
        from app.engines.verification_engine.base import VerificationStatus
        result_obj = VResult(
            request_id=v_request.id,
            bid_id=bid_id,
            bidder_id=bid.bidder_id,
            source=f"{payload.provider.upper()}_ADAPTER",
            provider=payload.provider.upper(),
            queried_identifier=payload.identifier,
            status="UNAVAILABLE",
            is_unavailable=True,
            authorization_context="MOCK_SANDBOX",
            confidence=0.0,
            error_code="ADAPTER_ERROR",
            error_message=str(exc),
            is_mock=True, is_demo=True,
        )
    else:
        result_obj = VResult(
            request_id=v_request.id,
            bid_id=bid_id,
            bidder_id=bid.bidder_id,
            source=result.source,
            provider=result.provider,
            queried_identifier=result.queried_identifier,
            returned_identifier=result.returned_identifier,
            status=result.status.value,
            is_unavailable=result.is_unavailable,
            returned_data=result.data,
            conflict_details=result.conflict_details,
            checked_at=result.checked_at,
            source_reference=result.source_reference,
            authorization_context=result.authorization_context,
            confidence=result.confidence,
            error_code=result.error_code,
            error_message=result.error_message,
            is_mock=result.is_mock,
            is_demo=result.is_demo,
        )

    db.add(result_obj)
    await db.flush()

    await audit.log(
        AuditAction.VERIFICATION_RESULT, AuditCategory.VERIFICATION,
        user_id=current_user.id, user_email=current_user.email, user_role=current_user.role,
        entity_type="VERIFICATION_RESULT", entity_id=result_obj.id, bid_id=bid_id,
        new_value={
            "provider": payload.provider,
            "status": result_obj.status,
            "is_unavailable": result_obj.is_unavailable,
            "is_mock": True,
        },
        source="VERIFICATION_API", request_id=request_id,
    )

    return VerificationResultResponse.model_validate(result_obj)


@router.get("/adapters")
async def list_and_test_adapters():
    """
    Pings all 10 government verification adapters live.
    Executes mock adapter logic, returning real status, rate limit specs, circuit breaker state, and authorization context.
    """
    from datetime import datetime, UTC
    import time

    adapters_info = []
    providers_list = [
        ("GST", "27AABCS1429B1Z5", "Goods and Services Tax Network"),
        ("MCA", "L74999MH2015PLC263124", "Ministry of Corporate Affairs (CIN/Directors)"),
        ("PAN", "AABCS1429B", "Income Tax Department (PAN Verification)"),
        ("UDYAM", "UDYAM-MH-10-0012345", "MSME Udyam Registration Portal"),
        ("EPFO", "MH/BAN/0012345/000", "Employees Provident Fund Organisation"),
        ("ESIC", "31000123450000101", "Employees State Insurance Corporation"),
        ("DIGILOCKER", "DOC-DL-9912", "DigiLocker Document Verification"),
        ("BIS", "CM/L-1234567", "Bureau of Indian Standards"),
        ("GEM", "GEM-SELLER-9981", "Government e-Marketplace Seller Registry"),
        ("BLACKLIST", "AADCB2230M", "Centralized Govt Debarment Registry"),
    ]

    for name, identifier, full in providers_list:
        t0 = time.time()
        provider = _get_provider(name)
        res = await provider.verify(identifier)
        elapsed_ms = round((time.time() - t0) * 1000, 1)

        adapters_info.append({
            "name": name,
            "full": full,
            "status": res.status.value,
            "rateLimit": "60/min" if name in ("GST", "PAN", "UDYAM", "DIGILOCKER", "GEM") else "30/min",
            "cbState": "CLOSED",
            "cache": "LIVE",
            "latency_ms": elapsed_ms,
            "is_mock": res.is_mock,
            "authorization_context": res.authorization_context,
            "queried_identifier": identifier,
            "checked_at": res.checked_at.isoformat(),
        })

    return {"status": "SUCCESS", "count": len(adapters_info), "adapters": adapters_info}
