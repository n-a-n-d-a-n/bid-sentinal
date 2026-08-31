"""
Cross-Document Financial Consistency Checker.
"""
from typing import List, Dict, Any

class FinancialChecker:
    @staticmethod
    def check_financial_consistency(doc_extractions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        contradictions = []
        turnovers = []

        for d in doc_extractions:
            if d.get("field_name") == "annual_turnover_inr" and d.get("field_value"):
                try:
                    val = float(d["field_value"])
                    turnovers.append((val, d.get("document_id"), d.get("page_number")))
                except Exception:
                    pass

        if len(turnovers) >= 2:
            val1, doc1, page1 = turnovers[0]
            val2, doc2, page2 = turnovers[1]

            # Material discrepancy check (> 15% variance for same metric)
            if abs(val1 - val2) / max(val1, val2) > 0.15:
                contradictions.append({
                    "type": "FINANCIAL_CONFLICT",
                    "severity": "HIGH",
                    "description": f"Material turnover conflict detected across documents: INR {val1:,.0f} vs INR {val2:,.0f}",
                    "source_a": f"Document {doc1}",
                    "source_b": f"Document {doc2}",
                    "page_a": page1,
                    "page_b": page2,
                    "values": {"turnover_a": val1, "turnover_b": val2},
                    "confidence": 0.95,
                    "recommended_action": "Request audited balance sheet certified by Chartered Accountant.",
                })

        return contradictions

financial_checker = FinancialChecker()
