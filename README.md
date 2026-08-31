# PROCUREX — AI-Powered Integrated Bid Compliance Verification & Governance Platform

> **SIH Problem Statement**: SIH26100  
> **Tagline**: Verify. Explain. Detect. Decide.

---

## Executive Summary

**PROCUREX** is a production-grade, deployment-ready procurement intelligence and decision-support platform designed for government procurement officers on the Government e-Marketplace (GeM).

The system combines intelligent document processing, PyMuPDF text extraction, Tesseract OCR, deterministic compliance rules, government verification adapters, NetworkX entity graph intelligence, IsolationForest anomaly detection, evidence-grounded Policy RAG (GFR 2017 & GeM manual), officer decision governance, and a tamper-evident SHA-256 audit ledger.

---

## Non-Negotiable Governance Directives

1. **Deterministic Rule Supremacy**: Compliance outcomes are calculated by deterministic code rules. LLMs and ML models **never** make final qualification or disqualification decisions.
2. **Strict Guardrail Logic**:
   - `UNKNOWN ≠ PASS`
   - `UNAVAILABLE ≠ PASS`
   - `LOW CONFIDENCE ≠ PASS`
   - `MISSING DOCUMENT ≠ PASS`
3. **Advisory Signal Neutrality**: Anomaly scores and network relationships are presented strictly as advisory signals using neutral terminology (*"Potential shared-control relationship detected"*). Accusatory fraud terms are prohibited.
4. **Officer Override Governance**: System recommendations and officer decisions remain distinct. Overrides require mandatory written justification.
5. **Cryptographic Auditability**: Every system event and officer decision is recorded in an append-only SHA-256 hash chain ledger.

---

## System Architecture

```
[ NEXT.JS APP ROUTER FRONTEND ]
              │ (HTTP REST / JSON)
              ▼
    [ NGINX REVERSE PROXY ]
              │
              ▼
   [ FASTAPI BACKEND API ]
    ├── AUTH / RBAC MODULE
    ├── DOCUMENT PARSER (PyMuPDF + OCR)
    ├── COMPLIANCE ENGINE (17 Requirement Types)
    ├── VERIFICATION ORCHESTRATOR (10 Gov Adapters)
    ├── GRAPH ENGINE (NetworkX Entity Centrality)
    ├── ANOMALY ENGINE (IsolationForest Detector)
    ├── POLICY RAG (GFR 2017 Vector Retriever)
    ├── DECISION WORKFLOW (State Machine + Overrides)
    └── AUDIT LEDGER (SHA-256 Hash Chain)
              │
      ┌───────┼───────────────┐
      ▼       ▼               ▼
[POSTGRESQL] [REDIS] [MINIO STORAGE]
```

---

## Key Capabilities & Features

### 1. Document Intelligence & Provenance
- Ingests procurement PDFs, audited financial statements, and certificates.
- Validates file headers via magic bytes (`%PDF-`) and calculates SHA-256 checksums.
- Extracts structured fields with 100% traceable document page provenance.

### 2. Tender Requirement Intelligence
- Normalizes requirements across 17 canonical types (`FINANCIAL`, `TURNOVER`, `TAX`, `EXPERIENCE`, `LEGAL`, `EMD`, etc.).
- Evaluates evidence using deterministic operators (`>=`, `<=`, `==`, `REQUIRED`, `EXISTS`).

### 3. Government Verification Resilience
- Orchestrates 10 government adapters (GST, MCA, PAN, Udyam, EPFO, ESIC, DigiLocker, BIS, GeM, Debarment).
- Implements Circuit Breakers, Rate Limiters, Retry logic, and Cache Managers.

### 4. Graph & Anomaly Intelligence
- Builds NetworkX entity graphs connecting bidders, directors, addresses, bank accounts, and tenders.
- Evaluates degree/betweenness centrality and flags shared attribute patterns.
- Runs an unsupervised `IsolationForest` model across 9 feature vectors to generate an advisory **PROCUREMENT ANOMALY SCORE**.

### 5. Policy Intelligence & Evidence-Grounded RAG
- Ingests GFR 2017 & GeM Procurement Manual guidelines into 384-dimensional vector embeddings.
- Provides Policy Copilot assistance with structured policy citations. Abstains (`INSUFFICIENT_EVIDENCE`) when evidence is lacking.

### 6. Officer Decision Workflow & Tamper-Evident Audit
- Formal state machine (`PENDING_REVIEW` → `UNDER_REVIEW` → `APPROVED` / `REJECTED`).
- Records officer overrides with mandatory written justifications.
- Maintains an append-only SHA-256 hash chained audit log with automated chain verification.

### 7. Interactive Demo Center (23 Scenarios A - W)
- Repeatable evaluation environment covering 23 synthetic scenarios.
- Includes **Presentation Mode** (`/demo/presentation`) for SIH evaluator demonstrations.

---

## Quick Start & Running Locally

### 1. Master Seed & Bootstrap (Backend)
```bash
# Navigate to backend
cd backend

# Execute SIH One-Command Master Bootstrap
python scripts/sih_bootstrap.py
```

### 2. Start Frontend
```bash
# Navigate to frontend
cd frontend

# Install & start dev server
npm install
npm run dev

# Open in browser: http://localhost:3000
```

### 3. Pre-Flight Health & System Readiness
```bash
# Query system readiness endpoint
curl -X GET http://localhost:8000/api/v1/system/readiness
```

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Async SQLAlchemy, PostgreSQL 16 + pgvector, Redis, MinIO, Nginx.
- **AI & Data Engines**: PyMuPDF, Tesseract OCR, NetworkX, scikit-learn (IsolationForest), Sentence-Transformers (MiniLM), Pytest.
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Cytoscape.js, Recharts, TanStack React Query, Axios, Lucide icons.

---

## License & Governance Disclosure

Developed for Smart India Hackathon (SIH26100). All demonstration data generated by the synthetic data engine is clearly marked **SYNTHETIC DEMONSTRATION DATA**.
