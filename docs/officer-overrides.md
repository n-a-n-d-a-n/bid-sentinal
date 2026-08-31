# Officer Overrides

## Overview
PROCUREX allows Procurement Officers to override system recommendations while enforcing full accountability.

## Override Protocol
1. System recommendation is preserved (`MANUAL_REVIEW_REQUIRED` or `BLOCKED`).
2. Officer records final decision (`APPROVED`).
3. `is_override = True` is automatically set.
4. Mandatory `override_justification` is recorded in audit ledger.
