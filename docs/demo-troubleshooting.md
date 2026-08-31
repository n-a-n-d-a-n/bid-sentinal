# Demo Troubleshooting Guide

## Common Issues & Solutions

### 1. Pre-flight Health Check Failure
If `/api/v1/demo/health` returns degraded status:
- Ensure PostgreSQL & Redis containers are running: `docker compose up -d postgres redis`
- Re-run database migrations: `cd backend && alembic upgrade head`

### 2. Anomaly Model Missing
If anomaly score returns fallback values:
- Re-train IsolationForest model: `python backend/scripts/train_anomaly_model.py`

### 3. Policy RAG Corpus Empty
If policy questions return `INSUFFICIENT_EVIDENCE`:
- Re-seed policy corpus: `python backend/scripts/seed_policy_corpus.py`
