"""
Demo Center Schemas.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DemoExecutionMode(str, Enum):
    FULL_RUN = "FULL_RUN"
    STEP_BY_STEP = "STEP_BY_STEP"

class DemoRunStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RESET = "RESET"

class DemoPipelineStage(str, Enum):
    INGESTION = "INGESTION"
    EXTRACTION = "EXTRACTION"
    REQUIREMENTS = "REQUIREMENTS"
    EVIDENCE = "EVIDENCE"
    VERIFICATION = "VERIFICATION"
    CONSISTENCY = "CONSISTENCY"
    GRAPH = "GRAPH"
    ANOMALY = "ANOMALY"
    RISK = "RISK"
    POLICY = "POLICY"
    DECISION_READINESS = "DECISION_READINESS"
    OFFICER_DECISION = "OFFICER_DECISION"
    AUDIT = "AUDIT"

class DemoScenarioSchema(BaseModel):
    code: str
    name: str
    description: str
    category: str
    difficulty: str = "INTERMEDIATE"
    expected_outcome: str
    tags: List[str]
    display_order: int

class DemoRunRequest(BaseModel):
    mode: DemoExecutionMode = DemoExecutionMode.FULL_RUN

class DemoTimelineEvent(BaseModel):
    timestamp_offset_ms: int
    stage: str
    summary: str
    details: Optional[Dict[str, Any]] = None

class DemoRunResultSchema(BaseModel):
    demo_run_id: str
    scenario_code: str
    scenario_name: str
    status: DemoRunStatus
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: int = 0
    expected_outcome: str
    actual_outcome: str
    outcome_match: bool
    stage_results: Dict[str, Any] = Field(default_factory=dict)
