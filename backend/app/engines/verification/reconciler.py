"""
Verification Reconciler.

Compares:
- Submitted document evidence
- Extracted identifiers
- Government API verification responses

Categorizes into:
- VERIFIED_MATCH
- MISMATCH
- VERIFICATION_UNAVAILABLE
- CONFLICTING_VERIFICATION
"""
import structlog
from typing import Dict, Any, List, Optional

logger = structlog.get_logger(__name__)

class VerificationReconciler:
    def reconcile(
        self,
        extracted_identifier: Optional[str],
        verification_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        v_status = verification_result.get("status")
        provider = verification_result.get("provider", "UNKNOWN")
        returned_id = verification_result.get("returned_identifier")

        if v_status == "UNAVAILABLE":
            return {
                "reconciliation_status": "VERIFICATION_UNAVAILABLE",
                "explanation": f"Government API provider ({provider}) unavailable.",
                "requires_manual_review": True,
            }

        if v_status == "CONFLICT" or v_status == "NOT_FOUND":
            return {
                "reconciliation_status": "MISMATCH",
                "explanation": f"Mismatch between extracted identifier ({extracted_identifier}) and {provider} API response.",
                "requires_manual_review": True,
            }

        if v_status == "VERIFIED":
            if extracted_identifier and returned_id and extracted_identifier.upper() != returned_id.upper():
                return {
                    "reconciliation_status": "CONFLICTING_VERIFICATION",
                    "explanation": f"Returned identifier ({returned_id}) differs from submitted ({extracted_identifier}).",
                    "requires_manual_review": True,
                }
            return {
                "reconciliation_status": "VERIFIED_MATCH",
                "explanation": f"Successfully verified against {provider} API.",
                "requires_manual_review": False,
            }

        return {
            "reconciliation_status": "VERIFICATION_UNAVAILABLE",
            "explanation": f"Unknown status ({v_status}) from provider {provider}.",
            "requires_manual_review": True,
        }

verification_reconciler = VerificationReconciler()
