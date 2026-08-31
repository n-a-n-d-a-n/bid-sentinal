"""Tender repository."""
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tender import Tender, TenderRequirement
from app.repositories.base import BaseRepository


class TenderRepository(BaseRepository[Tender]):
    model = Tender

    async def get_with_requirements(self, tender_id: str) -> Optional[Tender]:
        result = await self.db.execute(
            select(Tender)
            .options(selectinload(Tender.requirements))
            .where(Tender.id == tender_id)
        )
        return result.scalar_one_or_none()

    async def get_by_gem_bid_number(self, gem_bid_number: str) -> Optional[Tender]:
        result = await self.db.execute(
            select(Tender).where(Tender.gem_bid_number == gem_bid_number)
        )
        return result.scalar_one_or_none()

    async def list_paginated(self, offset: int, limit: int, status: Optional[str] = None):
        q = select(Tender)
        if status:
            q = q.where(Tender.status == status)
        q = q.order_by(Tender.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def count_by_status(self, status: Optional[str] = None) -> int:
        q = select(func.count()).select_from(Tender)
        if status:
            q = q.where(Tender.status == status)
        result = await self.db.execute(q)
        return result.scalar_one()


class TenderRequirementRepository(BaseRepository[TenderRequirement]):
    model = TenderRequirement

    async def get_by_tender(self, tender_id: str) -> List[TenderRequirement]:
        result = await self.db.execute(
            select(TenderRequirement)
            .where(TenderRequirement.tender_id == tender_id)
            .order_by(TenderRequirement.category, TenderRequirement.created_at)
        )
        return list(result.scalars().all())

    async def get_approved_rules(self, tender_id: str) -> List[TenderRequirement]:
        result = await self.db.execute(
            select(TenderRequirement)
            .where(
                TenderRequirement.tender_id == tender_id,
                TenderRequirement.is_approved == True,
                TenderRequirement.rule_definition.isnot(None),
            )
        )
        return list(result.scalars().all())
