# Government Verification Layer Architecture

## Overview
PROCUREX integrates with government databases via an adapter architecture.

## Supported Verification Providers
1. **GST** — Goods and Services Tax Network
2. **PAN** — Permanent Account Number (Income Tax Dept)
3. **MCA** — Ministry of Corporate Affairs (CIN/Directors)
4. **UDYAM** — MSME Registration
5. **EPFO** — Employees' Provident Fund Organisation
6. **ESIC** — Employees' State Insurance Corporation
7. **DigiLocker** — Document Verification
8. **BIS** — Bureau of Indian Standards
9. **GeM** — Government e-Marketplace
10. **Blacklist** — Debarment Registry

## Resilience Mechanisms
- **Circuit Breaker**: CLOSED, OPEN, HALF_OPEN states per provider.
- **Rate Limiting**: Configurable requests per minute.
- **Caching**: Verification responses cached with LIVE, CACHED, STALE tags.
- **Retries**: Exponential backoff with jitter.

## Governance Enforcement
- `UNAVAILABLE` status **NEVER** becomes `PASS`.
- All simulated provider responses are labeled `DEMO / MOCK VERIFICATION`.
