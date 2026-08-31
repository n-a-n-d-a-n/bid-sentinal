"""Document and extracted field schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import DocumentType


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    entity_id: str
    filename: str
    original_filename: str
    content_type: str
    size_bytes: int
    page_count: Optional[int]
    sha256_hash: str
    document_type: str
    classification_confidence: Optional[float]
    classification_method: Optional[str]
    ocr_status: str
    average_ocr_confidence: Optional[float]
    extraction_status: str
    security_status: str
    is_corrupted: bool
    is_demo: bool
    is_synthetic: bool
    created_at: datetime


class ExtractedFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    field_name: str
    field_value: Optional[str]
    field_value_normalized: Optional[str]
    data_type: Optional[str]
    confidence: Optional[float]
    page_number: Optional[int]
    bounding_box: Optional[Dict[str, Any]]
    extraction_method: str
    validation_status: str
    validation_error: Optional[str]
    consistency_status: Optional[str]
    created_at: datetime


class DocumentPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    page_number: int
    text: Optional[str]
    ocr_confidence: Optional[float]
    ocr_engine: Optional[str]
    is_scanned: bool
