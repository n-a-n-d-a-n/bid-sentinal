"""Bidder repository."""
from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bidder import Bidder, BidderIdentifier
from app.repositories.base import BaseRepository


class BidderRepository(BaseRepository[Bidder]):
    model = Bidder

    async def get_with_identifiers(self, bidder_id: str) -> Optional[Bidder]:
        result = await self.db.execute(
            select(Bidder)
            .options(selectinload(Bidder.identifiers))
            .where(Bidder.id == bidder_id)
        )
        return result.scalar_one_or_none()

    async def get_by_pan(self, pan: str) -> Optional[Bidder]:
        result = await self.db.execute(select(Bidder).where(Bidder.pan == pan.upper()))
        return result.scalar_one_or_none()

    async def get_by_gstin(self, gstin: str) -> Optional[Bidder]:
        result = await self.db.execute(select(Bidder).where(Bidder.gstin == gstin.upper()))
        return result.scalar_one_or_none()

    async def get_by_cin(self, cin: str) -> Optional[Bidder]:
        result = await self.db.execute(select(Bidder).where(Bidder.cin == cin.upper()))
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 20) -> List[Bidder]:
        q_like = f"%{query.upper()}%"
        result = await self.db.execute(
            select(Bidder)
            .where(
                or_(
                    Bidder.canonical_name.ilike(f"%{query}%"),
                    Bidder.pan == query.upper(),
                    Bidder.gstin == query.upper(),
                    Bidder.cin == query.upper(),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_paginated(self, offset: int, limit: int) -> List[Bidder]:
        result = await self.db.execute(
            select(Bidder)
            .options(selectinload(Bidder.identifiers))
            .order_by(Bidder.canonical_name)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Bidder))
        return result.scalar_one()
