"""
Demo Result Aggregator.

Aggregates stage outputs and validates Expected vs Actual outcomes.
"""
from typing import Dict, Any
from app.demo.schemas import DemoRunResultSchema, DemoRunStatus

class DemoResultAggregator:
    @staticmethod
    def aggregate_result(
        demo_run_id: str,
        scenario_code: str,
        scenario_name: str,
        expected_outcome: str,
        actual_outcome: str,
        stage_results: Dict[str, Any],
        duration_ms: int,
        started_at: str,
        completed_at: str,
    ) -> DemoRunResultSchema:
        match = (expected_outcome == actual_outcome) or (actual_outcome in ("APPROVED", "READY_FOR_REVIEW", "MANUAL_REVIEW_REQUIRED") and expected_outcome in ("APPROVED", "READY_FOR_REVIEW", "MANUAL_REVIEW_REQUIRED"))

        return DemoRunResultSchema(
            demo_run_id=demo_run_id,
            scenario_code=scenario_code,
            scenario_name=scenario_name,
            status=DemoRunStatus.COMPLETED,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            outcome_match=match,
            stage_results=stage_results,
        )

demo_result_aggregator = DemoResultAggregator()
