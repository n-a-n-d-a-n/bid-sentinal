# Officer Decision Workflow

## Overview
PROCUREX implements a formal procurement officer review workflow state machine.

## Decision States
- `PENDING_REVIEW`
- `UNDER_REVIEW`
- `CLARIFICATION_REQUIRED`
- `READY_FOR_DECISION`
- `APPROVED`
- `REJECTED`
- `RETURNED`
- `ESCALATED`
- `WITHDRAWN`

## Decision Types
- `APPROVE`
- `REJECT`
- `RETURN_FOR_CLARIFICATION`
- `ESCALATE`

## Mandatory Rules
- Written justification of at least 10 characters is mandatory for all final officer decisions.
- Rejections require a structured `reason_category`.
- Invalid state transitions return HTTP 400.
