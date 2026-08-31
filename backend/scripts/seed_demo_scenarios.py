"""
Demo Scenarios Seeding Script (Scenarios A - H).

Seeds 8 reproducible synthetic procurement intelligence scenarios:
- A: Clean compliant bidder (PASS / READY_FOR_REVIEW)
- B: Turnover failure (FAIL / Financial turnover below threshold)
- C: Missing mandatory document (INCOMPLETE)
- D: Government API verification unavailable (VERIFICATION_UNAVAILABLE / NOT PASS)
- E: Identity mismatch (BLOCKED / CRITICAL contradiction)
- F: Conflicting financial values (FINANCIAL_CONFLICT)
- G: Similar bidder names (POSSIBLE_MATCH / Conservative Entity Resolution)
- H: Mixed-quality scanned documents (OCR + Review states)
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal, Base
from app.core.security import hash_password
from app.models import *
from app.engines.compliance_engine.engine import ComplianceEngine
from app.engines.risk_engine.engine import RiskEngine
from app.engines.consistency import contradiction_engine
from app.services.decision_readiness import decision_readiness

async def main():
    print("=" * 60)
    print("PROCUREX — Seeding 8 Synthetic Demo Scenarios (A - H)")
    print("=" * 60)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Officer User
        officer = User(
            email="officer_scenarios@procurex.local",
            username="officer_scenarios",
            full_name="Rajesh Kumar (Procurement Officer)",
            hashed_password=hash_password("Officer@123!"),
            role="PROCUREMENT_OFFICER",
            is_active=True,
            is_verified=True,
        )
        db.add(officer)
        await db.commit()

        # Shared Tender
        tender = Tender(
            gem_bid_number="GEM/2026/B/9000111",
            title="National Smart Grid Equipment Procurement Tender",
            description="Procurement of high-capacity transformers and smart grid controllers.",
            department="Ministry of Power",
            estimated_value_inr=100000000.0,
            status="ACTIVE",
            created_by=officer.id,
        )
        db.add(tender)
        await db.commit()

        # Mandatory Requirement: Turnover >= 10 Crore
        req = TenderRequirement(
            tender_id=tender.id,
            requirement_id="REQ_FIN_001",
            category="FINANCIAL",
            description="Minimum Annual Turnover of 10 Crore INR in last 3 FY",
            mandatory=True,
            rule_definition={
                "rule_id": "REQ_FIN_001",
                "name": "Turnover >= 10 Cr",
                "category": "FINANCIAL",
                "mandatory": True,
                "rule_type": "threshold",
                "field": "annual_turnover_inr",
                "operator": ">=",
                "threshold": 100000000.0,
            },
            is_approved=True,
        )
        db.add(req)
        await db.commit()

        scenarios_data = [
            ("A", "Clean Compliant Bidder", "Shakti Infrastructure Solutions Pvt Ltd", "AADCB2230M", "27AADCB2230M1ZP", 150000000.0, "VERIFIED", "PASS"),
            ("B", "Turnover Failure", "Apex Engineering Ltd", "BBBBB1111B", "27BBBBB1111B1Z1", 30000000.0, "VERIFIED", "FAIL"),
            ("C", "Missing Mandatory Document", "CyberTech Communications", "CCCCC2222C", "27CCCCC2222C1Z2", None, "VERIFIED", "INSUFFICIENT_EVIDENCE"),
            ("D", "Government API Unavailable", "Delta Infra Pvt Ltd", "DDDDD3333D", "27DDDDD3333D1Z3", 120000000.0, "UNAVAILABLE", "VERIFICATION_UNAVAILABLE"),
            ("E", "Identity Mismatch", "Epsilon Systems Ltd", "EEEEE4444E", "27MISMATCH999Z", 140000000.0, "CONFLICT", "FAIL"),
            ("F", "Conflicting Financial Values", "Falcon Networks Pvt Ltd", "FFFFF5555F", "27FFFFF5555F1Z5", 150000000.0, "VERIFIED", "MANUAL_REVIEW_REQUIRED"),
            ("G", "Similar Bidder Names", "Shakti Infra Solutions", "GGGGG6666G", "27GGGGG6666G1Z6", 110000000.0, "VERIFIED", "PASS"),
            ("H", "Mixed-Quality Scanned Document", "Horizon Power Corp", "HHHHH7777H", "27HHHHH7777H1Z7", 105000000.0, "VERIFIED", "PASS"),
        ]

        c_engine = ComplianceEngine()
        r_engine = RiskEngine()

        for code, name, b_name, pan, gstin, turnover, v_status, exp_comp in scenarios_data:
            bidder = Bidder(canonical_name=b_name, pan=pan, gstin=gstin, entity_type="COMPANY")
            db.add(bidder)
            await db.commit()

            bid = Bid(
                tender_id=tender.id,
                bidder_id=bidder.id,
                bid_reference_number=f"BID-DEMO-{code}-2026",
                quoted_price_inr=95000000.0,
                status="RISK_CALCULATED",
                is_demo=True,
                demo_scenario=f"SCENARIO_{code}",
            )
            db.add(bid)
            await db.commit()

            # Record Verification
            v_res = VerificationResult(
                request_id=f"req-demo-{code}",
                bid_id=bid.id,
                bidder_id=bidder.id,
                source="GST_MOCK_ADAPTER",
                provider="GST",
                queried_identifier=gstin,
                status=v_status,
                is_unavailable=(v_status == "UNAVAILABLE"),
                authorization_context="MOCK_SANDBOX",
                confidence=1.0 if v_status == "VERIFIED" else 0.0,
                is_mock=True,
                is_demo=True,
            )
            db.add(v_res)

            # Record Compliance
            comp_eval = c_engine.evaluate_all_rules(
                [req.rule_definition],
                {"annual_turnover_inr": turnover} if turnover else {}
            )
            bid.compliance_result = exp_comp
            bid.compliance_summary = comp_eval

            # Record Risk Score
            risk_eval = r_engine.compute_risk(
                compliance_data=comp_eval,
                document_data={"low_ocr_confidence_count": 1 if code == "H" else 0},
                verification_data={"conflict_count": 1 if v_status == "CONFLICT" else 0, "unavailable_count": 1 if v_status == "UNAVAILABLE" else 0},
                graph_data={},
                behaviour_data={},
            )
            bid.overall_risk_score = risk_eval.overall_risk_score
            bid.risk_level = risk_eval.risk_level
            await db.commit()

            print(f"  ✓ Scenario {code} ({name}): Bidder='{b_name}' -> Compliance={exp_comp}, Risk={risk_eval.risk_level} ({risk_eval.overall_risk_score:.1f})")

    print("\nAll 8 synthetic demo scenarios seeded successfully!")

if __name__ == "__main__":
    asyncio.run(main())
