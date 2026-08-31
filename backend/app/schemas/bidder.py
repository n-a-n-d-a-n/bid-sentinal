"""Bidder schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BidderIdentifierCreate(BaseModel):
    identifier_type: str = Field(..., description="PAN|GSTIN|CIN|UDYAM|EMAIL|PHONE|DOMAIN")
    identifier_value: str = Field(..., min_length=1, max_length=255)
    is_primary: bool = False
    state: Optional[str] = None


class BidderCreate(BaseModel):
    canonical_name: str = Field(..., min_length=2, max_length=500)
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    entity_type: Optional[str] = Field(None, description="COMPANY|PARTNERSHIP|PROPRIETORSHIP|LLP")
    pan: Optional[str] = Field(None, max_length=20)
    gstin: Optional[str] = Field(None, max_length=20)
    cin: Optional[str] = Field(None, max_length=25)
    udyam_number: Optional[str] = Field(None, max_length=30)
    gem_seller_id: Optional[str] = None
    registered_address: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    incorporation_date: Optional[str] = None
    directors: Optional[List[Dict[str, Any]]] = None
    msme_category: Optional[str] = None
    is_startup: bool = False
    additional_identifiers: Optional[List[BidderIdentifierCreate]] = None


class BidderUpdate(BaseModel):
    canonical_name: Optional[str] = None
    legal_name: Optional[str] = None
    registered_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    directors: Optional[List[Dict[str, Any]]] = None
    msme_category: Optional[str] = None
    is_startup: Optional[bool] = None


class BidderIdentifierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    identifier_type: str
    identifier_value: str
    is_primary: bool
    state: Optional[str]
    created_at: datetime


class BidderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    canonical_name: str
    legal_name: Optional[str]
    trade_name: Optional[str]
    entity_type: Optional[str]
    pan: Optional[str]
    gstin: Optional[str]
    cin: Optional[str]
    udyam_number: Optional[str]
    gem_seller_id: Optional[str]
    registered_address: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    incorporation_date: Optional[str]
    directors: Optional[List[Dict[str, Any]]]
    msme_category: Optional[str]
    is_startup: bool
    is_blacklisted: bool
    blacklist_reference: Optional[str]
    resolution_confidence: float
    created_at: datetime
    updated_at: datetime
    identifiers: List[BidderIdentifierResponse] = []
