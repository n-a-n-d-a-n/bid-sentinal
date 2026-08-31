"""Bid schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import BidStatus, RiskLevel, ComplianceResult


class BidCreate(BaseModel):
    tender_id: str
    bidder_id: str
    bid_reference_number: Optional[str] = None
    quoted_price_inr: Optional[float] = Field(None, ge=0)
    quoted_price_currency: str = "INR"
    bid_validity_days: Optional[int] = Field(None, ge=1)
    submission_timestamp: Optional[datetime] = None


class BidUpdate(BaseModel):
    bid_reference_number: Optional[str] = None
    quoted_price_inr: Optional[float] = None
    status: Optional[str] = None


class BidResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tender_id: str
    bidder_id: str
    bid_reference_number: Optional[str]
    status: str
    quoted_price_inr: Optional[float]
    quoted_price_currency: str
    bid_validity_days: Optional[int]
    submission_timestamp: Optional[datetime]
    compliance_score: Optional[float]
    document_integrity_score: Optional[float]
    verification_risk_score: Optional[float]
    graph_risk_score: Optional[float]
    behaviour_risk_score: Optional[float]
    overall_risk_score: Optional[float]
    risk_level: Optional[str]
    compliance_result: Optional[str]
    compliance_summary: Optional[Dict[str, Any]]
    decision: Optional[str]
    decision_by: Optional[str]
    decision_at: Optional[datetime]
    decision_reason: Optional[str]
    has_anomaly: bool
    requires_manual_review: bool
    is_demo: bool
    demo_scenario: Optional[str]
    created_at: datetime
    updated_at: datetime


class DecisionCreate(BaseModel):
    decision: str = Field(..., description="APPROVED|FLAGGED|REJECTED|REFERRED|PENDING_MORE_INFO")
    reason: str = Field(..., min_length=10, max_length=5000)
    override_justification: Optional[str] = None
    evidence_reviewed: Optional[Dict[str, Any]] = None


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    bid_id: str
    officer_id: str
    decision: str
    previous_result: Optional[str]
    new_result: str
    reason: str
    override_justification: Optional[str]
    evidence_reviewed: Optional[Dict[str, Any]]
    rule_version: Optional[str]
    model_version: Optional[str]
    risk_score_snapshot: Optional[Dict[str, Any]]
    is_final: bool
    decided_at: datetime
