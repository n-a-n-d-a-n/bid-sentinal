# Tamper-Evident Audit Ledger

## Overview
PROCUREX implements a cryptographic append-only audit ledger with SHA-256 hash chaining.

## Hash Chain Formula
For event N:
```
previous_event_hash = hash(event N-1)  (or "GENESIS")
event_hash = SHA-256(action | entity_id | canonical_payload | timestamp | previous_event_hash)
```

## Immutability Rules
- Append-only log. No UPDATE or DELETE endpoints exist.
- Deterministic payload canonicalization prevents false integrity failures from key ordering differences.
