"""Bid model — links a bidder to a tender."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tender_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenders.id"), nullable=False, index=True)
    bidder_id: Mapped[str] = mapped_column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    bid_reference_number: Mapped[str | None] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(50), default="UPLOADED")
    # UPLOADED | PROCESSING | PROCESSED | COMPLIANCE_EVALUATED | RISK_CALCULATED | OFFICER_REVIEW | DECIDED | ERROR

    # Processing job tracking
    processing_job_id: Mapped[str | None] = mapped_column(String(36))

    # Financial details
    quoted_price_inr: Mapped[float | None] = mapped_column(Float)
    quoted_price_currency: Mapped[str] = mapped_column(String(10), default="INR")
    bid_validity_days: Mapped[int | None] = mapped_column(Integer)
    submission_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Scores (computed by engines)
    compliance_score: Mapped[float | None] = mapped_column(Float)
    document_integrity_score: Mapped[float | None] = mapped_column(Float)
    verification_risk_score: Mapped[float | None] = mapped_column(Float)
    graph_risk_score: Mapped[float | None] = mapped_column(Float)
    behaviour_risk_score: Mapped[float | None] = mapped_column(Float)
    overall_risk_score: Mapped[float | None] = mapped_column(Float)
    risk_level: Mapped[str | None] = mapped_column(String(20))  # LOW | MEDIUM | HIGH | CRITICAL

    # Compliance summary
    compliance_result: Mapped[str | None] = mapped_column(String(50))  # PASS | FAIL | CONDITIONAL | MANUAL_REVIEW
    compliance_summary: Mapped[dict | None] = mapped_column(JSON)

    # Officer decision
    decision: Mapped[str | None] = mapped_column(String(50))  # APPROVED | FLAGGED | REJECTED | REFERRED
    decision_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_reason: Mapped[str | None] = mapped_column(Text)

    # Flags
    has_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_manual_review: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    demo_scenario: Mapped[str | None] = mapped_column(String(10))

    metadata_: Mapped[dict | None] = mapped_column(JSON, name="metadata")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    tender: Mapped["Tender"] = relationship("Tender", back_populates="bids")
    bidder: Mapped["Bidder"] = relationship("Bidder", back_populates="bids")
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        primaryjoin="and_(Document.entity_type=='bid', Document.entity_id==Bid.id)",
        foreign_keys="[Document.entity_id]",
        overlaps="bid_documents",
    )
    verification_requests: Mapped[list["VerificationRequest"]] = relationship(
        "VerificationRequest", back_populates="bid"
    )
    rule_evaluations: Mapped[list["RuleEvaluation"]] = relationship("RuleEvaluation", back_populates="bid")
    risk_scores: Mapped[list["RiskScore"]] = relationship("RiskScore", back_populates="bid")
    audit_events: Mapped[list["AuditEvent"]] = relationship("AuditEvent", back_populates="bid")
    decisions: Mapped[list["OfficerDecision"]] = relationship("OfficerDecision", back_populates="bid")
