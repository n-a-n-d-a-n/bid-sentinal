"""Risk score and contributing factor models."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bid_id: Mapped[str] = mapped_column(String(36), ForeignKey("bids.id"), nullable=False, index=True)

    # Component scores (0-100 scale, higher = more risk)
    compliance_score: Mapped[float | None] = mapped_column(Float)       # 30% weight
    document_integrity_score: Mapped[float | None] = mapped_column(Float)  # 15% weight
    verification_risk_score: Mapped[float | None] = mapped_column(Float)   # 15% weight
    graph_risk_score: Mapped[float | None] = mapped_column(Float)          # 25% weight
    behaviour_risk_score: Mapped[float | None] = mapped_column(Float)      # 15% weight
    overall_risk_score: Mapped[float | None] = mapped_column(Float)

    # Thresholds used
    weights_used: Mapped[dict | None] = mapped_column(JSON)
    risk_level: Mapped[str | None] = mapped_column(String(20))
    # LOW (<30) | MEDIUM (30-60) | HIGH (60-80) | CRITICAL (>80)

    # Anomaly detection
    anomaly_score: Mapped[float | None] = mapped_column(Float)
    anomaly_features: Mapped[dict | None] = mapped_column(JSON)
    isolation_forest_score: Mapped[float | None] = mapped_column(Float)

    explanation: Mapped[str | None] = mapped_column(Text)
    model_version: Mapped[str | None] = mapped_column(String(50))
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    bid: Mapped["Bid"] = relationship("Bid", back_populates="risk_scores")
    factors: Mapped[list["RiskFactor"]] = relationship("RiskFactor", back_populates="risk_score")


class RiskFactor(Base):
    __tablename__ = "risk_factors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    risk_score_id: Mapped[str] = mapped_column(String(36), ForeignKey("risk_scores.id"), nullable=False, index=True)
    factor_type: Mapped[str] = mapped_column(String(100))
    # COMPLIANCE_FAIL | VERIFICATION_CONFLICT | NETWORK_CLUSTER |
    # ANOMALOUS_PRICE | SHARED_DIRECTOR | etc.
    category: Mapped[str] = mapped_column(String(50))
    # COMPLIANCE | DOCUMENT | VERIFICATION | GRAPH | BEHAVIOUR
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20))  # LOW | MEDIUM | HIGH | CRITICAL
    score_contribution: Mapped[float] = mapped_column(Float)
    evidence: Mapped[dict | None] = mapped_column(JSON)
    recommendation: Mapped[str | None] = mapped_column(Text)

    risk_score: Mapped["RiskScore"] = relationship("RiskScore", back_populates="factors")
