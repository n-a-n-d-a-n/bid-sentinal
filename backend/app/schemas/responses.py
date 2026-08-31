"""Compliance, Risk, Audit, and Processing job schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Compliance ─────────────────────────────────────────────────────────────────
class RuleEvaluationResponse(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    mandatory: bool
    result: str
    computed_value: Optional[Any]
    threshold_value: Optional[Any]
    detail: str
    confidence: float


class ComplianceSummaryResponse(BaseModel):
    bid_id: str
    overall_result: str
    compliance_score: float
    total_rules: int
    mandatory_rules: int
    mandatory_passes: int
    mandatory_fails: int
    warnings: List[str]
    rule_results: List[RuleEvaluationResponse]
    evaluated_at: Optional[datetime] = None


# ── Risk ───────────────────────────────────────────────────────────────────────
class RiskFactorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    factor_type: str
    category: str
    description: str
    severity: str
    score_contribution: float
    evidence: Optional[Dict[str, Any]]
    recommendation: Optional[str]


class RiskScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    bid_id: str
    compliance_score: Optional[float]
    document_integrity_score: Optional[float]
    verification_risk_score: Optional[float]
    graph_risk_score: Optional[float]
    behaviour_risk_score: Optional[float]
    overall_risk_score: Optional[float]
    risk_level: Optional[str]
    weights_used: Optional[Dict[str, float]]
    anomaly_score: Optional[float]
    explanation: Optional[str]
    model_version: Optional[str]
    calculated_at: datetime
    factors: List[RiskFactorResponse] = []


# ── Audit ──────────────────────────────────────────────────────────────────────
class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    user_id: Optional[str]
    user_email: Optional[str]
    user_role: Optional[str]
    action: str
    action_category: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    bid_id: Optional[str]
    tender_id: Optional[str]
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    change_summary: Optional[str]
    document_hash: Optional[str]
    rule_version: Optional[str]
    model_version: Optional[str]
    source: Optional[str]
    request_id: Optional[str]
    timestamp: datetime


# ── Processing Jobs ────────────────────────────────────────────────────────────
class ProcessingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    celery_task_id: Optional[str]
    job_type: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    status: str
    progress: int
    current_step: Optional[str]
    total_steps: int
    pipeline_steps: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    created_at: datetime


# ── Health ─────────────────────────────────────────────────────────────────────
class ServiceHealth(BaseModel):
    status: str  # healthy | degraded | unavailable
    latency_ms: Optional[float] = None
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    demo_mode: bool
    services: Dict[str, ServiceHealth]
    timestamp: datetime


# ── Graph ─────────────────────────────────────────────────────────────────────
class GraphNodeResponse(BaseModel):
    id: str
    node_id: str
    entity_type: str
    label: str
    properties: Optional[Dict[str, Any]]
    risk_score: Optional[float]


class GraphEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str
    properties: Optional[Dict[str, Any]]
    confidence: float
    evidence: Optional[str]


class GraphResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]
    tender_id: Optional[str] = None
    bid_id: Optional[str] = None


# ── Policy ─────────────────────────────────────────────────────────────────────
class PolicySearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    tender_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    filters: Optional[Dict[str, Any]] = None


class PolicyChunkResponse(BaseModel):
    chunk_id: str
    text: str
    source_name: str
    source_authority: str
    version: str
    section: Optional[str]
    page_number: Optional[int]
    relevance_score: float
    official_url: Optional[str]


class PolicySearchResponse(BaseModel):
    query: str
    answer: str
    citations: List[PolicyChunkResponse]
    confidence: float
    retrieval_method: str
    warning: Optional[str] = None  # e.g., "LOW_CONFIDENCE" or "NO_RELEVANT_CLAUSE"
