"""Verification schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.common import VerificationStatus


class VerificationResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    request_id: str
    bid_id: Optional[str]
    bidder_id: Optional[str]
    source: str
    provider: str
    queried_identifier: str
    returned_identifier: Optional[str]
    status: str
    is_unavailable: bool
    returned_data: Optional[Dict[str, Any]]
    conflict_details: Optional[str]
    checked_at: datetime
    source_reference: Optional[str]
    authorization_context: str
    confidence: Optional[float]
    error_code: Optional[str]
    error_message: Optional[str]
    is_demo: bool
    is_mock: bool


class VerificationSummary(BaseModel):
    bid_id: str
    total: int
    verified: int
    conflicts: int
    unavailable: int
    not_found: int
    unauthorized: int
    pending: int
    results: List[VerificationResultResponse]
    # CRITICAL: UNAVAILABLE must never auto-pass
    has_blocking_unavailable: bool
    can_auto_pass: bool  # True only if all mandatory checks are VERIFIED


class VerifyRequest(BaseModel):
    provider: str
    identifier: str
    scenario: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None
