"""
Processing Job Status Router.

Provides status monitoring for asynchronous document & bid processing jobs.
"""
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.job import ProcessingJob
from app.schemas.responses import ProcessingJobResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/processing")

@router.get("/{job_id}", response_model=ProcessingJobResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(ProcessingJob).where(ProcessingJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Processing job not found.")
    return job
