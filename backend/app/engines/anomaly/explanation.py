"""
Anomaly Explanation Builder.

Translates numeric feature vectors and anomaly scores into explainable evidence signals.
ENFORCES MODEL GOVERNANCE:
- Neutral terminology ("PROCUREMENT ANOMALY SCORE", "Unusual behavioural pattern")
- NEVER uses black-box or accusatory language ("fraud", "collusion", "guilty")
- Always link signals back to concrete data points.
"""
from typing import List, Dict, Any

from app.engines.anomaly.feature_builder import FEATURE_NAMES

class AnomalyExplanationBuilder:
    def explain_anomaly(
        self,
        score: float,
        feature_vector: List[float],
    ) -> Dict[str, Any]:
        signals = []

        # Feature index mappings
        # 0: bid_count, 1: win_rate, 2: shared_address, 3: shared_director, 4: shared_bank, 5: verif_mismatch, 6: contradiction, 7: comp_fail
        if feature_vector[2] > 0:
            signals.append(f"Shares registered address with {int(feature_vector[2])} other bidder(s).")
        if feature_vector[3] > 0:
            signals.append(f"Shares director with {int(feature_vector[3])} other entity/entities.")
        if feature_vector[4] > 0:
            signals.append(f"Shares bank account details with {int(feature_vector[4])} other bidder(s).")
        if feature_vector[5] > 0:
            signals.append(f"Contains {int(feature_vector[5])} government API verification mismatch(es).")
        if feature_vector[6] > 0:
            signals.append(f"Contains {int(feature_vector[6])} cross-document contradiction(s).")

        if not signals:
            signals.append("Normal procurement behavioural pattern within standard baseline variance.")

        summary_text = (
            f"Procurement Anomaly Score is {score:.2f} (Advisory signal). "
            f"Key contributing signals: {'; '.join(signals)}"
        )

        return {
            "anomaly_score": score,
            "title": "PROCUREMENT ANOMALY SCORE",
            "explanation_summary": summary_text,
            "contributing_signals": signals,
            "is_advisory": True,
            "governance_note": "ML model output is advisory only. Procurement officer makes the final qualification decision.",
        }

anomaly_explainer = AnomalyExplanationBuilder()
