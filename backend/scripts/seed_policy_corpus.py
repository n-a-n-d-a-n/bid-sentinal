"""
Seed Policy Corpus Script.

Ingests GFR 2017 & GeM Procurement Manual into database with semantic chunking & vector embeddings.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal, Base
from app.engines.policy.ingestion import PolicyIngestionPipeline

GFR_2017_TEXT = """
General Financial Rules (GFR) 2017 - Chapter 6: Procurement of Goods and Services
Rule 144: General Principles Relating to Goods Procurement
Every authority delegated with the financial powers of procuring goods in public interest shall be responsible for ensuring efficiency, economy, and transparency.
Rule 149: Government e-Marketplace (GeM)
Procurement of Goods and Services by Ministries or Departments will be mandatory for Goods or Services available on GeM. The credentials of suppliers on GeM shall be verified by GeM portal.
Rule 151: Debarment from Bidding
A bidder shall be debarred if he has been convicted of an offence under the Prevention of Corruption Act, 1988 or the Indian Penal Code, or if found guilty of serious breach of contract.
Rule 170: Earnest Money Deposit (EMD)
To safeguard against a bidder's withdrawing or altering its bid during the bid validity period, Bid Security (EMD) is to be obtained from all bidders except Micro and Small Enterprises (MSEs) and Startups.
"""

GEM_MANUAL_TEXT = """
GeM General Terms & Conditions (GTC) & Procurement Manual
Section 4: Technical & Financial Qualification Requirements
4.1 Annual Turnover Requirements: Buyers may specify minimum average annual turnover requirements for the last 3 financial years.
4.2 Verification of Documents: Submitted GSTIN, PAN, and Udyam registrations shall be verified against government databases.
4.3 Blacklisted / Debarred Entities: Bidders appearing on the centralized government debarment list shall be automatically disqualified.
"""

async def main():
    print("=" * 60)
    print("PROCUREX — Seeding Policy Corpus (GFR 2017 & GeM Manual)")
    print("=" * 60)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        pipeline = PolicyIngestionPipeline(db)

        # 1. Ingest GFR 2017
        gfr_ver = await pipeline.ingest_policy_document(
            source_code="GFR",
            document_name="General Financial Rules 2017",
            authority="Ministry of Finance, Govt of India",
            version="2017",
            text_content=GFR_2017_TEXT,
            document_type="RULE",
            official_url="https://doe.gov.in/gfr-2017",
        )
        print(f"  ✓ Ingested GFR 2017 (Chunks: {gfr_ver.chunk_count})")

        # 2. Ingest GeM Manual
        gem_ver = await pipeline.ingest_policy_document(
            source_code="GEM_MANUAL",
            document_name="GeM Procurement & Technical Qualification Manual",
            authority="Government e-Marketplace (GeM)",
            version="v4.0",
            text_content=GEM_MANUAL_TEXT,
            document_type="MANUAL",
            official_url="https://gem.gov.in/gtc",
        )
        print(f"  ✓ Ingested GeM Manual v4.0 (Chunks: {gem_ver.chunk_count})")

    print("\nPolicy Corpus seeded successfully!")

if __name__ == "__main__":
    asyncio.run(main())
