"""
Tender Requirement Extraction Schemas.

Canonical Requirement Schema & Types:
- Requirement Types: ELIGIBILITY, FINANCIAL, TECHNICAL, EXPERIENCE, LEGAL, REGISTRATION, TAX, EMD, TURNOVER, NET_WORTH, PAST_CONTRACT, CERTIFICATION, DOCUMENT_SUBMISSION, DEADLINE, LOCATION, QUANTITY, TECHNICAL_SPECIFICATION
- Operators: GREATER_THAN_OR_EQUAL, LESS_THAN_OR_EQUAL, EQUAL, REQUIRED, CONTAINS, EXISTS
"""
from enum import Enum
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class RequirementType(str, Enum):
    ELIGIBILITY = "ELIGIBILITY"
    FINANCIAL = "FINANCIAL"
    TECHNICAL = "TECHNICAL"
    EXPERIENCE = "EXPERIENCE"
    LEGAL = "LEGAL"
    REGISTRATION = "REGISTRATION"
    TAX = "TAX"
    EMD = "EMD"
    TURNOVER = "TURNOVER"
    NET_WORTH = "NET_WORTH"
    PAST_CONTRACT = "PAST_CONTRACT"
    CERTIFICATION = "CERTIFICATION"
    DOCUMENT_SUBMISSION = "DOCUMENT_SUBMISSION"
    DEADLINE = "DEADLINE"
    LOCATION = "LOCATION"
    QUANTITY = "QUANTITY"
    TECHNICAL_SPECIFICATION = "TECHNICAL_SPECIFICATION"

class RequirementOperator(str, Enum):
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    EQUAL = "=="
    REQUIRED = "REQUIRED"
    CONTAINS = "CONTAINS"
    EXISTS = "EXISTS"

class TenderRequirementContract(BaseModel):
    requirement_id: str
    tender_id: Optional[str] = None
    requirement_type: RequirementType
    name: str
    description: str
    operator: RequirementOperator = RequirementOperator.REQUIRED
    required_value: Optional[Any] = None
    unit: Optional[str] = None  # INR, Crore, Years, Count, etc.
    mandatory: bool = True
    source_document_id: Optional[str] = None
    source_page: Optional[int] = None
    source_excerpt: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    extraction_method: str = "HYBRID"  # RULE | REGEX | LLM | HYBRID

class TenderRequirementExtractionResult(BaseModel):
    tender_id: str
    requirements: List[TenderRequirementContract]
    prompt_version: str = "tender_requirement_v1"
    pipeline_version: str = "3.0.0"
