"""
Tender Requirement Orchestrator.

Extracts & normalizes tender requirements from tender document pages.
Populates TenderRequirement database models with evidence & provenance.
"""
import structlog
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.requirements.schemas import TenderRequirementContract, TenderRequirementExtractionResult
from app.engines.requirements.rule_extractor import requirement_rule_extractor
from app.models.tender import Tender, TenderRequirement

logger = structlog.get_logger(__name__)

class RequirementOrchestratorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_and_save_requirements(
        self,
        tender_id: str,
        pages_text: List[Dict[str, Any]],
    ) -> List[TenderRequirement]:
        all_contracts: List[TenderRequirementContract] = []

        for page in pages_text:
            p_num = page["page_number"]
            p_text = page.get("text", "")
            found = requirement_rule_extractor.extract_requirements(p_text, p_num)
            all_contracts.extend(found)

        # Deduplicate contracts by requirement_type
        deduped: Dict[str, TenderRequirementContract] = {}
        for c in all_contracts:
            key = c.requirement_type.value
            if key not in deduped or c.confidence > deduped[key].confidence:
                deduped[key] = c

        saved_models: List[TenderRequirement] = []
        for contract in deduped.values():
            req_model = TenderRequirement(
                tender_id=tender_id,
                requirement_id=contract.requirement_id,
                category=contract.requirement_type.value,
                description=contract.description,
                mandatory=contract.mandatory,
                rule_definition={
                    "rule_id": contract.requirement_id,
                    "name": contract.name,
                    "category": contract.requirement_type.value,
                    "mandatory": contract.mandatory,
                    "rule_type": "threshold" if contract.operator in (">= ", "<=") else "existence",
                    "field": "annual_turnover_inr" if contract.requirement_type == "TURNOVER" else "gstin",
                    "operator": contract.operator.value,
                    "threshold": contract.required_value,
                    "unit": contract.unit,
                },
                source_document=contract.source_document_id,
                source_page=contract.source_page,
                confidence=contract.confidence,
                is_approved=True,  # Auto-approve extracted requirements for demo
            )
            self.db.add(req_model)
            saved_models.append(req_model)

        await self.db.flush()
        logger.info("tender_requirements_extracted", tender_id=tender_id, count=len(saved_models))
        return saved_models
