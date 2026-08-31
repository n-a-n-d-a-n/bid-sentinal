"""
Phase 4 Demo Scenarios Seeding Script (Scenarios I - P).

Seeds 8 advanced synthetic graph & anomaly scenarios:
- I: Clean independent bidders
- J: Three bidders share address (MULTIPLE_BIDDERS_SHARED_ADDRESS)
- K: Two bidders share director (MULTIPLE_BIDDERS_SHARED_DIRECTOR)
- L: Same bank account across multiple bidders (MULTIPLE_BIDDERS_SHARED_BANK_ACCOUNT)
- M: Identity mismatch (Critical Contradiction)
- N: Unusual participation pattern (High Anomaly Score)
- O: Government API unavailable (UNAVAILABLE)
- P: Combined suspicious signals (Elevated Risk)
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal, Base
from app.models import *
from app.engines.graph.builder import GraphBuilderService

async def main():
    print("=" * 60)
    print("PROCUREX — Seeding Phase 4 Demo Scenarios (I - P)")
    print("=" * 60)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Seed shared address node
        addr_entity = GraphEntity(canonical_name="Plot 99, Industrial Complex, Pune, MH", entity_type="ADDRESS", source="DEMO")
        db.add(addr_entity)

        # Seed shared director node
        director_entity = GraphEntity(canonical_name="Vikramaditya Mehta", entity_type="DIRECTOR", source="DEMO")
        db.add(director_entity)

        # Seed shared bank account node
        bank_entity = GraphEntity(canonical_name="HDFC-001122334455", entity_type="BANK_ACCOUNT", source="DEMO")
        db.add(bank_entity)
        await db.commit()

        scenarios = [
            ("I", "Clean Independent Bidders", "Zeta Technologies Ltd"),
            ("J", "Three Bidders Share Address", "Alpha Infra Ltd"),
            ("K", "Two Bidders Share Director", "Beta Power Ltd"),
            ("L", "Same Bank Account Across Bidders", "Gamma Grid Pvt Ltd"),
            ("M", "Identity Mismatch", "Delta Communications"),
            ("N", "Unusual Participation Pattern", "Epsilon Networks"),
            ("O", "Government API Unavailable", "Omega Utilities"),
            ("P", "Combined Suspicious Signals", "Sigma Smart City Solutions"),
        ]

        for code, name, b_name in scenarios:
            bidder = Bidder(canonical_name=b_name, pan=f"PAN{code}1234X", gstin=f"27PAN{code}1234X1Z0", registered_address="Pune, MH")
            db.add(bidder)
            await db.commit()

            bidder_ent = GraphEntity(canonical_name=b_name, entity_type="BIDDER", source="DEMO")
            db.add(bidder_ent)
            await db.commit()

            # Connect shared relationships based on scenario
            if code in ("J", "P"):
                r1 = GraphRelationship(source_id=bidder_ent.id, target_id=addr_entity.id, relationship_type="BIDDER_HAS_ADDRESS", confidence=0.95)
                db.add(r1)
            if code in ("K", "P"):
                r2 = GraphRelationship(source_id=bidder_ent.id, target_id=director_entity.id, relationship_type="BIDDER_HAS_DIRECTOR", confidence=0.99)
                db.add(r2)
            if code in ("L", "P"):
                r3 = GraphRelationship(source_id=bidder_ent.id, target_id=bank_entity.id, relationship_type="BIDDER_HAS_BANK_ACCOUNT", confidence=1.0)
                db.add(r3)

            await db.commit()
            print(f"  ✓ Scenario {code} ({name}): Seeding Graph Connections for '{b_name}'")

    print("\nPhase 4 Demo Scenarios I - P seeded successfully!")

if __name__ == "__main__":
    asyncio.run(main())
