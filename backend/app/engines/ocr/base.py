"""
OCR Engine Architecture Base.

Enforces:
- Standardized OCRResult
- OCR Statuses: NOT_REQUIRED, QUEUED, PROCESSING, COMPLETED, FAILED, UNAVAILABLE
- Safe fallback when OCR dependencies are missing
"""
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class OCRStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"

@dataclass
class OCRResult:
    status: OCRStatus
    extracted_text: str
    confidence: float  # 0.0 to 1.0
    engine_name: str
    page_number: int
    error_message: Optional[str] = None
    bounding_boxes: Optional[Dict[str, Any]] = None

class OCRProvider(ABC):
    engine_name: str = "ABSTRACT"

    @abstractmethod
    async def extract_text(self, image_bytes: bytes, page_number: int) -> OCRResult:
        """Extract text from rendered page image bytes."""
        ...
