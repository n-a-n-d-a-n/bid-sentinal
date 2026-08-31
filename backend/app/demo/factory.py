"""
Demo Data Factory.

Seeds realistic synthetic DB records for scenarios A through W using existing engines.
"""
import uuid
import structlog
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tender import Tender, TenderRequirement
from app.models.bidder import Bidder
from app.models.bid import Bid
from app.models.document import Document
from app.models.verification import VerificationResult

logger = structlog.get_logger(__name__)

class DemoDataFactory:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_scenario_entities(self, scenario_code: str) -> Tuple[Tender, Bidder, Bid]:
        code = scenario_code.upper()

        # Tender
        tender = Tender(
            tender_number=f"TNDR-DEMO-{code}-2026",
            title=f"Demo Tender Scenario {code}",
            description=f"Synthetic demonstration tender for scenario {code}",
            category="GOODS",
            estimated_value=10000000.0,
            status="PUBLISHED",
        )
        self.db.add(tender)
        await self.db.flush()

        # Mandatory Requirement
        req = TenderRequirement(
            tender_id=tender.id,
            requirement_type="TURNOVER",
            operator=">=",
            target_value="5000000.0",
            unit="INR",
            is_mandatory=True,
        )
        self.db.add(req)

        # Bidder
        bidder = Bidder(
            canonical_name=f"Shakti Demo Entity {code} Pvt Ltd",
            pan=f"PAN{code}1234X"[:10],
            gstin=f"27PAN{code}1234X1Z0"[:15],
            registered_address="Plot 99, Industrial Area, Pune, MH",
        )
        self.db.add(bidder)
        await self.db.flush()

        # Bid
        bid = Bid(
            tender_id=tender.id,
            bidder_id=bidder.id,
            bid_number=f"BID-DEMO-{code}-001",
            proposed_price=4800000.0,
            status="SUBMITTED",
        )
        self.db.add(bid)
        await self.db.commit()

        return tender, bidder, bid

demo_data_factory = DemoDataFactory
