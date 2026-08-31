"""
Compliance Explanation Service.

Generates structured, evidence-backed explanations from evaluation data.
Never lets LLMs invent compliance reasons.
"""
from typing import List, Dict, Any

class ComplianceExplainerService:
    @staticmethod
    def build_summary(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(evaluations)
        passed = sum(1 for e in evaluations if e.get("status") == "PASS")
        failed = sum(1 for e in evaluations if e.get("status") == "FAIL")
        insufficient = sum(1 for e in evaluations if e.get("status") == "INSUFFICIENT_EVIDENCE")
        unavailable = sum(1 for e in evaluations if e.get("status") == "VERIFICATION_UNAVAILABLE")
        review = sum(1 for e in evaluations if e.get("status") == "MANUAL_REVIEW_REQUIRED")

        if failed > 0:
            overall = "FAIL"
        elif unavailable > 0 or insufficient > 0 or review > 0:
            overall = "MANUAL_REVIEW_REQUIRED"
        else:
            overall = "PASS"

        table_rows = []
        for e in evaluations:
            table_rows.append({
                "requirement_id": e.get("requirement_id"),
                "requirement_name": e.get("requirement_name"),
                "status": e.get("status"),
                "required_value": str(e.get("required_value")),
                "actual_value": str(e.get("actual_value")),
                "confidence": e.get("confidence", 1.0),
                "evidence_document": e.get("evidence_document_id"),
                "page": e.get("evidence_page_number"),
                "reason": e.get("reason"),
            })

        return {
            "overall_status": overall,
            "total_requirements": total,
            "passed": passed,
            "failed": failed,
            "insufficient_evidence": insufficient,
            "verification_unavailable": unavailable,
            "manual_review": review,
            "requirements_matrix": table_rows,
        }

compliance_explainer = ComplianceExplainerService()
