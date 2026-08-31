# Audit Integrity & Verification

## Verification APIs
- `GET /api/v1/audit/verify` — Verifies global audit hash chain integrity.
- `GET /api/v1/audit/verify/{entity_type}/{entity_id}` — Verifies entity-specific audit chain integrity.

## Tamper Detection
If any historic payload, timestamp, or previous hash link is altered, the verifier returns `status: INVALID` with details of the broken event ID.
