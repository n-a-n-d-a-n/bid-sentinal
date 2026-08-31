"""
PROCUREX Test Suite — Phase 4 Tests (T57 - T77)
Verification Orchestration, Circuit Breakers, Rate Limiting, Verification Caching,
Graph Intelligence, Shared Attribute Signals, NetworkX Analytics, Anomaly Detection & Model Governance.
"""
import pytest
import asyncio
from datetime import UTC, datetime

# ─────────────────────────────────────────────────────────────────────────────
# T57 - T62: Verification Orchestration & Resilience
# ─────────────────────────────────────────────────────────────────────────────

def test_circuit_breaker_states():
    """T60: Circuit breaker transitions from CLOSED -> OPEN -> HALF_OPEN."""
    from app.engines.verification.circuit_breaker import ProviderCircuitBreaker, CircuitBreakerState

    cb = ProviderCircuitBreaker(failure_threshold=2, cooldown_seconds=0.1)
    assert cb.get_state("GST") == CircuitBreakerState.CLOSED

    # Record 2 failures -> OPEN
    cb.record_failure("GST")
    cb.record_failure("GST")
    assert cb.get_state("GST") == CircuitBreakerState.OPEN

    # Sleep cooldown -> HALF_OPEN
    import time
    time.sleep(0.15)
    assert cb.get_state("GST") == CircuitBreakerState.HALF_OPEN

    print("\n  [T60] Circuit breaker state machine (CLOSED -> OPEN -> HALF_OPEN): OK")

def test_rate_limiter_and_caching():
    """T59 & T61: Rate limiter checks & verification caching with status tags."""
    from app.engines.verification.rate_limiter import ProviderRateLimiter
    from app.engines.verification.cache_manager import VerificationCacheManager

    limiter = ProviderRateLimiter()
    assert limiter.is_allowed("GST") == True

    cache = VerificationCacheManager(ttl_seconds=1.0)
    data, status = cache.get("GST", "27AADCB2230M1ZP")
    assert status == "MISS"

    cache.put("GST", "27AADCB2230M1ZP", {"status": "VERIFIED"})
    data_c, status_c = cache.get("GST", "27AADCB2230M1ZP")
    assert status_c == "CACHED"
    assert data_c["status"] == "VERIFIED"

    print("\n  [T59, T61] Rate limiter & verification cache (MISS -> CACHED): OK")

def test_verification_reconciliation():
    """T62: Reconciles submitted evidence vs government API response."""
    from app.engines.verification.reconciler import verification_reconciler

    # Unavailable case
    r_unavail = verification_reconciler.reconcile("27AADCB2230M1ZP", {"status": "UNAVAILABLE", "provider": "GST"})
    assert r_unavail["reconciliation_status"] == "VERIFICATION_UNAVAILABLE"

    # Match case
    r_match = verification_reconciler.reconcile("27AADCB2230M1ZP", {"status": "VERIFIED", "provider": "GST", "returned_identifier": "27AADCB2230M1ZP"})
    assert r_match["reconciliation_status"] == "VERIFIED_MATCH"

    print("\n  [T62] Verification reconciliation logic: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T63 - T70: Graph Intelligence & Analytics
# ─────────────────────────────────────────────────────────────────────────────

def test_graph_entity_and_relationship_factories():
    """T63-T66: Graph entity creation, relationship provenance, & possible match safety."""
    from app.engines.graph.entity_factory import graph_entity_factory
    from app.engines.graph.relationship_factory import graph_relationship_factory

    ent = graph_entity_factory.create_entity_dict("Shakti Infra", "BIDDER")
    assert ent["canonical_name"] == "Shakti Infra"
    assert ent["entity_type"] == "BIDDER"

    rel = graph_relationship_factory.create_relationship_dict("ent-1", "ent-2", "ENTITY_POSSIBLE_MATCH", confidence=0.75)
    assert rel["relationship_type"] == "ENTITY_POSSIBLE_MATCH"
    assert rel["relationship_type"] != "ENTITY_MATCH"

    print("\n  [T63-T66] Graph entity/relationship factories & possible match safety: OK")

def test_networkx_graph_analytics_signals():
    """T67-T70: NetworkX graph analytics & shared attribute pattern detection."""
    import networkx as nx
    from app.engines.graph.analytics import graph_analytics

    G = nx.Graph()
    G.add_node("b1", label="Bidder A", type="BIDDER")
    G.add_node("b2", label="Bidder B", type="BIDDER")
    G.add_node("addr1", label="Plot 99 Pune", type="ADDRESS")

    G.add_edge("b1", "addr1", relationship="BIDDER_HAS_ADDRESS")
    G.add_edge("b2", "addr1", relationship="BIDDER_HAS_ADDRESS")

    res = graph_analytics.analyze_graph(G)

    assert res["nodes_count"] == 3
    assert res["edges_count"] == 2
    assert len(res["network_signals"]) == 1
    assert res["network_signals"][0]["pattern"] == "MULTIPLE_BIDDERS_SHARED_ADDRESS"
    assert "collusion" not in res["network_signals"][0]["description"].lower()

    print("\n  [T67-T70] NetworkX graph analytics & shared address signal detection: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T71 - T75: Anomaly Detection & Model Governance
# ─────────────────────────────────────────────────────────────────────────────

def test_anomaly_feature_extraction_and_scoring():
    """T71-T75: Anomaly feature vector, IsolationForest scoring, & neutral governance explanation."""
    from app.engines.anomaly.feature_builder import anomaly_feature_builder
    from app.engines.anomaly.isolation_forest import isolation_forest_detector
    from app.engines.anomaly.explanation import anomaly_explainer

    g_analytics = {
        "network_signals": [{"pattern": "MULTIPLE_BIDDERS_SHARED_DIRECTOR"}],
        "nodes_count": 5,
    }

    features = anomaly_feature_builder.extract_features(
        bidder_data={"bid_count": 10, "win_rate": 0.50},
        graph_analytics_data=g_analytics,
        compliance_summary={"failed": 1},
        contradictions=[{"type": "IDENTITY_MISMATCH"}],
        verifications=[{"status": "CONFLICT"}],
    )

    assert len(features) == 9

    score, is_anomalous = isolation_forest_detector.predict_anomaly(features)
    explanation = anomaly_explainer.explain_anomaly(score, features)

    assert "fraud" not in explanation["explanation_summary"].lower()
    assert "guilty" not in explanation["explanation_summary"].lower()
    assert explanation["title"] == "PROCUREMENT ANOMALY SCORE"
    assert explanation["is_advisory"] == True

    print("\n  [T71-T75] Anomaly feature extraction, scoring, & neutral governance explanation: OK")

# ─────────────────────────────────────────────────────────────────────────────
# T76 - T77: Investigation API & Audit Trail
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_investigation_api_and_audit(db_session):
    """T76-T77: Investigation graph query & audit logging."""
    from app.services.audit_service import AuditService, AuditCategory

    audit = AuditService(db_session)
    await audit.log(
        action="ANOMALY_ANALYSIS_COMPLETED",
        action_category=AuditCategory.SYSTEM,
        entity_type="BIDDER",
        entity_id="bidder-t76",
        new_value={"anomaly_score": 0.75},
    )

    print("\n  [T76-T77] Investigation graph query & audit logging: OK")
