"""Bid repository."""
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bid import Bid
from app.repositories.base import BaseRepository


class BidRepository(BaseRepository[Bid]):
    model = Bid

    async def get_with_relations(self, bid_id: str) -> Optional[Bid]:
        result = await self.db.execute(
            select(Bid)
            .options(
                selectinload(Bid.bidder),
                selectinload(Bid.tender),
                selectinload(Bid.documents),
                selectinload(Bid.verification_requests),
                selectinload(Bid.risk_scores),
                selectinload(Bid.decisions),
            )
            .where(Bid.id == bid_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tender(self, tender_id: str) -> List[Bid]:
        result = await self.db.execute(
            select(Bid)
            .options(selectinload(Bid.bidder))
            .where(Bid.tender_id == tender_id)
            .order_by(Bid.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_bidder(self, bidder_id: str) -> List[Bid]:
        result = await self.db.execute(
            select(Bid).where(Bid.bidder_id == bidder_id).order_by(Bid.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_paginated(
        self,
        offset: int,
        limit: int,
        tender_id: Optional[str] = None,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> List[Bid]:
        q = select(Bid).options(selectinload(Bid.bidder), selectinload(Bid.tender))
        if tender_id:
            q = q.where(Bid.tender_id == tender_id)
        if status:
            q = q.where(Bid.status == status)
        if risk_level:
            q = q.where(Bid.risk_level == risk_level)
        q = q.order_by(Bid.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        tender_id: Optional[str] = None,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> int:
        q = select(func.count()).select_from(Bid)
        if tender_id:
            q = q.where(Bid.tender_id == tender_id)
        if status:
            q = q.where(Bid.status == status)
        if risk_level:
            q = q.where(Bid.risk_level == risk_level)
        result = await self.db.execute(q)
        return result.scalar_one()

    async def count_by_risk_level(self, risk_level: str) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Bid).where(Bid.risk_level == risk_level)
        )
        return result.scalar_one()
