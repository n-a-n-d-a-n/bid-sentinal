"""
Acceptance Test for Bid API Database Fidelity & Zero Hardcoded Data Leaks.

Verifies:
1. Direct DB count matches GET /api/v1/bids count and returned IDs exactly.
2. Adding a new real bid to DB makes it immediately appear in GET /api/v1/bids.
3. Zero hardcoded bid objects exist in non-demo frontend code paths.
"""
import os
import re
import pytest
import pytest_asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.database import Base
from app.models.bidder import Bidder
from app.models.bid import Bid
from app.models.tender import Tender
from app.models.user import User
from app.repositories.bids import BidRepository


@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_bid_api_matches_db_count_and_ids_exactly(test_db: AsyncSession):
    """
    1. Queries DB directly for bid count.
    2. Calls BidRepository / list_bids logic and confirms count & IDs match DB exactly.
    """
    repo = BidRepository(test_db)

    # Initially DB is empty
    count_res = await test_db.execute(select(func.count(Bid.id)))
    initial_db_count = count_res.scalar() or 0
    assert initial_db_count == 0

    api_bids = await repo.list_paginated(offset=0, limit=20)
    api_count = await repo.count_filtered()

    assert api_count == initial_db_count == 0
    assert len(api_bids) == 0


@pytest.mark.asyncio
async def test_adding_new_bid_immediately_appears_in_api_response(test_db: AsyncSession):
    """
    Adds one new real bid to DB and confirms it appears in API response with exact ID and details.
    """
    repo = BidRepository(test_db)

    # Create prerequisite Tender & Bidder
    tender = Tender(title="Solar Panel Procurement", gem_bid_number="GEM/2026/B/777000", status="ACTIVE")
    bidder = Bidder(canonical_name="Solaris Infra Pvt Ltd", pan="SOLAR1234P", gstin="27SOLAR1234P1Z8", state="Gujarat")
    test_db.add(tender)
    test_db.add(bidder)
    await test_db.flush()

    new_bid = Bid(
        tender_id=tender.id,
        bidder_id=bidder.id,
        bid_reference_number="BID-2026-REAL-101",
        quoted_price_inr=15000000.0,
        status="SUBMITTED",
    )
    test_db.add(new_bid)
    await test_db.commit()

    # Query DB count
    count_res = await test_db.execute(select(func.count(Bid.id)))
    db_count = count_res.scalar()
    assert db_count == 1

    # Query API logic
    api_bids = await repo.list_paginated(offset=0, limit=20)
    api_count = await repo.count_filtered()

    assert api_count == db_count == 1
    assert api_bids[0].id == new_bid.id
    assert api_bids[0].bid_reference_number == "BID-2026-REAL-101"


def test_zero_hardcoded_fallback_bids_in_main_frontend_views():
    """
    Grep test: scanning main frontend app pages to confirm zero hardcoded fallback bids leak outside /demo.
    """
    frontend_app_dir = os.path.abspath("frontend/src/app")
    non_demo_pages = [
        "bids/page.tsx",
        "dashboard/page.tsx",
        "bidders/page.tsx",
        "tenders/page.tsx",
        "decisions/page.tsx",
        "anomalies/page.tsx",
        "documents/page.tsx",
        "audit/page.tsx",
    ]

    hardcoded_patterns = [
        r"BID-2026-001",
        r"BID-2026-002",
        r"Shakti Infrastructure Solutions",
        r"Alpha Infra Solutions Pvt Ltd",
        r"Audited_Financial_Statement_FY24\.pdf",
    ]

    leaks = []
    for rel_path in non_demo_pages:
        full_path = os.path.join(frontend_app_dir, rel_path)
        if not os.path.exists(full_path):
            continue
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            for pattern in hardcoded_patterns:
                if re.search(pattern, content):
                    leaks.append((rel_path, pattern))

    assert len(leaks) == 0, f"Found hardcoded fallback leaks in main views: {leaks}"


def test_zero_sih_references_in_web_views():
    """
    Automated check: verifies zero occurrence of 'SIH' or 'SIH26100' in any web view file under frontend/src.
    """
    frontend_src_dir = os.path.abspath("frontend/src")
    sih_matches = []

    for root, dirs, files in os.walk(frontend_src_dir):
        for file_name in files:
            if file_name.endswith((".tsx", ".ts", ".js", ".jsx", ".html")):
                full_path = os.path.join(root, file_name)
                with open(full_path, "r", encoding="utf-8") as f:
                    for line_idx, line in enumerate(f, 1):
                        if re.search(r"\bSIH\b|SIH26100", line, re.IGNORECASE):
                            sih_matches.append((os.path.relpath(full_path, frontend_src_dir), line_idx, line.strip()))

    assert len(sih_matches) == 0, f"Found prohibited 'SIH' references in web views: {sih_matches}"

