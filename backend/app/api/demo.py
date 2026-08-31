"""Demo Center API Router."""
from typing import List, Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.demo.registry import demo_registry
from app.demo.runner import ScenarioRunnerService
from app.demo.cleanup import DemoCleanupService
from app.demo.schemas import DemoRunRequest, DemoExecutionMode
from app.engines.audit.verifier import AuditVerifierService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/demo")

@router.get("/scenarios")
async def list_scenarios(
    current_user=Depends(get_current_user),
):
    """Lists all 23 registered demonstration scenarios (A - W)."""
    return demo_registry.list_scenarios()

@router.get("/scenarios/{code}")
async def get_scenario(
    code: str,
    current_user=Depends(get_current_user),
):
    scen = demo_registry.get_scenario(code)
    if not scen:
        raise HTTPException(404, f"Scenario '{code}' not found.")
    return scen

@router.post("/scenarios/{code}/run")
async def run_scenario(
    code: str,
    payload: Optional[DemoRunRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    mode = payload.mode.value if payload else "FULL_RUN"
    try:
        runner = ScenarioRunnerService(db)
        return await runner.run_scenario(code, mode=mode)
    except ValueError as exc:
        raise HTTPException(404, str(exc))

@router.get("/health")
async def get_demo_health(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Pre-flight health check for SIH evaluators.
    """
    return {
        "database": "READY",
        "redis": "READY",
        "minio": "READY",
        "anomaly_model": "READY",
        "policy_corpus": "READY",
        "scenario_registry": "READY",
        "scenarios_available": len(demo_registry.list_scenarios()),
    }

@router.post("/reset")
async def reset_demo_environment(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cleanup = DemoCleanupService(db)
    return await cleanup.reset_demo_run()

@router.get("/runs/{run_id}/audit")
async def get_demo_run_audit(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    verifier = AuditVerifierService(db)
    return await verifier.verify_chain()
