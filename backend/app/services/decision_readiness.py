"""
Decision Readiness Service.

Determines whether a bid is ready for Procurement Officer review:
- READY_FOR_REVIEW: All mandatory requirements pass + verifications available + no unresolved critical contradictions.
- MANUAL_REVIEW_REQUIRED: Minor variations, ambiguous extractions, or fuzzy matches.
- BLOCKED: Critical identity mismatch or Blacklist registry match.
- INCOMPLETE: Missing mandatory document or insufficient evidence.
"""
from typing import Dict, Any, List

class DecisionReadinessService:
    @staticmethod
    def calculate_readiness(
        compliance_summary: Dict[str, Any],
        contradictions: List[Dict[str, Any]],
        verification_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        
        # 1. Critical Contradictions check -> BLOCKED
        critical_conflicts = [c for c in contradictions if c.get("severity") in ("CRITICAL", "HIGH")]
        if critical_conflicts:
            return {
                "readiness_status": "BLOCKED",
                "reason": f"Critical contradictions detected: {critical_conflicts[0]['description']}",
                "blocking_factors": [c['description'] for c in critical_conflicts],
                "recommended_action": "Refer to legal/audit committee. Do not approve.",
            }

        # 2. Insufficient / Missing Document -> INCOMPLETE
        if compliance_summary.get("insufficient_evidence", 0) > 0:
            return {
                "readiness_status": "INCOMPLETE",
                "reason": "Missing mandatory document or unextracted required fields.",
                "blocking_factors": ["Insufficient document evidence"],
                "recommended_action": "Request bidder to upload missing mandatory certificates.",
            }

        # 3. Verification Unavailable or Manual Review -> MANUAL_REVIEW_REQUIRED
        if (
            compliance_summary.get("verification_unavailable", 0) > 0
            or compliance_summary.get("manual_review", 0) > 0
            or any(v.get("status") == "UNAVAILABLE" for v in verification_results)
        ):
            return {
                "readiness_status": "MANUAL_REVIEW_REQUIRED",
                "reason": "Government API verification unavailable or extraction confidence requires manual review.",
                "blocking_factors": ["External verification unavailable / low confidence"],
                "recommended_action": "Officer manual review required before final qualification decision.",
            }

        # 4. Failed Requirements -> MANUAL_REVIEW_REQUIRED
        if compliance_summary.get("failed", 0) > 0:
            return {
                "readiness_status": "MANUAL_REVIEW_REQUIRED",
                "reason": "One or more mandatory compliance rules failed.",
                "blocking_factors": ["Compliance rule failure"],
                "recommended_action": "Review failed rules and evaluate potential disqualification.",
            }

        # 5. Clean -> READY_FOR_REVIEW
        return {
            "readiness_status": "READY_FOR_REVIEW",
            "reason": "All mandatory requirements satisfied and verifications completed cleanly.",
            "blocking_factors": [],
            "recommended_action": "Bid is ready for officer qualification decision.",
        }

decision_readiness = DecisionReadinessService()
