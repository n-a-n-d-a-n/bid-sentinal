# Procurement Anomaly Detection Engine

## Overview
Unsupervised anomaly detection using `scikit-learn` IsolationForest.

## Features Extracted
1. `bid_count`
2. `win_rate`
3. `shared_address_count`
4. `shared_director_count`
5. `shared_bank_account_count`
6. `verification_mismatch_count`
7. `document_contradiction_count`
8. `compliance_failure_count`
9. `network_centrality`

## Output
- `anomaly_score`: 0.0 to 1.0 (Advisory)
- `contributing_signals`: Top contributing factors explaining score.
