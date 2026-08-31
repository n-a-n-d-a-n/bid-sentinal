"""
IsolationForest Anomaly Detector Wrapper.

Uses scikit-learn IsolationForest for unsupervised anomaly detection.
Outputs:
- anomaly_score (0.0 to 1.0, higher = more anomalous)
- model_version
- is_anomalous (boolean flag)
"""
import structlog
from typing import List, Dict, Any, Tuple
import numpy as np

logger = structlog.get_logger(__name__)

class IsolationForestDetector:
    def __init__(self, contamination: float = 0.1):
        self.model_version = "isolation_forest_v1.0"
        self.contamination = contamination
        self._model = None
        self._init_fallback_model()

    def _init_fallback_model(self):
        try:
            from sklearn.ensemble import IsolationForest
            # Pre-fit on dummy synthetic baseline dataset
            X_dummy = np.array([
                [5, 0.20, 0, 0, 0, 0, 0, 0, 0.2],
                [3, 0.10, 0, 0, 0, 0, 0, 0, 0.1],
                [8, 0.25, 0, 0, 0, 0, 0, 0, 0.3],
                [15, 0.80, 2, 2, 1, 3, 4, 2, 0.9], # anomalous row
            ])
            self._model = IsolationForest(contamination=self.contamination, random_state=42)
            self._model.fit(X_dummy)
        except Exception as exc:
            logger.warning("scikit_learn_init_warning", error=str(exc))
            self._model = None

    def predict_anomaly(self, feature_vector: List[float]) -> Tuple[float, bool]:
        """
        Returns: (anomaly_score, is_anomalous)
        anomaly_score is normalized in [0.0, 1.0].
        """
        if not self._model:
            # Deterministic heuristic fallback if sklearn is missing
            sum_risk = feature_vector[2] + feature_vector[3] + feature_vector[4] + feature_vector[5] + feature_vector[6]
            score = min(1.0, round(sum_risk / 5.0, 2))
            return score, (score > 0.6)

        try:
            X = np.array([feature_vector])
            raw_score = float(self._model.score_samples(X)[0])  # Negative score: smaller = more anomalous
            # Convert raw score to 0.0 - 1.0 scale
            normalized_score = round(min(1.0, max(0.0, 0.5 - raw_score)), 2)
            is_anomalous = bool(normalized_score > 0.60)
            return normalized_score, is_anomalous
        except Exception as exc:
            logger.warning("isolation_forest_prediction_failed", error=str(exc))
            return 0.20, False

isolation_forest_detector = IsolationForestDetector()
