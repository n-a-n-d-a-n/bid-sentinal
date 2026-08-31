"""
Demo Execution Context.

Tracks isolated demo_run_id and generated entities per execution run.
"""
import uuid
from typing import Dict, Any, Optional

class DemoExecutionContext:
    def __init__(self, scenario_code: str, mode: str = "FULL_RUN"):
        self.demo_run_id = str(uuid.uuid4())
        self.scenario_code = scenario_code.upper()
        self.mode = mode
        self.tender_id: Optional[str] = None
        self.bidder_id: Optional[str] = None
        self.bid_id: Optional[str] = None
        self.stage_results: Dict[str, Any] = {}
        self.timeline_events: list = []
