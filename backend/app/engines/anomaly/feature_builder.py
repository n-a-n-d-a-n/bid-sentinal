"""
Procurement Anomaly Feature Builder.

Extracts bidder behavioural & network features for anomaly scoring:
1. bid_count
2. win_rate
3. shared_address_count
4. shared_director_count
5. shared_bank_account_count
6. verification_mismatch_count
7. document_contradiction_count
8. compliance_failure_count
9. network_centrality
"""
import structlog
from typing import Dict, Any, List

logger = structlog.get_logger(__name__)

FEATURE_NAMES = [
    "bid_count",
    "win_rate",
    "shared_address_count",
    "shared_director_count",
    "shared_bank_account_count",
    "verification_mismatch_count",
    "document_contradiction_count",
    "compliance_failure_count",
    "network_centrality",
]

class AnomalyFeatureBuilder:
    def extract_features(
        self,
        bidder_data: Dict[str, Any],
        graph_analytics_data: Dict[str, Any],
        compliance_summary: Dict[str, Any],
        contradictions: List[Dict[str, Any]],
        verifications: List[Dict[str, Any]],
    ) -> List[float]:
        bid_count = float(bidder_data.get("bid_count", 5))
        win_rate = float(bidder_data.get("win_rate", 0.20))

        signals = graph_analytics_data.get("network_signals", [])
        shared_address_count = float(sum(1 for s in signals if s.get("pattern") == "MULTIPLE_BIDDERS_SHARED_ADDRESS"))
        shared_director_count = float(sum(1 for s in signals if s.get("pattern") == "MULTIPLE_BIDDERS_SHARED_DIRECTOR"))
        shared_bank_count = float(sum(1 for s in signals if s.get("pattern") == "MULTIPLE_BIDDERS_SHARED_BANK_ACCOUNT"))

        verification_mismatch_count = float(sum(1 for v in verifications if v.get("status") in ("CONFLICT", "NOT_FOUND")))
        document_contradiction_count = float(len(contradictions))
        compliance_failure_count = float(compliance_summary.get("failed", 0))
        network_centrality = float(graph_analytics_data.get("nodes_count", 0)) / 10.0

        vector = [
            bid_count,
            win_rate,
            shared_address_count,
            shared_director_count,
            shared_bank_count,
            verification_mismatch_count,
            document_contradiction_count,
            compliance_failure_count,
            network_centrality,
        ]
        return vector

anomaly_feature_builder = AnomalyFeatureBuilder()
