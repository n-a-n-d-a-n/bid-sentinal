# PROCUREX Security Audit Report

## 1. Authentication & Role-Based Access Control (RBAC)
- Password Hashing: Password hashing with bcrypt.
- Session Tokens: JWT access tokens with strict expiration (`ACCESS_TOKEN_EXPIRE_MINUTES = 60`).
- RBAC Enforcement: Role guards (`ADMIN`, `PROCUREMENT_OFFICER`, `ANALYST`, `VIEWER`).

## 2. Document & Upload Security
- Magic Byte Verification: File headers validated (`%PDF-` for PDFs, `\xFF\xD8\xFF` for images).
- SHA-256 Checksum Deduplication: Unique file hash calculated upon ingestion.
- Upload Isolation: Uploads stored in isolated MinIO buckets.

## 3. Cryptographic Audit Hash Ledger
- SHA-256 Hash Chaining: `event_hash = SHA-256(action | entity_id | canonical_payload | timestamp | previous_hash)`.
- Automated Integrity Verification: Endpoint `GET /api/v1/audit/verify` checks hash chain continuity.

## 4. AI & Prompt Security
- Grounding Enforcement: Strict abstention (`INSUFFICIENT_EVIDENCE`) when policy context is weak.
- Prompt Injection Defense: Input sanitizer removes injection strings ("ignore instructions", "disregard previous prompts").
