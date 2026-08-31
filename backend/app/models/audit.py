"""Append-only audit event ledger with cryptographic hash chaining."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Actor
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    user_email: Mapped[str | None] = mapped_column(String(255))  # Denormalized for audit permanence
    user_role: Mapped[str | None] = mapped_column(String(50))

    # Action
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # e.g. DOCUMENT_UPLOADED | REQUIREMENT_APPROVED | DECISION_RECORDED |
    #      VERIFICATION_COMPLETED | RULE_EVALUATED | AI_EXTRACTION | etc.
    action_category: Mapped[str] = mapped_column(String(50))
    # DOCUMENT | VERIFICATION | COMPLIANCE | DECISION | ADMIN | SYSTEM | AI | SECURITY

    # Entity
    entity_type: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[str | None] = mapped_column(String(36), index=True)

    # Bid/Tender context
    bid_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bids.id"), index=True)
    tender_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("tenders.id"))

    # Change tracking
    old_value: Mapped[dict | None] = mapped_column(JSON)
    new_value: Mapped[dict | None] = mapped_column(JSON)
    change_summary: Mapped[str | None] = mapped_column(Text)

    # Cryptographic Tamper-Evident Hash Chain
    previous_event_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    event_hash: Mapped[str | None] = mapped_column(String(64), index=True)

    # Technical context
    document_hash: Mapped[str | None] = mapped_column(String(64))
    rule_version: Mapped[str | None] = mapped_column(String(50))
    model_version: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(100))  # System component
    request_id: Mapped[str | None] = mapped_column(String(36))
    ip_address: Mapped[str | None] = mapped_column(String(50))
    user_agent: Mapped[str | None] = mapped_column(String(500))

    # Metadata
    metadata_: Mapped[dict | None] = mapped_column(JSON, name="metadata")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True
    )

    user: Mapped["User | None"] = relationship("User", back_populates="audit_events")
    bid: Mapped["Bid | None"] = relationship("Bid", back_populates="audit_events")


class AuditLedgerImmutableException(PermissionError):
    """Raised when an attempt is made to update or delete an immutable audit ledger entry."""
    pass


from sqlalchemy import event


@event.listens_for(AuditEvent, "before_update")
def _prevent_audit_update(mapper, connection, target):
    raise AuditLedgerImmutableException("Audit ledger is append-only. UPDATE operations are strictly prohibited.")


@event.listens_for(AuditEvent, "before_delete")
def _prevent_audit_delete(mapper, connection, target):
    raise AuditLedgerImmutableException("Audit ledger is append-only. DELETE operations are strictly prohibited.")

