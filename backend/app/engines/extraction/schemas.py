"""
Extraction Contract Schemas.

CRITICAL GUARANTEE:
Every extracted value must contain evidence and provenance:
- field_name
- field_value
- confidence
- source_document_id
- page_number
- text_excerpt
- extraction_method (RULE | REGEX | TABLE | LLM | HYBRID | MANUAL)
"""
from enum import Enum
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class ExtractionMethod(str, Enum):
    RULE = "RULE"
    REGEX = "REGEX"
    TABLE = "TABLE"
    LLM = "LLM"
    HYBRID = "HYBRID"
    MANUAL = "MANUAL"

class ExtractedFieldContract(BaseModel):
    field_name: str
    field_value: Optional[str] = None
    field_value_normalized: Optional[str] = None
    data_type: str = "string"  # string | number | date | boolean
    confidence: float = Field(..., ge=0.0, le=1.0)
    page_number: Optional[int] = None
    text_excerpt: Optional[str] = None
    extraction_method: ExtractionMethod
    validation_status: str = "VALID"  # PENDING | VALID | INVALID | REVIEW
    validation_error: Optional[str] = None

class BidderExtractionSchema(BaseModel):
    legal_name: Optional[ExtractedFieldContract] = None
    trade_name: Optional[ExtractedFieldContract] = None
    pan: Optional[ExtractedFieldContract] = None
    gstin: Optional[ExtractedFieldContract] = None
    cin: Optional[ExtractedFieldContract] = None
    udyam_number: Optional[ExtractedFieldContract] = None
    registered_address: Optional[ExtractedFieldContract] = None
    email: Optional[ExtractedFieldContract] = None
    phone: Optional[ExtractedFieldContract] = None

class FinancialExtractionSchema(BaseModel):
    annual_turnover_inr: Optional[ExtractedFieldContract] = None
    net_worth_inr: Optional[ExtractedFieldContract] = None
    financial_year: Optional[ExtractedFieldContract] = None
    ca_name: Optional[ExtractedFieldContract] = None
    ca_udin: Optional[ExtractedFieldContract] = None

class DocumentExtractionResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    document_id: str
    document_type: str
    fields: List[ExtractedFieldContract]
    prompt_version: Optional[str] = None
    model_name: Optional[str] = None
