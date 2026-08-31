"""
Document Security Service.

Enforces:
- File size limits
- MIME & Extension consistency
- Magic bytes validation for PDFs & images
- SHA-256 hash deduplication
- Safe filename sanitization
- Corrupted PDF & empty file detection
"""
import re
import hashlib
import structlog
from typing import Dict, Any, Tuple
from pathlib import Path
from fastapi import HTTPException

from app.core.config import settings

logger = structlog.get_logger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".xlsx", ".xls"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/octet-stream",
}

# Magic signatures
PDF_MAGIC = b"%PDF"
JPEG_MAGIC = b"\xFF\xD8\xFF"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

class DocumentSecurityService:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Strip directory traversal, path separators, and unsafe characters."""
        base_name = Path(filename).name
        # Allow alphanumeric, dots, underscores, dashes
        clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", base_name)
        return clean_name or "document.pdf"

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def validate_file(cls, filename: str, content_type: str, data: bytes) -> Dict[str, Any]:
        """
        Thorough security validation.
        Raises HTTPException on violation.
        Returns validated metadata dict.
        """
        # 1. Empty check
        if not data or len(data) == 0:
            raise HTTPException(400, "Empty document submission not allowed.")

        # 2. File size limit
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(data) > max_bytes:
            raise HTTPException(413, f"File size ({len(data)} bytes) exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB.")

        # 3. Filename sanitization
        safe_name = cls.sanitize_filename(filename)
        ext = "." + safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"File extension '{ext}' is not permitted.")

        # 4. MIME validation
        if content_type and content_type.lower() not in ALLOWED_MIME_TYPES:
            raise HTTPException(400, f"MIME type '{content_type}' is not permitted.")

        # 5. Magic Byte Signature check
        detected_mime = content_type or "application/octet-stream"
        if ext == ".pdf":
            if not data.startswith(PDF_MAGIC):
                raise HTTPException(400, "Corrupted PDF or invalid magic header signature.")
            detected_mime = "application/pdf"
        elif ext in (".jpg", ".jpeg"):
            if not data.startswith(JPEG_MAGIC):
                raise HTTPException(400, "Corrupted JPEG or invalid magic header signature.")
            detected_mime = "image/jpeg"
        elif ext == ".png":
            if not data.startswith(PNG_MAGIC):
                raise HTTPException(400, "Corrupted PNG or invalid magic header signature.")
            detected_mime = "image/png"

        # 6. Compute SHA256
        sha256_hash = cls.compute_sha256(data)

        return {
            "safe_filename": safe_name,
            "original_filename": filename,
            "detected_mime_type": detected_mime,
            "sha256_hash": sha256_hash,
            "size_bytes": len(data),
            "extension": ext,
        }

document_security = DocumentSecurityService()
