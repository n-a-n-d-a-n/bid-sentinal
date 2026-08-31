"""Common shared Pydantic schemas — pagination, errors, enums."""
from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIError(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    detail: Optional[Any] = None


class APIErrorResponse(BaseModel):
    error: APIError


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(items=items, total=total, page=page, page_size=page_size, pages=pages)


class MessageResponse(BaseModel):
    message: str
    request_id: Optional[str] = None


class IDResponse(BaseModel):
    id: str
    message: str = "Created successfully"


# ── Shared Enums ───────────────────────────────────────────────────────────────
class UserRole(str, Enum):
    PROCUREMENT_OFFICER = "PROCUREMENT_OFFICER"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"
    SYSTEM = "SYSTEM"


class BidStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    COMPLIANCE_EVALUATED = "COMPLIANCE_EVALUATED"
    RISK_CALCULATED = "RISK_CALCULATED"
    OFFICER_REVIEW = "OFFICER_REVIEW"
    DECIDED = "DECIDED"
    ERROR = "ERROR"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CONFLICT = "CONFLICT"
    NOT_FOUND = "NOT_FOUND"
    UNAVAILABLE = "UNAVAILABLE"
    UNAUTHORIZED = "UNAUTHORIZED"
    PENDING = "PENDING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ComplianceResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CONDITIONAL = "CONDITIONAL"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    NOT_VERIFIED = "NOT_VERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class DocumentType(str, Enum):
    GST_CERTIFICATE = "GST_CERTIFICATE"
    PAN_DOCUMENT = "PAN_DOCUMENT"
    UDYAM_CERTIFICATE = "UDYAM_CERTIFICATE"
    MCA_DOCUMENT = "MCA_DOCUMENT"
    FINANCIAL_STATEMENT = "FINANCIAL_STATEMENT"
    OEM_AUTHORIZATION = "OEM_AUTHORIZATION"
    EXPERIENCE_CERTIFICATE = "EXPERIENCE_CERTIFICATE"
    BANK_GUARANTEE = "BANK_GUARANTEE"
    DECLARATION = "DECLARATION"
    STARTUP_CERTIFICATE = "STARTUP_CERTIFICATE"
    MSME_DOCUMENT = "MSME_DOCUMENT"
    EPFO_DOCUMENT = "EPFO_DOCUMENT"
    ESIC_DOCUMENT = "ESIC_DOCUMENT"
    BLACKLIST_DOCUMENT = "BLACKLIST_DOCUMENT"
    TENDER_DOCUMENT = "TENDER_DOCUMENT"
    OTHER = "OTHER"


class TimestampMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: Optional[datetime] = None
