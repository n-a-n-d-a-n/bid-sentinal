"""Rule definition and evaluation models."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tender_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("tenders.id"), index=True)
    requirement_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("tender_requirements.id"))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))
    # FINANCIAL | TECHNICAL | EXPERIENCE | ELIGIBILITY | DOCUMENT_EXISTENCE | COMPLIANCE
    rule_type: Mapped[str] = mapped_column(String(50))
    # THRESHOLD | AVERAGE | SUM | COUNT | DATE_VALIDITY | EXISTENCE | SET_MEMBERSHIP |
    # CROSS_EQUALITY | CONDITIONAL | PERCENTAGE | MIN_MAX
    definition: Mapped[dict] = mapped_column(JSON, nullable=False)  # Full rule JSON
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    evaluations: Mapped[list["RuleEvaluation"]] = relationship("RuleEvaluation", back_populates="rule")


class RuleEvaluation(Base):
    __tablename__ = "rule_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("rules.id"), nullable=False, index=True)
    bid_id: Mapped[str] = mapped_column(String(36), ForeignKey("bids.id"), nullable=False, index=True)
    requirement_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("tender_requirements.id"))

    result: Mapped[str] = mapped_column(String(30))
    # PASS | FAIL | CONDITIONAL | MANUAL_REVIEW | NOT_VERIFIED | NOT_APPLICABLE
    result_detail: Mapped[str | None] = mapped_column(Text)
    computed_value: Mapped[str | None] = mapped_column(String(500))  # Actual value computed
    threshold_value: Mapped[str | None] = mapped_column(String(500))  # Threshold compared against
    evidence: Mapped[dict | None] = mapped_column(JSON)  # Evidence chain
    confidence: Mapped[float | None] = mapped_column(Float)
    rule_version: Mapped[int] = mapped_column(Integer, default=1)
    model_version: Mapped[str | None] = mapped_column(String(50))
    evaluation_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    rule: Mapped["Rule"] = relationship("Rule", back_populates="evaluations")
    bid: Mapped["Bid"] = relationship("Bid", back_populates="rule_evaluations")
    requirement: Mapped["TenderRequirement | None"] = relationship(
        "TenderRequirement", back_populates="rule_evaluations"
    )
