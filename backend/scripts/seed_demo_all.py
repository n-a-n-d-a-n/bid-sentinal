"""
Master Demo Seeding Script.

Orchestrates seeding for all 23 synthetic demonstration scenarios (A - W):
1. Phase 3 Scenarios (A - H)
2. Phase 4 Scenarios (I - P)
3. Phase 5 Policy Corpus (GFR 2017 & GeM Manual)
4. Phase 6 Decision Workflow Scenarios (Q - W)
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_demo_scenarios import main as seed_phase3
from seed_demo_scenarios_phase4 import main as seed_phase4
from seed_policy_corpus import main as seed_phase5
from seed_decision_workflow_demo import main as seed_phase6

async def main():
    print("=" * 60)
    print("PROCUREX — Master Demo Seeding (Scenarios A - W)")
    print("=" * 60)

    print("\n1. Seeding Phase 3 Scenarios (A - H)...")
    await seed_phase3()

    print("\n2. Seeding Phase 4 Scenarios (I - P)...")
    await seed_phase4()

    print("\n3. Seeding Phase 5 Policy Corpus (GFR 2017 & GeM Manual)...")
    await seed_phase5()

    print("\n4. Seeding Phase 6 Decision Workflow Scenarios (Q - W)...")
    await seed_phase6()

    print("\n" + "=" * 60)
    print("✓ All 23 Demonstration Scenarios (A - W) Seeded Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
