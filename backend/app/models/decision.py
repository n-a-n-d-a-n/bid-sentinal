"""Officer decision model."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OfficerDecision(Base):
    __tablename__ = "officer_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bid_id: Mapped[str] = mapped_column(String(36), ForeignKey("bids.id"), nullable=False, index=True)
    officer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    # APPROVED | FLAGGED | REJECTED | REFERRED | PENDING_MORE_INFO

    previous_result: Mapped[str | None] = mapped_column(String(50))
    new_result: Mapped[str] = mapped_column(String(50))

    reason: Mapped[str] = mapped_column(Text, nullable=False)  # MANDATORY - can never be empty
    evidence_reviewed: Mapped[dict | None] = mapped_column(JSON)  # Evidence the officer reviewed
    override_justification: Mapped[str | None] = mapped_column(Text)  # If overriding AI recommendation

    # Version tracking for reproducibility
    rule_version: Mapped[str | None] = mapped_column(String(50))
    model_version: Mapped[str | None] = mapped_column(String(50))
    risk_score_snapshot: Mapped[dict | None] = mapped_column(JSON)

    is_final: Mapped[bool] = mapped_column(default=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    bid: Mapped["Bid"] = relationship("Bid", back_populates="decisions")
    officer: Mapped["User"] = relationship("User", back_populates="decisions")
