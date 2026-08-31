"""
Risk Recalculation Service.

Provides reusable risk computation functionality triggered by APIs or background domain events
(such as automated GraphRelationship discovery).
"""
import structlog
import networkx as nx
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bid import Bid
from app.models.risk import RiskScore, RiskFactor
from app.repositories.bids import BidRepository
from app.repositories.misc import VerificationRepository, RiskRepository
from app.engines.risk_engine.engine import RiskEngine
from app.engines.anomaly.isolation_forest import isolation_forest_model
from app.services.audit_service import AuditService, AuditAction, AuditCategory

logger = structlog.get_logger(__name__)


async def recalculate_bid_risk(db: AsyncSession, bid_id: str, source: str = "SYSTEM_EVENT") -> Optional[RiskScore]:
    """
    Recalculates risk for a given bid_id and updates DB records.
    Can be triggered by direct API call or automatically when Graph relationships change.
    """
    bid_repo = BidRepository(db)
    bid = await bid_repo.get_by_id(bid_id)
    if not bid:
        logger.warning("recalculate_bid_risk_bid_not_found", bid_id=bid_id)
        return None

    compliance_data = bid.compliance_summary or {}

    doc_data = {
        "low_ocr_confidence_count": 0,
        "duplicate_hash_detected": False,
        "missing_required_docs": 0,
        "cross_doc_conflicts": 0,
    }

    v_repo = VerificationRepository(db)
    v_results = await v_repo.get_by_bid(bid_id)
    statuses = [r.status for r in v_results]
    v_data = {
        "conflict_count": statuses.count("CONFLICT"),
        "unavailable_count": statuses.count("UNAVAILABLE"),
        "not_found_count": statuses.count("NOT_FOUND"),
        "unauthorized_count": statuses.count("UNAUTHORIZED"),
        "conflict_details": [r.conflict_details for r in v_results if r.conflict_details],
    }

    # Build Graph metrics for this bid's network
    from app.engines.graph.builder import GraphBuilderService
    builder = GraphBuilderService(db)
    nx_g = await builder.export_to_networkx()

    shared_address_count = 0
    shared_director_count = 0
    centrality_score = 0.0

    if len(nx_g) > 0:
        deg_cent = nx.degree_centrality(nx_g)
        centrality_score = max(deg_cent.values()) if deg_cent else 0.0

        for u, v, d in nx_g.edges(data=True):
            rel = d.get("relationship", "")
            if rel in ("BIDDER_HAS_ADDRESS", "SHARES_ADDRESS", "SHARED_ADDRESS"):
                shared_address_count += 1
            elif rel in ("BIDDER_HAS_DIRECTOR", "SHARES_DIRECTOR", "SHARED_DIRECTOR", "DIRECTOR_OF"):
                shared_director_count += 1

    anomaly_val = isolation_forest_model.predict_anomaly_score({
        "shared_address_count": shared_address_count,
        "shared_director_count": shared_director_count,
        "verification_mismatch_count": v_data["conflict_count"],
        "degree_centrality": centrality_score,
    })

    graph_data = {
        "shared_address_count": shared_address_count,
        "shared_director_count": shared_director_count,
        "degree_centrality": centrality_score,
    }

    behaviour_data = {
        "isolation_forest_score": anomaly_val,
        "anomaly_score": anomaly_val,
    }

    engine = RiskEngine()
    result = engine.compute_risk(
        compliance_data=compliance_data,
        document_data=doc_data,
        verification_data=v_data,
        graph_data=graph_data,
        behaviour_data=behaviour_data,
    )

    risk_score = RiskScore(
        bid_id=bid_id,
        compliance_score=result.compliance_score,
        document_integrity_score=result.document_integrity_score,
        verification_risk_score=result.verification_risk_score,
        graph_risk_score=result.graph_risk_score,
        behaviour_risk_score=result.behaviour_risk_score,
        overall_risk_score=result.overall_risk_score,
        risk_level=result.risk_level,
        weights_used=result.weights_used,
        anomaly_score=result.anomaly_score,
        explanation=result.explanation,
        model_version=result.model_version,
    )
    db.add(risk_score)
    await db.flush()

    for factor in result.factors:
        rf = RiskFactor(
            risk_score_id=risk_score.id,
            factor_type=factor.factor_type,
            category=factor.category,
            description=factor.description,
            severity=factor.severity,
            score_contribution=factor.score_contribution,
            evidence=factor.evidence,
            recommendation=factor.recommendation,
        )
        db.add(rf)

    await db.flush()

    await bid_repo.update(bid, {
        "overall_risk_score": result.overall_risk_score,
        "risk_level": result.risk_level,
        "compliance_score": result.compliance_score,
        "document_integrity_score": result.document_integrity_score,
        "verification_risk_score": result.verification_risk_score,
        "graph_risk_score": result.graph_risk_score,
        "behaviour_risk_score": result.behaviour_risk_score,
        "has_anomaly": (result.anomaly_score is not None and result.anomaly_score < -0.1),
        "requires_manual_review": result.risk_level in ("HIGH", "CRITICAL"),
        "status": "RISK_CALCULATED",
    })

    audit = AuditService(db)
    await audit.log(
        AuditAction.RISK_CALCULATION,
        AuditCategory.COMPLIANCE,
        entity_type="BID",
        entity_id=bid_id,
        bid_id=bid_id,
        new_value={
            "overall_risk_score": result.overall_risk_score,
            "risk_level": result.risk_level,
        },
        model_version=result.model_version,
        source=source,
    )

    logger.info(
        "recalculate_bid_risk_complete",
        bid_id=bid_id,
        overall_score=result.overall_risk_score,
        graph_score=result.graph_risk_score,
        risk_level=result.risk_level,
    )
    return risk_score


async def recalculate_risk_for_bidder_bids(db: AsyncSession, bidder_id: str, source: str = "GRAPH_CHANGE_EVENT") -> List[str]:
    """
    Finds all active/relevant bids involving `bidder_id` and recalculates their risk scores.
    Called whenever new GraphRelationships are created for a bidder.
    """
    res = await db.execute(select(Bid).where(Bid.bidder_id == bidder_id))
    bids = res.scalars().all()
    updated_bid_ids = []
    for bid in bids:
        await recalculate_bid_risk(db, bid.id, source=source)
        updated_bid_ids.append(bid.id)
    return updated_bid_ids
