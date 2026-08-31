"""
Cross-Document Identifier Checker.
"""
from typing import List, Dict, Any, Optional

class IdentifierChecker:
    @staticmethod
    def check_identifier_consistency(
        doc_extractions: List[Dict[str, Any]],
        verifications: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        contradictions = []

        # Check PAN across documents
        pans = set()
        for d in doc_extractions:
            if d.get("field_name") == "pan" and d.get("field_value"):
                pans.add((d["field_value"].strip().upper(), d.get("document_id"), d.get("page_number")))

        if len(pans) > 1:
            pan_list = list(pans)
            contradictions.append({
                "type": "IDENTITY_MISMATCH",
                "severity": "HIGH",
                "description": f"Conflicting PAN numbers detected across documents: {[p[0] for p in pan_list]}",
                "source_a": f"Document {pan_list[0][1]}",
                "source_b": f"Document {pan_list[1][1]}",
                "page_a": pan_list[0][2],
                "page_b": pan_list[1][2],
                "values": {"pan_a": pan_list[0][0], "pan_b": pan_list[1][0]},
                "confidence": 0.98,
                "recommended_action": "Manually verify bidder PAN card and tax registration certificates.",
            })

        # Check Government Verification Mismatches
        for v in verifications:
            if v.get("status") == "CONFLICT":
                contradictions.append({
                    "type": "GOVERNMENT_VERIFICATION_CONFLICT",
                    "severity": "HIGH",
                    "description": f"Government API ({v.get('provider')}) status conflict: {v.get('conflict_details')}",
                    "source_a": "Submitted Document",
                    "source_b": f"Government API ({v.get('provider')})",
                    "page_a": 1,
                    "page_b": None,
                    "values": {"queried": v.get("queried_identifier"), "status": v.get("status")},
                    "confidence": 1.0,
                    "recommended_action": "Do not auto-approve. Require official clarification from issuing authority.",
                })

        return contradictions

identifier_checker = IdentifierChecker()
