"""Processing job tracking for async pipeline."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    celery_task_id: Mapped[str | None] = mapped_column(String(255), index=True)
    job_type: Mapped[str] = mapped_column(String(50))
    # BID_ANALYSIS | TENDER_ANALYSIS | DOCUMENT_OCR | VERIFICATION | DATASET_GENERATION
    entity_type: Mapped[str | None] = mapped_column(String(30))
    entity_id: Mapped[str | None] = mapped_column(String(36), index=True)

    status: Mapped[str] = mapped_column(String(30), default="QUEUED")
    # QUEUED | RUNNING | COMPLETED | FAILED | CANCELLED
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    current_step: Mapped[str | None] = mapped_column(String(100))
    total_steps: Mapped[int] = mapped_column(Integer, default=0)

    pipeline_steps: Mapped[dict | None] = mapped_column(JSON)  # Step-by-step status
    error_message: Mapped[str | None] = mapped_column(Text)
    error_traceback: Mapped[str | None] = mapped_column(Text)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[float | None] = mapped_column(Float)

    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
