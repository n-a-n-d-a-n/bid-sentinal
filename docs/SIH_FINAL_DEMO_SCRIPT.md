# PROCUREX SIH Final 5-Minute Evaluator Demonstration Script

## Overview
Recommended demonstration script for Smart India Hackathon evaluators.

## 5-Minute Demonstration Walkthrough

### 00:00 - 00:30 | Overview & Pre-Flight Readiness
- Open `http://localhost:3000/demo`.
- Click **"Run Pre-flight Check"**.
- Verify status: Backend, Database, Redis, MinIO, IsolationForest Model, Policy RAG, 23 Scenarios all `READY`.

### 00:30 - 01:30 | Requirement Intelligence & Document Evidence
- Open Bid Investigation Workspace (`/bids/bid-demo-s`).
- Show Extracted Field Provenance: Turnover ₹3.2 Crore extracted from PDF (Page 7).
- Show Deterministic Requirement Evaluation: Tender Turnover requirement >= ₹5.0 Crore triggers `MANUAL_REVIEW_REQUIRED`.

### 01:30 - 02:30 | Verification & Cytoscape Graph Intelligence
- Show Government Verification Adapters (GST, MCA, PAN verified `VERIFIED`).
- Open **Network Graph Tab**: Demonstrate Cytoscape.js interactive entity graph.
- Highlight neutral signal warning: *"Potential shared-control relationship detected: Shared Corporate Director."*

### 02:30 - 03:30 | Policy Copilot Demonstration
- Open **Policy Copilot Tab**.
- Ask: *"What does GFR Rule 149 say about GeM procurement?"*
- Show response with verifiable citations (`[Source: GFR 2017 | Section: Rule 149 | Page: 82]`).
- Demonstrate strict abstention (`INSUFFICIENT_EVIDENCE`) for out-of-corpus queries.

### 03:30 - 04:30 | Officer Override Governance (WOW Scenario S)
- Open **Decision Center Tab**.
- System Recommendation: `MANUAL_REVIEW_REQUIRED`.
- Officer selects `APPROVE` based on supplementary evidence.
- System displays mandatory written justification form & override alert.
- Submit decision -> System records `is_override = True` and signs decision into SHA-256 audit ledger.

### 04:30 - 05:00 | Tamper-Evident Audit Ledger (WOW Scenario W)
- Open **Audit Ledger Tab** (`/audit`).
- Show valid SHA-256 hash chain (`status: VALID`).
- Click **"Re-Verify Chain Integrity"** to verify audit events.
- Conclude: **Verify. Explain. Detect. Decide.**
