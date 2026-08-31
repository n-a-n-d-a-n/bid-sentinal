"""
Append-Only Audit Ledger Manager.

Appends audit events with cryptographic hash chaining.
Strictly append-only: No UPDATE or DELETE operations exposed.
"""
import structlog
from typing import Dict, Any, Optional
from datetime import UTC, datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditEvent
from app.engines.audit.hasher import audit_hasher, GENESIS_HASH

logger = structlog.get_logger(__name__)

class AuditLedgerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def append_event(
        self,
        action: str,
        action_category: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        bid_id: Optional[str] = None,
        tender_id: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        change_summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        # Fetch last event to link previous_event_hash
        stmt = select(AuditEvent).order_by(desc(AuditEvent.timestamp), desc(AuditEvent.id)).limit(1)
        res = await self.db.execute(stmt)
        last_event: Optional[AuditEvent] = res.scalar_one_or_none()

        prev_hash = last_event.event_hash if (last_event and last_event.event_hash) else GENESIS_HASH

        now_dt = datetime.now(UTC)
        ts_iso = now_dt.isoformat()

        payload = new_value or metadata or {}
        curr_hash = audit_hasher.calculate_event_hash(action, entity_id, payload, ts_iso, prev_hash)

        event = AuditEvent(
            action=action,
            action_category=action_category,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            bid_id=bid_id,
            tender_id=tender_id,
            old_value=old_value,
            new_value=new_value,
            change_summary=change_summary,
            previous_event_hash=prev_hash,
            event_hash=curr_hash,
            metadata_=metadata,
            timestamp=now_dt,
        )
        self.db.add(event)
        await self.db.commit()

        logger.info("audit_event_appended", action=action, event_id=event.id, hash=curr_hash[:8])
        return event

audit_ledger = AuditLedgerService
