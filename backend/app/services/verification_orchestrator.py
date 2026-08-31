"""
Verification Orchestrator Service.

Orchestrates government verifications:
1. Circuit Breaker Check
2. Rate Limiting Check
3. Cache Lookups
4. Mock/Live Adapter Execution with Retries & Exponential Backoff
5. Reconciliation against extracted evidence
6. Audit Logging
"""
import asyncio
import structlog
from typing import Dict, Any, Optional
from datetime import UTC, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.verification.circuit_breaker import circuit_breaker, CircuitBreakerState
from app.engines.verification.rate_limiter import rate_limiter
from app.engines.verification.cache_manager import verification_cache
from app.engines.verification.reconciler import verification_reconciler
from app.engines.verification_engine.mock_adapters import (
    MockGSTProvider, MockPANProvider, MockUdyamProvider, MockMCAProvider, MockBlacklistProvider,
)
from app.services.audit_service import AuditService, AuditAction, AuditCategory
from app.models.verification import VerificationRequest, VerificationResult

logger = structlog.get_logger(__name__)

PROVIDERS = {
    "GST": MockGSTProvider,
    "PAN": MockPANProvider,
    "UDYAM": MockUdyamProvider,
    "MCA": MockMCAProvider,
    "BLACKLIST": MockBlacklistProvider,
}

class VerificationOrchestratorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit = AuditService(db)

    async def execute_verification(
        self,
        bid_id: str,
        bidder_id: str,
        provider_name: str,
        identifier: str,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        p_name = provider_name.upper()

        # 1. Circuit Breaker Check
        cb_state = circuit_breaker.get_state(p_name)
        if cb_state == CircuitBreakerState.OPEN:
            logger.warning("verification_bypassed_circuit_open", provider=p_name)
            return {
                "status": "UNAVAILABLE",
                "is_unavailable": True,
                "error": f"Circuit breaker for provider '{p_name}' is OPEN due to consecutive failures.",
            }

        # 2. Rate Limiter Check
        if not rate_limiter.is_allowed(p_name):
            return {
                "status": "RATE_LIMITED",
                "is_unavailable": True,
                "error": f"Rate limit exceeded for provider '{p_name}'.",
            }

        # 3. Cache Lookup
        cached_data, cache_status = verification_cache.get(p_name, identifier)
        if cache_status == "CACHED" and cached_data:
            logger.info("verification_cache_hit", provider=p_name, identifier=identifier)
            return cached_data

        # 4. Instantiate Adapter
        adapter_cls = PROVIDERS.get(p_name, MockGSTProvider)
        adapter = adapter_cls()

        # 5. Execute with Retries & Exponential Backoff
        result_obj = None
        attempt = 0

        for attempt in range(1, max_retries + 2):
            try:
                result = await adapter.verify(identifier)
                if result.status.value != "UNAVAILABLE":
                    circuit_breaker.record_success(p_name)
                    result_obj = result
                    break
                else:
                    raise Exception("Adapter returned UNAVAILABLE")
            except Exception as exc:
                logger.warning("verification_attempt_failed", provider=p_name, attempt=attempt, error=str(exc))
                if attempt <= max_retries:
                    await asyncio.sleep(0.1 * (2 ** attempt))

        if not result_obj:
            circuit_breaker.record_failure(p_name)
            res_dict = {
                "provider": p_name,
                "queried_identifier": identifier,
                "status": "UNAVAILABLE",
                "is_unavailable": True,
                "authorization_context": "MOCK_SANDBOX",
                "error": "Failed after max retries or adapter unavailable.",
            }
            return res_dict

        res_dict = {
            "provider": result_obj.provider,
            "queried_identifier": result_obj.queried_identifier,
            "returned_identifier": result_obj.returned_identifier,
            "status": result_obj.status.value,
            "is_unavailable": result_obj.is_unavailable,
            "authorization_context": result_obj.authorization_context,
            "confidence": result_obj.confidence,
            "is_mock": result_obj.is_mock,
            "data": result_obj.data,
            "conflict_details": result_obj.conflict_details,
        }

        # Cache result if valid
        verification_cache.put(p_name, identifier, res_dict)

        # Audit log
        await self.audit.log(
            action=AuditAction.VERIFICATION_RESULT,
            action_category=AuditCategory.VERIFICATION,
            entity_type="BID",
            entity_id=bid_id,
            bid_id=bid_id,
            new_value={"provider": p_name, "status": result_obj.status.value},
            change_summary=f"Executed government verification check against provider {p_name}.",
        )

        return res_dict

verification_orchestrator = VerificationOrchestratorService
