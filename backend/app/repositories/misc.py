"""Audit, verification, document, processing job repositories."""
from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditEvent
from app.models.verification import VerificationRequest, VerificationResult
from app.models.document import Document, DocumentPage, ExtractedField
from app.models.job import ProcessingJob
from app.models.risk import RiskScore, RiskFactor
from app.models.decision import OfficerDecision
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditEvent]):
    model = AuditEvent

    async def log(self, **kwargs) -> AuditEvent:
        """Append-only audit event creation."""
        event = AuditEvent(**kwargs)
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_for_bid(self, bid_id: str) -> List[AuditEvent]:
        result = await self.db.execute(
            select(AuditEvent)
            .where(AuditEvent.bid_id == bid_id)
            .order_by(AuditEvent.timestamp.asc())
        )
        return list(result.scalars().all())

    async def get_for_entity(self, entity_type: str, entity_id: str) -> List[AuditEvent]:
        result = await self.db.execute(
            select(AuditEvent)
            .where(AuditEvent.entity_type == entity_type, AuditEvent.entity_id == entity_id)
            .order_by(AuditEvent.timestamp.asc())
        )
        return list(result.scalars().all())

    async def list_paginated(
        self,
        offset: int,
        limit: int,
        action: Optional[str] = None,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        bid_id: Optional[str] = None,
        from_dt: Optional[datetime] = None,
        to_dt: Optional[datetime] = None,
    ) -> List[AuditEvent]:
        q = select(AuditEvent)
        if action:
            q = q.where(AuditEvent.action == action)
        if category:
            q = q.where(AuditEvent.action_category == category)
        if user_id:
            q = q.where(AuditEvent.user_id == user_id)
        if bid_id:
            q = q.where(AuditEvent.bid_id == bid_id)
        if from_dt:
            q = q.where(AuditEvent.timestamp >= from_dt)
        if to_dt:
            q = q.where(AuditEvent.timestamp <= to_dt)
        q = q.order_by(desc(AuditEvent.timestamp)).offset(offset).limit(limit)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def count_filtered(self, **filters) -> int:
        q = select(func.count()).select_from(AuditEvent)
        result = await self.db.execute(q)
        return result.scalar_one()


class VerificationRepository(BaseRepository[VerificationResult]):
    model = VerificationResult

    async def get_by_bid(self, bid_id: str) -> List[VerificationResult]:
        result = await self.db.execute(
            select(VerificationResult)
            .where(VerificationResult.bid_id == bid_id)
            .order_by(VerificationResult.checked_at.asc())
        )
        return list(result.scalars().all())

    async def count_by_status(self, bid_id: str, status: str) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(VerificationResult).where(
                VerificationResult.bid_id == bid_id,
                VerificationResult.status == status,
            )
        )
        return result.scalar_one()


class DocumentRepository(BaseRepository[Document]):
    model = Document

    async def get_with_pages(self, doc_id: str) -> Optional[Document]:
        result = await self.db.execute(
            select(Document)
            .options(selectinload(Document.pages), selectinload(Document.extracted_fields))
            .where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()

    async def get_by_entity(self, entity_type: str, entity_id: str) -> List[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.entity_type == entity_type, Document.entity_id == entity_id)
            .order_by(Document.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_by_hash(self, sha256_hash: str) -> Optional[Document]:
        result = await self.db.execute(
            select(Document).where(Document.sha256_hash == sha256_hash)
        )
        return result.scalar_one_or_none()


class ProcessingJobRepository(BaseRepository[ProcessingJob]):
    model = ProcessingJob

    async def get_latest_for_entity(self, entity_type: str, entity_id: str) -> Optional[ProcessingJob]:
        result = await self.db.execute(
            select(ProcessingJob)
            .where(ProcessingJob.entity_type == entity_type, ProcessingJob.entity_id == entity_id)
            .order_by(desc(ProcessingJob.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()


class RiskRepository(BaseRepository[RiskScore]):
    model = RiskScore

    async def get_latest_for_bid(self, bid_id: str) -> Optional[RiskScore]:
        result = await self.db.execute(
            select(RiskScore)
            .options(selectinload(RiskScore.factors))
            .where(RiskScore.bid_id == bid_id)
            .order_by(desc(RiskScore.calculated_at))
            .limit(1)
        )
        return result.scalar_one_or_none()


class DecisionRepository(BaseRepository[OfficerDecision]):
    model = OfficerDecision

    async def get_by_bid(self, bid_id: str) -> List[OfficerDecision]:
        result = await self.db.execute(
            select(OfficerDecision)
            .where(OfficerDecision.bid_id == bid_id)
            .order_by(OfficerDecision.decided_at.asc())
        )
        return list(result.scalars().all())
