"""Tender schemas."""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TenderCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    gem_bid_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    department: Optional[str] = None
    ministry: Optional[str] = None
    category: Optional[str] = None
    estimated_value_inr: Optional[float] = Field(None, ge=0)
    bid_submission_deadline: Optional[date] = None
    technical_bid_opening: Optional[date] = None
    financial_bid_opening: Optional[date] = None
    published_date: Optional[date] = None
    msme_applicable: bool = False
    startup_applicable: bool = False
    make_in_india: bool = False
    local_content_min_pct: Optional[float] = Field(None, ge=0, le=100)


class TenderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = None
    department: Optional[str] = None
    estimated_value_inr: Optional[float] = None
    bid_submission_deadline: Optional[date] = None
    status: Optional[str] = None


class TenderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    gem_bid_number: Optional[str]
    title: str
    description: Optional[str]
    department: Optional[str]
    ministry: Optional[str]
    category: Optional[str]
    status: str
    estimated_value_inr: Optional[float]
    currency: str
    bid_submission_deadline: Optional[date]
    technical_bid_opening: Optional[date]
    financial_bid_opening: Optional[date]
    published_date: Optional[date]
    requirements_approved: bool
    msme_applicable: bool
    startup_applicable: bool
    make_in_india: bool
    local_content_min_pct: Optional[float]
    created_at: datetime
    updated_at: datetime


class TenderRequirementCreate(BaseModel):
    requirement_id: Optional[str] = None
    category: str = Field(..., description="FINANCIAL|TECHNICAL|EXPERIENCE|COMPLIANCE|DOCUMENT")
    description: str = Field(..., min_length=5)
    mandatory: bool = True
    rule_definition: Optional[Dict[str, Any]] = None
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None


class TenderRequirementUpdate(BaseModel):
    description: Optional[str] = None
    mandatory: Optional[bool] = None
    rule_definition: Optional[Dict[str, Any]] = None
    officer_notes: Optional[str] = None
    is_approved: Optional[bool] = None


class TenderRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tender_id: str
    requirement_id: Optional[str]
    category: str
    description: str
    mandatory: bool
    rule_definition: Optional[Dict[str, Any]]
    source_document: Optional[str]
    source_page: Optional[int]
    confidence: Optional[float]
    effective_from: Optional[date]
    effective_until: Optional[date]
    is_approved: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    officer_notes: Optional[str]
    version: int
    created_at: datetime
