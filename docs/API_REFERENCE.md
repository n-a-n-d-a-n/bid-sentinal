# PROCUREX REST API Reference

## Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/login` — Authenticate officer & receive JWT token.
- `GET /api/v1/auth/me` — Retrieve current user profile.

## Tenders (`/api/v1/tenders`)
- `GET /api/v1/tenders` — List all published tenders.
- `GET /api/v1/tenders/{id}` — Get tender details & normalized requirements.

## Bidders (`/api/v1/bidders`)
- `GET /api/v1/bidders` — List bidders.
- `GET /api/v1/bidders/{id}` — Get bidder profile.
- `GET /api/v1/bidders/{id}/graph` — Get bidder NetworkX entity graph.
- `GET /api/v1/bidders/{id}/anomalies` — Get bidder IsolationForest anomaly signals.

## Bids & Investigation (`/api/v1/bids`)
- `GET /api/v1/bids` — List bids.
- `GET /api/v1/bids/{id}` — Get bid workspace details.
- `GET /api/v1/bids/{id}/decision-readiness` — Get decision readiness status.
- `POST /api/v1/bids/{id}/decision` — Submit officer decision (Approve/Reject/Return/Escalate).

## Verification (`/api/v1/verification`)
- `POST /api/v1/verification/verify` — Execute government adapter verification.
- `GET /api/v1/verification/providers` — Get provider resilience status.

## Policy RAG (`/api/v1/policy`)
- `POST /api/v1/policy/query` — Ask Policy Copilot question.
- `GET /api/v1/policy/sources` — List policy sources (GFR 2017, GeM manual).

## Audit Ledger (`/api/v1/audit`)
- `GET /api/v1/audit` — List audit log events.
- `GET /api/v1/audit/verify` — Verify global audit hash chain.

## Demo Center (`/api/v1/demo`)
- `GET /api/v1/demo/scenarios` — List 23 scenarios (A-W).
- `POST /api/v1/demo/scenarios/{code}/run` — Run scenario execution engine.
- `GET /api/v1/demo/health` — Pre-flight health check.
- `POST /api/v1/demo/reset` — Reset demo environment.

## System Readiness (`/api/v1/system/readiness`)
- `GET /api/v1/system/readiness` — SIH evaluator readiness health report.
