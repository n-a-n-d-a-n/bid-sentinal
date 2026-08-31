# PROCUREX — SIH 5-Minute Evaluator Demonstration Runbook

## Overview
Recommended step-by-step walkthrough for Smart India Hackathon evaluators to demonstrate PROCUREX capabilities in 5 minutes.

## 5-Minute Sequence

### 00:00 - 00:30 | Health & System Status
- Call `GET /api/v1/demo/health`
- Show status: Database, Redis, MinIO, IsolationForest Model, Policy Corpus all `READY`.

### 00:30 - 01:30 | Scenario S Demo (The "WOW" Scenario)
- Call `POST /api/v1/demo/scenarios/S/run`
- Demonstrate:
  - **Document Evidence**: Financial turnover ₹3.2 Crore.
  - **Tender Requirement**: Turnover >= ₹5.0 Crore.
  - **Government Verification**: GST & PAN verified (`VERIFIED_MATCH`).
  - **Network Graph**: Shared director signal detected.
  - **Anomaly Score**: 0.78 (Advisory alert).
  - **System Recommendation**: `MANUAL_REVIEW_REQUIRED`.
  - **Officer Action**: Officer investigates & selects `APPROVE`.
  - **Override Recording**: System records `is_override = True` with mandatory written justification.
  - **Audit Chain**: `status: VALID`.

### 01:30 - 02:30 | Policy Copilot Demonstration
- Call `POST /api/v1/policy/query` with question: *"What does GFR Rule 149 say about GeM procurement?"*
- Show structured answer with citations (`[Source: GFR 2017 | Section: Rule 149 | Page: 82]`).
- Show strict abstention by asking an out-of-corpus question. Response returns: `INSUFFICIENT_EVIDENCE`.

### 02:30 - 03:30 | Tamper-Evident Audit Ledger (Scenario W)
- Call `GET /api/v1/audit/verify`
- Show `AUDIT CHAIN: VALID`.
- Simulate payload tampering in Scenario W.
- Call `GET /api/v1/audit/verify` -> System detects tampering: `status: INVALID` with broken event ID.

### 03:30 - 05:00 | Officer Decision Workspace & Conclusion
- Call `GET /api/v1/bids/{id}/decision-history` to display complete timeline.
- Summarize PROCUREX core value: **Verify. Explain. Detect. Decide.**
