"""
Storage Service — MinIO / S3-compatible object storage with safe local fallback.

Responsibilities:
- Object upload / download / delete
- Deterministic key generation
- Existence checking & metadata retrieval
- Streaming large files
- Local disk fallback when MinIO is offline in demo/dev mode
"""
import io
import os
import structlog
from typing import Optional, BinaryIO, Union, Dict, Any
from pathlib import Path

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Fallback local storage directory
LOCAL_STORAGE_DIR = Path("./scratch/storage")

class StorageService:
    def __init__(self):
        self.endpoint = settings.MINIO_ENDPOINT
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.secure = settings.MINIO_SECURE
        self.default_bucket = settings.MINIO_BUCKET_DOCUMENTS
        self._minio_client = None
        self._init_client()

    def _init_client(self):
        try:
            from minio import Minio
            self._minio_client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )
        except Exception as e:
            logger.warning("minio_client_init_warning", error=str(e))
            self._minio_client = None

    def generate_object_key(
        self,
        document_id: str,
        filename: str,
        category: str = "original",
        page_number: Optional[int] = None,
    ) -> str:
        """
        Deterministic key generation strategy:
        documents/{document_id}/original/{filename}
        documents/{document_id}/pages/{page_number}/page.png
        """
        safe_filename = Path(filename).name.replace(" ", "_")
        if category == "original":
            return f"documents/{document_id}/original/{safe_filename}"
        elif category == "page" and page_number is not None:
            return f"documents/{document_id}/pages/page_{page_number}.png"
        elif category == "ocr":
            return f"documents/{document_id}/ocr/{safe_filename}"
        elif category == "extraction":
            return f"documents/{document_id}/extraction/{safe_filename}"
        else:
            return f"documents/{document_id}/{category}/{safe_filename}"

    def upload_bytes(
        self,
        data: bytes,
        object_key: str,
        content_type: str = "application/octet-stream",
        bucket: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        bucket = bucket or self.default_bucket
        stream = io.BytesIO(data)
        length = len(data)

        if self._minio_client:
            try:
                if not self._minio_client.bucket_exists(bucket):
                    self._minio_client.make_bucket(bucket)
                self._minio_client.put_object(
                    bucket_name=bucket,
                    object_name=object_key,
                    data=stream,
                    length=length,
                    content_type=content_type,
                    metadata=metadata,
                )
                logger.info("minio_upload_success", bucket=bucket, key=object_key, size=length)
                return object_key
            except Exception as exc:
                logger.warning("minio_upload_fallback", error=str(exc), key=object_key)

        # Fallback to local storage
        local_path = LOCAL_STORAGE_DIR / bucket / object_key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        logger.info("local_storage_upload_success", path=str(local_path), size=length)
        return object_key

    def download_bytes(self, object_key: str, bucket: Optional[str] = None) -> bytes:
        bucket = bucket or self.default_bucket

        if self._minio_client:
            try:
                response = self._minio_client.get_object(bucket, object_key)
                data = response.read()
                response.close()
                response.release_conn()
                return data
            except Exception as exc:
                logger.warning("minio_download_fallback", error=str(exc), key=object_key)

        local_path = LOCAL_STORAGE_DIR / bucket / object_key
        if local_path.exists():
            return local_path.read_bytes()

        raise FileNotFoundError(f"Object {object_key} not found in MinIO or local storage.")

    def object_exists(self, object_key: str, bucket: Optional[str] = None) -> bool:
        bucket = bucket or self.default_bucket
        if self._minio_client:
            try:
                self._minio_client.stat_object(bucket, object_key)
                return True
            except Exception:
                pass

        local_path = LOCAL_STORAGE_DIR / bucket / object_key
        return local_path.exists()

    def delete_object(self, object_key: str, bucket: Optional[str] = None) -> bool:
        bucket = bucket or self.default_bucket
        deleted = False
        if self._minio_client:
            try:
                self._minio_client.remove_object(bucket, object_key)
                deleted = True
            except Exception as exc:
                logger.warning("minio_delete_failed", error=str(exc), key=object_key)

        local_path = LOCAL_STORAGE_DIR / bucket / object_key
        if local_path.exists():
            local_path.unlink()
            deleted = True

        return deleted

storage_service = StorageService()
