"""
Async processing tasks for document pipeline & bid analysis.

Architecture:
- BackgroundTasks runner for async jobs
- Tracks job status in processing_jobs table
- Idempotent execution
"""
import asyncio
import structlog
from datetime import UTC, datetime
from typing import Optional

from app.core.database import AsyncSessionLocal
from app.services.pipeline_orchestrator import PipelineOrchestratorService

logger = structlog.get_logger(__name__)

async def process_document_task(document_id: str, job_id: str):
    """Background task for processing a single uploaded document."""
    logger.info("process_document_task_start", document_id=document_id, job_id=job_id)
    async with AsyncSessionLocal() as db:
        try:
            orchestrator = PipelineOrchestratorService(db)
            res = await orchestrator.process_document(document_id, job_id=job_id)
            logger.info("process_document_task_success", document_id=document_id, result=res)
        except Exception as exc:
            logger.error("process_document_task_failed", document_id=document_id, error=str(exc), exc_info=True)
            from app.models.job import ProcessingJob
            from sqlalchemy import update
            await db.execute(
                update(ProcessingJob)
                .where(ProcessingJob.id == job_id)
                .values(status="FAILED", error_message=str(exc), completed_at=datetime.now(UTC))
            )
            await db.commit()

async def analyze_bid_task(bid_id: str, job_id: str):
    """
    Full bid analysis pipeline task:
    1. Process all documents attached to bid
    2. Run auto verification checks
    3. Run deterministic compliance rules
    4. Calculate 5-component risk score
    """
    logger.info("analyze_bid_task_start", bid_id=bid_id, job_id=job_id)
    async with AsyncSessionLocal() as db:
        try:
            from app.repositories.misc import DocumentRepository, VerificationRepository, RiskRepository
            from app.repositories.bids import BidRepository
            from app.repositories.tenders import TenderRequirementRepository
            from app.engines.verification_engine.mock_adapters import MockGSTProvider, MockPANProvider, MockBlacklistProvider
            from app.engines.compliance_engine.engine import ComplianceEngine
            from app.engines.risk_engine.engine import RiskEngine
            from app.models.verification import VerificationRequest, VerificationResult
            from app.models.risk import RiskScore, RiskFactor
            from app.models.job import ProcessingJob
            from app.services.audit_service import AuditService, AuditAction, AuditCategory

            audit = AuditService(db)
            doc_repo = DocumentRepository(db)
            bid_repo = BidRepository(db)

            # 1. Process attached documents
            docs = await doc_repo.get_by_entity("bid", bid_id)
            orchestrator = PipelineOrchestratorService(db)
            for d in docs:
                await orchestrator.process_document(d.id)

            # 2. Run auto verification
            bid = await bid_repo.get_by_id(bid_id)
            if bid:
                from app.repositories.bidders import BidderRepository
                bidder = await BidderRepository(db).get_by_id(bid.bidder_id) if bid.bidder_id else None
                if bidder:
                    if bidder.gstin:
                        res = await MockGSTProvider().verify(bidder.gstin)
                        v_req = VerificationRequest(bid_id=bid_id, bidder_id=bid.bidder_id, provider="GST", queried_identifier=bidder.gstin)
                        db.add(v_req)
                        await db.flush()
                        v_res = VerificationResult(
                            request_id=v_req.id, bid_id=bid_id, bidder_id=bid.bidder_id, source=res.source,
                            provider=res.provider, queried_identifier=res.queried_identifier,
                            status=res.status.value, is_unavailable=res.is_unavailable, returned_data=res.data,
                            checked_at=res.checked_at, authorization_context=res.authorization_context,
                            confidence=res.confidence, is_mock=True, is_demo=True,
                        )
                        db.add(v_res)
                    if bidder.pan:
                        res = await MockPANProvider().verify(bidder.pan)
                        v_req = VerificationRequest(bid_id=bid_id, bidder_id=bid.bidder_id, provider="PAN", queried_identifier=bidder.pan)
                        db.add(v_req)
                        await db.flush()
                        v_res = VerificationResult(
                            request_id=v_req.id, bid_id=bid_id, bidder_id=bid.bidder_id, source=res.source,
                            provider=res.provider, queried_identifier=res.queried_identifier,
                            status=res.status.value, is_unavailable=res.is_unavailable, returned_data=res.data,
                            checked_at=res.checked_at, authorization_context=res.authorization_context,
                            confidence=res.confidence, is_mock=True, is_demo=True,
                        )
                        db.add(v_res)
                    await db.flush()

            # 3. Compliance evaluation
            if bid:
                req_repo = TenderRequirementRepository(db)
                reqs = await req_repo.get_approved_rules(bid.tender_id)
                if reqs:
                    c_engine = ComplianceEngine()
                    rule_defs = [r.rule_definition for r in reqs if r.rule_definition]
                    comp_summary = c_engine.evaluate_all_rules(rule_defs, {})
                    bid.compliance_result = comp_summary["overall_result"]
                    bid.compliance_summary = comp_summary
                    bid.status = "COMPLIANCE_EVALUATED"
                    await db.flush()

            # 4. Risk evaluation
            if bid:
                r_engine = RiskEngine()
                risk_res = r_engine.compute_risk(
                    compliance_data=bid.compliance_summary or {},
                    document_data={}, verification_data={}, graph_data={}, behaviour_data={},
                )
                r_score = RiskScore(
                    bid_id=bid_id, compliance_score=risk_res.compliance_score,
                    document_integrity_score=risk_res.document_integrity_score,
                    verification_risk_score=risk_res.verification_risk_score,
                    graph_risk_score=risk_res.graph_risk_score,
                    behaviour_risk_score=risk_res.behaviour_risk_score,
                    overall_risk_score=risk_res.overall_risk_score, risk_level=risk_res.risk_level,
                    weights_used=risk_res.weights_used, explanation=risk_res.explanation,
                )
                db.add(r_score)
                bid.overall_risk_score = risk_res.overall_risk_score
                bid.risk_level = risk_res.risk_level
                bid.status = "RISK_CALCULATED"

            # 5. Mark job completed
            from sqlalchemy import update
            await db.execute(
                update(ProcessingJob)
                .where(ProcessingJob.id == job_id)
                .values(status="COMPLETED", progress=100, completed_at=datetime.now(UTC))
            )
            await db.commit()
            logger.info("analyze_bid_task_complete", bid_id=bid_id)
        except Exception as exc:
            logger.error("analyze_bid_task_failed", bid_id=bid_id, error=str(exc), exc_info=True)
            from app.models.job import ProcessingJob
            from sqlalchemy import update
            await db.execute(
                update(ProcessingJob)
                .where(ProcessingJob.id == job_id)
                .values(status="FAILED", error_message=str(exc), completed_at=datetime.now(UTC))
            )
            await db.commit()
