"""
Seed Demo Pipeline Script.

Seeds:
1. Demo User Accounts (Admin, Officer, Analyst, Auditor)
2. Synthetic Tender ("Municipal Smart Infrastructure Procurement — Demo")
3. Synthetic Tender Requirements (Financial turnover >= 10 Crore, PAN/GSTIN mandatory)
4. Synthetic Bidder ("Shakti Infrastructure Solutions Pvt Ltd")
5. Synthetic Bid with Document Upload & Processing Pipeline execution
6. Runs Compliance Engine & Risk Engine
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal, Base
from app.core.security import hash_password
from app.models import *
from app.services.pipeline_orchestrator import PipelineOrchestratorService
from app.engines.compliance_engine.engine import ComplianceEngine
from app.engines.risk_engine.engine import RiskEngine

async def main():
    print("=" * 60)
    print("PROCUREX — Seeding Demo Pipeline Scenario")
    print("=" * 60)

    # 1. Initialize Tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 2. Officer User
        officer = User(
            email="officer_demo@procurex.local",
            username="officer_demo",
            full_name="Rajesh Kumar (Procurement Officer)",
            hashed_password=hash_password("Officer@123!"),
            role="PROCUREMENT_OFFICER",
            department="Smart City Cell",
            is_active=True,
            is_verified=True,
        )
        db.add(officer)
        await db.commit()
        await db.refresh(officer)

        # 3. Tender
        tender = Tender(
            gem_bid_number="GEM/2026/B/8899100",
            title="Municipal Smart Infrastructure Procurement — Demo",
            description="Procurement and deployment of IoT sensors and smart grid controllers.",
            department="Municipal Corporation",
            estimated_value_inr=50000000.0,
            status="ACTIVE",
            created_by=officer.id,
        )
        db.add(tender)
        await db.commit()
        await db.refresh(tender)

        # 4. Tender Requirement
        req1 = TenderRequirement(
            tender_id=tender.id,
            requirement_id="TURN_001",
            category="FINANCIAL",
            description="Minimum Annual Turnover of 10 Crore INR",
            mandatory=True,
            rule_definition={
                "rule_id": "TURN_001",
                "name": "Minimum Annual Turnover 10 Cr",
                "category": "FINANCIAL",
                "mandatory": True,
                "rule_type": "threshold",
                "field": "annual_turnover_inr",
                "operator": ">=",
                "threshold": 100000000.0,
            },
            is_approved=True,
            approved_by=officer.id,
        )
        db.add(req1)
        await db.commit()

        # 5. Bidder
        bidder = Bidder(
            canonical_name="Shakti Infrastructure Solutions Pvt Ltd",
            pan="AADCB2230M",
            gstin="27AADCB2230M1ZP",
            cin="U72900MH2020PTC345678",
            udyam_number="UDYAM-MH-01-0000001",
            entity_type="COMPANY",
            registered_address="Plot 42, MIDC Industrial Area, Mumbai, Maharashtra 400093",
            phone="+919876543210",
            email="contact@shaktiinfra.local",
        )
        db.add(bidder)
        await db.commit()
        await db.refresh(bidder)

        # Add Identifiers
        ident_pan = BidderIdentifier(bidder_id=bidder.id, identifier_type="PAN", identifier_value="AADCB2230M", is_primary=True)
        ident_gst = BidderIdentifier(bidder_id=bidder.id, identifier_type="GSTIN", identifier_value="27AADCB2230M1ZP", is_primary=True)
        db.add(ident_pan)
        db.add(ident_gst)
        await db.commit()

        # 6. Bid
        bid = Bid(
            tender_id=tender.id,
            bidder_id=bidder.id,
            bid_reference_number="BID-SHAKTI-2026-001",
            quoted_price_inr=48000000.0,
            status="PROCESSING",
            is_demo=True,
            demo_scenario="A_CLEAN_BIDDER",
        )
        db.add(bid)
        await db.commit()
        await db.refresh(bid)

        # 7. Document
        doc = Document(
            entity_type="bid",
            entity_id=bid.id,
            filename="bidder_credentials.pdf",
            original_filename="bidder_credentials.pdf",
            content_type="application/pdf",
            size_bytes=1024,
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            storage_path=f"documents/{bid.id}/original/bidder_credentials.pdf",
            storage_bucket="procurex-documents",
            document_type="OTHER",
            uploaded_by=officer.id,
            is_demo=True,
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        # 8. Run Pipeline Orchestration
        orchestrator = PipelineOrchestratorService(db)
        await orchestrator.process_document(doc.id)

        # 9. Run Compliance & Risk evaluation
        c_engine = ComplianceEngine()
        comp_res = c_engine.evaluate_all_rules(
            [req1.rule_definition],
            {"annual_turnover_inr": 150000000.0}
        )
        bid.compliance_result = comp_res["overall_result"]
        bid.compliance_summary = comp_res

        r_engine = RiskEngine()
        risk_res = r_engine.compute_risk(
            compliance_data=comp_res,
            document_data={"low_ocr_confidence_count": 0},
            verification_data={"conflict_count": 0},
            graph_data={},
            behaviour_data={},
        )

        bid.overall_risk_score = risk_res.overall_risk_score
        bid.risk_level = risk_res.risk_level
        bid.status = "RISK_CALCULATED"
        await db.commit()

        print("\n✓ Demo scenario seeded successfully!")
        print(f"  Tender ID:  {tender.id}")
        print(f"  Bidder ID:  {bidder.id}")
        print(f"  Bid ID:     {bid.id}")
        print(f"  Risk Level: {bid.risk_level} (Score: {bid.overall_risk_score})")
        print(f"  Compliance: {bid.compliance_result}")

if __name__ == "__main__":
    asyncio.run(main())
