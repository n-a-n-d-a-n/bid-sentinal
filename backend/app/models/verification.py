"""Verification request and result models."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bid_id: Mapped[str] = mapped_column(String(36), ForeignKey("bids.id"), nullable=False, index=True)
    bidder_id: Mapped[str] = mapped_column(String(36), ForeignKey("bidders.id"), index=True)
    provider: Mapped[str] = mapped_column(String(50))
    # GST | UDYAM | MCA | PAN | EPFO | ESIC | DIGILOCKER | BIS | GEM | BLACKLIST
    queried_identifier: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(30), default="PENDING")
    # PENDING | COMPLETED | FAILED | RETRY
    retry_count: Mapped[int] = mapped_column(default=0)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    bid: Mapped["Bid"] = relationship("Bid", back_populates="verification_requests")
    results: Mapped[list["VerificationResult"]] = relationship("VerificationResult", back_populates="request")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("verification_requests.id"), nullable=False)
    bid_id: Mapped[str] = mapped_column(String(36), ForeignKey("bids.id"), index=True)
    bidder_id: Mapped[str] = mapped_column(String(36), ForeignKey("bidders.id"), index=True)

    source: Mapped[str] = mapped_column(String(50))  # e.g. "GST_MOCK_ADAPTER"
    provider: Mapped[str] = mapped_column(String(50))
    queried_identifier: Mapped[str] = mapped_column(String(255))
    returned_identifier: Mapped[str | None] = mapped_column(String(255))

    status: Mapped[str] = mapped_column(String(30))
    # VERIFIED | CONFLICT | NOT_FOUND | UNAVAILABLE | UNAUTHORIZED | PENDING | NOT_APPLICABLE

    # CRITICAL: UNAVAILABLE must never become PASS
    is_unavailable: Mapped[bool] = mapped_column(Boolean, default=False)

    returned_data: Mapped[dict | None] = mapped_column(JSON)  # Full API response
    conflict_details: Mapped[str | None] = mapped_column(Text)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    source_reference: Mapped[str | None] = mapped_column(String(500))  # Official URL/reference
    authorization_context: Mapped[str | None] = mapped_column(String(100))
    # "LIVE_API" | "MOCK_SANDBOX" | "DEMO" | "MANUAL"
    confidence: Mapped[float | None] = mapped_column(Float)
    error_code: Mapped[str | None] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)

    # Clearly label demo/mock data
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    request: Mapped["VerificationRequest"] = relationship("VerificationRequest", back_populates="results")
