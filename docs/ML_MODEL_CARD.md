# ML Model Card: Procurement Anomaly Detector

## 1. Model Details
- **Model Name**: `procurement_anomaly_v1.0`
- **Model Type**: IsolationForest (Unsupervised Anomaly Detection)
- **Framework**: `scikit-learn`
- **Contamination Parameter**: 0.05 (5% synthetic anomaly target)

## 2. Intended Use & Governance
- **Primary Purpose**: Calculate an advisory **PROCUREMENT ANOMALY SCORE** to assist procurement officers during manual review.
- **Prohibited Use**: The model MUST NOT autonomously disqualify bidders or accuse entities of fraud, collusion, or guilt. Neutral signal terminology is strictly enforced throughout the platform.
- **Human Oversight**: High anomaly scores trigger `MANUAL_REVIEW_REQUIRED` state for human officer investigation.

## 3. Input Features (9 Feature Vectors)
1. `bid_count`
2. `win_rate`
3. `shared_address_count`
4. `shared_director_count`
5. `shared_bank_account_count`
6. `verification_mismatch_count`
7. `document_contradiction_count`
8. `compliance_failure_count`
9. `network_centrality`

## 4. Synthetic Data Disclosure
- **Dataset**: Trained on 1,000 synthetic observations generated via `scripts/generate_synthetic_dataset.py`.
- **Disclaimer**: SYNTHETIC DEMONSTRATION DATA FOR SIH EVALUATION ONLY.
