"""
Risk Scoring Engine — 5-component weighted risk model.

Weights (configurable, not statutory):
    Compliance      = 30%
    Doc Integrity   = 15%
    Verification    = 15%
    Graph           = 25%
    Behaviour       = 15%

Overall = 0.30*C + 0.15*D + 0.15*V + 0.25*G + 0.15*B

All weights are configurable. Never present as statutory thresholds.
Risk scores are decision-support signals, not legal findings.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

DEFAULT_WEIGHTS = {
    "compliance": 0.30,
    "document_integrity": 0.15,
    "verification": 0.15,
    "graph": 0.25,
    "behaviour": 0.15,
}

RISK_LEVELS = [
    (80.0, "CRITICAL"),
    (60.0, "HIGH"),
    (30.0, "MEDIUM"),
    (0.0, "LOW"),
]


@dataclass
class RiskFactor:
    factor_type: str
    category: str
    description: str
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    score_contribution: float
    evidence: Optional[Dict] = None
    recommendation: Optional[str] = None


@dataclass
class RiskScoreResult:
    compliance_score: float
    document_integrity_score: float
    verification_risk_score: float
    graph_risk_score: float
    behaviour_risk_score: float
    overall_risk_score: float
    risk_level: str
    weights_used: Dict[str, float]
    factors: List[RiskFactor]
    explanation: str
    anomaly_score: Optional[float] = None
    model_version: str = "risk_engine_v1"


class RiskEngine:
    """
    Configurable weighted risk scoring engine.
    All scores are 0-100 scale (higher = more risk).
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self._validate_weights()

    def _validate_weights(self):
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Risk weights must sum to 1.0, got {total}")

    def compute_risk(
        self,
        compliance_data: Dict[str, Any],
        document_data: Dict[str, Any],
        verification_data: Dict[str, Any],
        graph_data: Dict[str, Any],
        behaviour_data: Dict[str, Any],
        anomaly_score: Optional[float] = None,
    ) -> RiskScoreResult:
        """
        Compute the full risk score from all 5 components.
        Returns explainable score with contributing factors.
        """
        factors: List[RiskFactor] = []

        # 1. Compliance Risk (0-100, higher = more non-compliant)
        c_score, c_factors = self._score_compliance(compliance_data)
        factors.extend(c_factors)

        # 2. Document Integrity Risk
        d_score, d_factors = self._score_document_integrity(document_data)
        factors.extend(d_factors)

        # 3. Verification Risk
        v_score, v_factors = self._score_verification(verification_data)
        factors.extend(v_factors)

        # 4. Graph Risk
        g_score, g_factors = self._score_graph(graph_data)
        factors.extend(g_factors)

        # 5. Behaviour Risk (includes anomaly detection output)
        b_score, b_factors = self._score_behaviour(behaviour_data, anomaly_score)
        factors.extend(b_factors)

        # Weighted overall
        overall = (
            self.weights["compliance"] * c_score
            + self.weights["document_integrity"] * d_score
            + self.weights["verification"] * v_score
            + self.weights["graph"] * g_score
            + self.weights["behaviour"] * b_score
        )
        overall = round(min(100.0, max(0.0, overall)), 2)

        risk_level = self._get_risk_level(overall)

        explanation = self._generate_explanation(
            overall, risk_level, c_score, d_score, v_score, g_score, b_score, factors
        )

        return RiskScoreResult(
            compliance_score=round(c_score, 2),
            document_integrity_score=round(d_score, 2),
            verification_risk_score=round(v_score, 2),
            graph_risk_score=round(g_score, 2),
            behaviour_risk_score=round(b_score, 2),
            overall_risk_score=overall,
            risk_level=risk_level,
            weights_used=self.weights,
            factors=factors,
            explanation=explanation,
            anomaly_score=anomaly_score,
        )

    def _score_compliance(self, data: Dict) -> tuple[float, List[RiskFactor]]:
        factors = []
        if not data:
            return 50.0, [RiskFactor("COMPLIANCE_UNKNOWN", "COMPLIANCE", "Compliance data unavailable", "MEDIUM", 50.0)]

        total = data.get("total_rules", 0)
        fails = data.get("mandatory_fails", 0)
        manual_reviews = len(data.get("warnings", []))

        if total == 0:
            return 0.0, []

        fail_rate = (fails / total) * 100
        review_penalty = min(manual_reviews * 5, 20)
        score = min(100.0, fail_rate * 2 + review_penalty)

        if fails > 0:
            factors.append(RiskFactor(
                "MANDATORY_RULE_FAIL", "COMPLIANCE",
                f"{fails} mandatory compliance rule(s) failed out of {total}",
                "HIGH" if fails > 2 else "MEDIUM",
                fail_rate * 2,
                evidence={"failed_count": fails, "total_rules": total},
                recommendation="Review failed rules and gather remediation evidence.",
            ))

        if manual_reviews > 0:
            factors.append(RiskFactor(
                "MANUAL_REVIEW_REQUIRED", "COMPLIANCE",
                f"{manual_reviews} rule(s) require manual review",
                "MEDIUM",
                review_penalty,
            ))

        return score, factors

    def _score_document_integrity(self, data: Dict) -> tuple[float, List[RiskFactor]]:
        factors = []
        if not data:
            return 20.0, []

        score = 0.0
        low_ocr_docs = data.get("low_ocr_confidence_count", 0)
        duplicate_hash = data.get("duplicate_hash_detected", False)
        missing_docs = data.get("missing_required_docs", 0)
        conflict_count = data.get("cross_doc_conflicts", 0)

        if low_ocr_docs > 0:
            penalty = min(low_ocr_docs * 15, 30)
            score += penalty
            factors.append(RiskFactor(
                "LOW_OCR_CONFIDENCE", "DOCUMENT",
                f"{low_ocr_docs} document(s) have low OCR confidence",
                "MEDIUM", penalty,
                recommendation="Request clearer document copies for manual review.",
            ))

        if duplicate_hash:
            score += 40
            factors.append(RiskFactor(
                "DUPLICATE_DOCUMENT_HASH", "DOCUMENT",
                "Duplicate document hash detected — same document submitted multiple times",
                "HIGH", 40,
                recommendation="Investigate whether duplicate submission was intentional.",
            ))

        if missing_docs > 0:
            penalty = min(missing_docs * 20, 50)
            score += penalty
            factors.append(RiskFactor(
                "MISSING_REQUIRED_DOCUMENTS", "DOCUMENT",
                f"{missing_docs} required document(s) not uploaded",
                "HIGH", penalty,
            ))

        if conflict_count > 0:
            penalty = min(conflict_count * 15, 40)
            score += penalty
            factors.append(RiskFactor(
                "CROSS_DOCUMENT_CONFLICT", "DOCUMENT",
                f"{conflict_count} field(s) show conflicting values across documents",
                "HIGH", penalty,
                recommendation="Investigate field discrepancies across submitted documents.",
            ))

        return min(100.0, score), factors

    def _score_verification(self, data: Dict) -> tuple[float, List[RiskFactor]]:
        factors = []
        if not data:
            return 30.0, []

        score = 0.0
        conflicts = data.get("conflict_count", 0)
        unavailable = data.get("unavailable_count", 0)
        not_found = data.get("not_found_count", 0)
        unauthorized = data.get("unauthorized_count", 0)

        # Conflicts are most serious
        if conflicts > 0:
            penalty = min(conflicts * 35, 70)
            score += penalty
            factors.append(RiskFactor(
                "VERIFICATION_CONFLICT", "VERIFICATION",
                f"{conflicts} government verification conflict(s) detected",
                "CRITICAL" if conflicts > 1 else "HIGH",
                penalty,
                evidence=data.get("conflict_details"),
                recommendation=(
                    "Verification conflict requires manual investigation. "
                    "Do not auto-approve. Contact relevant authority for clarification."
                ),
            ))

        # UNAVAILABLE contributes to risk but must NOT become PASS
        if unavailable > 0:
            penalty = min(unavailable * 15, 30)
            score += penalty
            factors.append(RiskFactor(
                "VERIFICATION_UNAVAILABLE", "VERIFICATION",
                f"{unavailable} government API(s) unavailable — NOT VERIFIED (cannot auto-pass)",
                "MEDIUM",
                penalty,
                recommendation="Retry verification or route to manual verification process.",
            ))

        if not_found > 0:
            penalty = min(not_found * 20, 40)
            score += penalty
            factors.append(RiskFactor(
                "IDENTIFIER_NOT_FOUND", "VERIFICATION",
                f"{not_found} identifier(s) not found in government registry",
                "HIGH",
                penalty,
            ))

        if unauthorized > 0:
            penalty = min(unauthorized * 10, 20)
            score += penalty
            factors.append(RiskFactor(
                "API_UNAUTHORIZED", "VERIFICATION",
                f"{unauthorized} verification(s) require credentials not configured — manual review needed",
                "MEDIUM",
                penalty,
            ))

        return min(100.0, score), factors

    def _score_graph(self, data: Dict) -> tuple[float, List[RiskFactor]]:
        factors = []
        if not data:
            return 10.0, []

        score = 0.0
        shared_directors = data.get("shared_director_count", 0)
        shared_addresses = data.get("shared_address_count", 0)
        cluster_size = data.get("bidding_cluster_size", 1)
        network_density = data.get("network_density", 0.0)

        if shared_directors > 0:
            penalty = min(shared_directors * 20, 60)
            score += penalty
            factors.append(RiskFactor(
                "SHARED_DIRECTORS", "GRAPH",
                f"Elevated network risk: {shared_directors} director(s) shared across bidding entities",
                "HIGH" if shared_directors > 2 else "MEDIUM",
                penalty,
                recommendation=(
                    "Potential coordinated bidding pattern — shared directorship detected. "
                    "Manual investigation recommended. This does not constitute a finding of collusion."
                ),
            ))

        if shared_addresses > 0:
            penalty = min(shared_addresses * 15, 40)
            score += penalty
            factors.append(RiskFactor(
                "SHARED_ADDRESSES", "GRAPH",
                f"Elevated network risk: {shared_addresses} address(es) shared across bidders",
                "MEDIUM",
                penalty,
                recommendation="Verify whether shared addresses represent legitimate branch offices.",
            ))

        if cluster_size > 3:
            penalty = min((cluster_size - 3) * 10, 30)
            score += penalty
            factors.append(RiskFactor(
                "LARGE_BIDDING_CLUSTER", "GRAPH",
                f"Potential coordinated bidding pattern: cluster of {cluster_size} connected entities all bidding",
                "HIGH",
                penalty,
                recommendation=(
                    "Network cluster detected. Investigate relationship structure. "
                    "This is a risk signal, not a determination of coordination."
                ),
            ))

        if network_density > 0.7:
            penalty = min(network_density * 20, 20)
            score += penalty
            factors.append(RiskFactor(
                "HIGH_NETWORK_DENSITY", "GRAPH",
                f"Elevated network connectivity: density={network_density:.2f}",
                "MEDIUM",
                penalty,
            ))

        return min(100.0, score), factors

    def _score_behaviour(
        self, data: Dict, anomaly_score: Optional[float] = None
    ) -> tuple[float, List[RiskFactor]]:
        factors = []
        if not data and anomaly_score is None:
            return 10.0, []

        score = 0.0

        if anomaly_score is not None:
            # Isolation Forest: anomaly_score from -1 to 1 (more negative = more anomalous)
            # Normalize to 0-100 risk
            normalized = max(0.0, (1.0 - anomaly_score) / 2.0 * 100)
            score += normalized * 0.6
            if normalized > 50:
                factors.append(RiskFactor(
                    "ANOMALOUS_BIDDING_BEHAVIOUR", "BEHAVIOUR",
                    f"Isolation Forest anomaly score: {anomaly_score:.3f} (normalized risk: {normalized:.1f})",
                    "HIGH" if normalized > 70 else "MEDIUM",
                    normalized * 0.6,
                    recommendation=(
                        "Anomalous bidding behaviour detected by ML model. "
                        "This is an investigative risk signal, not a determination of fraud."
                    ),
                ))

        bid_deviation = data.get("bid_price_deviation_pct", 0)
        if bid_deviation and abs(bid_deviation) > 30:
            penalty = min(abs(bid_deviation) - 30, 40)
            score += penalty
            factors.append(RiskFactor(
                "EXTREME_PRICE_DEVIATION", "BEHAVIOUR",
                f"Bid price deviates {bid_deviation:.1f}% from market average",
                "MEDIUM",
                penalty,
            ))

        win_rate = data.get("historical_win_rate", None)
        if win_rate is not None and win_rate > 0.9:
            score += 20
            factors.append(RiskFactor(
                "ABNORMAL_WIN_RATE", "BEHAVIOUR",
                f"Unusually high historical win rate: {win_rate:.0%}",
                "MEDIUM",
                20.0,
                recommendation="Review historical bid pattern for potential winner rotation.",
            ))

        return min(100.0, score), factors

    def _get_risk_level(self, score: float) -> str:
        for threshold, level in RISK_LEVELS:
            if score >= threshold:
                return level
        return "LOW"

    def _generate_explanation(
        self, overall, level, c, d, v, g, b, factors
    ) -> str:
        """Generate a human-readable, neutral-language explanation."""
        lines = [
            f"Overall Procurement Risk: {overall:.1f}/100 ({level})",
            "",
            "Component Scores:",
            f"  • Compliance Risk:         {c:.1f}/100  (weight: {self.weights['compliance']:.0%})",
            f"  • Document Integrity Risk: {d:.1f}/100  (weight: {self.weights['document_integrity']:.0%})",
            f"  • Verification Risk:       {v:.1f}/100  (weight: {self.weights['verification']:.0%})",
            f"  • Network/Graph Risk:      {g:.1f}/100  (weight: {self.weights['graph']:.0%})",
            f"  • Behaviour Risk:          {b:.1f}/100  (weight: {self.weights['behaviour']:.0%})",
            "",
            "Key Risk Factors:",
        ]
        for factor in sorted(factors, key=lambda f: f.score_contribution, reverse=True)[:5]:
            lines.append(f"  [{factor.severity}] {factor.description}")

        lines += [
            "",
            "⚠️ This risk score is a decision-support signal. The Procurement Officer",
            "   makes the final qualification/disqualification decision.",
            "   Elevated risk scores indicate areas requiring investigation,",
            "   not a determination of fraud or non-compliance.",
        ]
        return "\n".join(lines)
