"""
Demo Scenario Registry.

Registers all 23 synthetic demonstration scenarios (A - W).
"""
from typing import Dict, List, Optional
from app.demo.schemas import DemoScenarioSchema

SCENARIOS: Dict[str, DemoScenarioSchema] = {
    "A": DemoScenarioSchema(code="A", name="Clean Procurement", description="Normal compliant procurement with clean bidder documents.", category="CLEAN_PROCUREMENT", expected_outcome="APPROVED", tags=["CLEAN", "PASS"], display_order=1),
    "B": DemoScenarioSchema(code="B", name="Missing Document", description="Bid missing required financial statements.", category="DOCUMENT_INTELLIGENCE", expected_outcome="CLARIFICATION_REQUIRED", tags=["MISSING_DOC", "INCOMPLETE"], display_order=2),
    "C": DemoScenarioSchema(code="C", name="Turnover Requirement Failure", description="Bidder turnover below required threshold.", category="COMPLIANCE", expected_outcome="REJECTED", tags=["FAIL", "COMPLIANCE"], display_order=3),
    "D": DemoScenarioSchema(code="D", name="Verification Mismatch", description="Extracted GSTIN differs from government record.", category="VERIFICATION", expected_outcome="MANUAL_REVIEW_REQUIRED", tags=["MISMATCH"], display_order=4),
    "E": DemoScenarioSchema(code="E", name="Government API Unavailable", description="GST API returns UNAVAILABLE (Never becomes PASS).", category="VERIFICATION", expected_outcome="UNAVAILABLE", tags=["UNAVAILABLE"], display_order=5),
    "F": DemoScenarioSchema(code="F", name="Cross-Document Financial Conflict", description="Turnover variance >15% across documents.", category="FINANCIAL_CONSISTENCY", expected_outcome="MANUAL_REVIEW_REQUIRED", tags=["CONTRADICTION"], display_order=6),
    "G": DemoScenarioSchema(code="G", name="Fuzzy Corporate Identity Match", description="Possible entity match requiring officer review.", category="IDENTITY", expected_outcome="MANUAL_REVIEW_REQUIRED", tags=["FUZZY_MATCH"], display_order=7),
    "H": DemoScenarioSchema(code="H", name="Scanned PDF OCR Fallback", description="Scanned PDF text extracted via Tesseract OCR.", category="DOCUMENT_INTELLIGENCE", expected_outcome="READY_FOR_REVIEW", tags=["OCR"], display_order=8),
    "I": DemoScenarioSchema(code="I", name="Independent Bidders Network", description="Clean independent bidders with low network density.", category="NETWORK_INTELLIGENCE", expected_outcome="READY_FOR_REVIEW", tags=["GRAPH"], display_order=9),
    "J": DemoScenarioSchema(code="J", name="Multiple Bidders Shared Address", description="Three bidders share registered address.", category="NETWORK_INTELLIGENCE", expected_outcome="MANUAL_REVIEW_REQUIRED", tags=["SHARED_ADDRESS"], display_order=10),
    "K": DemoScenarioSchema(code="K", name="Two Bidders Share Director", description="Potential shared-control relationship.", category="NETWORK_INTELLIGENCE", expected_outcome="MANUAL_REVIEW_REQUIRED", tags=["SHARED_DIRECTOR"], display_order=11),
    "L": DemoScenarioSchema(code="L", name="Same Bank Account Across Bidders", description="Multiple bidders share bank account.", category="NETWORK_INTELLIGENCE", expected_outcome="MANUAL_REVIEW_REQUIRED", tags=["SHARED_BANK"], display_order=12),
    "M": DemoScenarioSchema(code="M", name="Identity Mismatch", description="High severity identity mismatch contradiction.", category="IDENTITY", expected_outcome="BLOCKED", tags=["IDENTITY_MISMATCH"], display_order=13),
    "N": DemoScenarioSchema(code="N", name="Unusual Participation Pattern", description="High anomaly score advisory alert.", category="ANOMALY_DETECTION", expected_outcome="MANUAL_REVIEW_REQUIRED", tags=["ANOMALY"], display_order=14),
    "O": DemoScenarioSchema(code="O", name="Government Provider Unavailable", description="API timeout handled safely.", category="VERIFICATION", expected_outcome="UNAVAILABLE", tags=["UNAVAILABLE"], display_order=15),
    "P": DemoScenarioSchema(code="P", name="Combined Suspicious Signals", description="Graph signals + verification mismatch + high risk.", category="NETWORK_INTELLIGENCE", expected_outcome="MANUAL_REVIEW_REQUIRED", tags=["COMBINED_SIGNALS"], display_order=16),
    "Q": DemoScenarioSchema(code="Q", name="Clean Officer Approval", description="Compliant bid approved by officer.", category="OFFICER_DECISION", expected_outcome="APPROVED", tags=["WORKFLOW"], display_order=17),
    "R": DemoScenarioSchema(code="R", name="Non-Compliant Officer Rejection", description="Officer rejects non-compliant bid with mandatory justification.", category="OFFICER_DECISION", expected_outcome="REJECTED", tags=["REJECT"], display_order=18),
    "S": DemoScenarioSchema(code="S", name="Officer Override After Investigation", description="Officer approves bid recommended for MANUAL_REVIEW after evidence review.", category="OFFICER_DECISION", expected_outcome="APPROVED", tags=["OVERRIDE", "WOW_DEMO"], display_order=19),
    "T": DemoScenarioSchema(code="T", name="Critical Contradiction Escalation", description="Officer escalates bid with identity mismatch.", category="OFFICER_DECISION", expected_outcome="ESCALATED", tags=["ESCALATE"], display_order=20),
    "U": DemoScenarioSchema(code="U", name="Clarification Request Loop", description="Officer requests clarification -> reanalysis -> review.", category="OFFICER_DECISION", expected_outcome="UNDER_REVIEW", tags=["CLARIFICATION"], display_order=21),
    "V": DemoScenarioSchema(code="V", name="Stale Decision Context", description="Verification changes after review freeze.", category="DECISION_GOVERNANCE", expected_outcome="STALE", tags=["STALE_CONTEXT"], display_order=22),
    "W": DemoScenarioSchema(code="W", name="Audit Ledger Tamper Verification", description="Demonstrates audit chain tamper detection.", category="AUDIT_INTEGRITY", expected_outcome="INVALID", tags=["TAMPER_DEMO"], display_order=23),
}

class DemoScenarioRegistry:
    @staticmethod
    def list_scenarios() -> List[DemoScenarioSchema]:
        return sorted(list(SCENARIOS.values()), key=lambda x: x.display_order)

    @staticmethod
    def get_scenario(code: str) -> Optional[DemoScenarioSchema]:
        return SCENARIOS.get(code.upper())

demo_registry = DemoScenarioRegistry()
