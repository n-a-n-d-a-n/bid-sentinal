"""
Contradiction Engine.

Aggregates cross-document, cross-source, and verification contradictions:
- Identity Mismatch (PAN / GSTIN / CIN)
- Financial Conflicts
- Blacklist Verification Match
- Address Mismatches
"""
import structlog
from typing import List, Dict, Any

from app.engines.consistency.identifier_checker import identifier_checker
from app.engines.consistency.financial_checker import financial_checker

logger = structlog.get_logger(__name__)

class ContradictionEngineService:
    def evaluate_contradictions(
        self,
        doc_extractions: List[Dict[str, Any]],
        verifications: List[Dict[str, Any]],
        bidder_info: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        all_contradictions: List[Dict[str, Any]] = []

        # 1. Identifier Contradictions
        ident_conflicts = identifier_checker.check_identifier_consistency(doc_extractions, verifications)
        all_contradictions.extend(ident_conflicts)

        # 2. Financial Contradictions
        fin_conflicts = financial_checker.check_financial_consistency(doc_extractions)
        all_contradictions.extend(fin_conflicts)

        # 3. Blacklist Check
        for v in verifications:
            if v.get("provider") == "BLACKLIST" and v.get("status") == "CONFLICT":
                all_contradictions.append({
                    "type": "BLACKLIST_MATCH",
                    "severity": "CRITICAL",
                    "description": f"Bidder matched against government debarment/blacklist registry!",
                    "source_a": "Bidder Identifier",
                    "source_b": "Government Blacklist Registry",
                    "page_a": None,
                    "page_b": None,
                    "values": {"identifier": v.get("queried_identifier")},
                    "confidence": 1.0,
                    "recommended_action": "IMMEDIATE DISQUALIFICATION RECOMMENDED. Refer to legal audit committee.",
                })

        logger.info("contradiction_evaluation_complete", count=len(all_contradictions))
        return all_contradictions

contradiction_engine = ContradictionEngineService()
