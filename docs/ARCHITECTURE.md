# PROCUREX System Architecture

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
