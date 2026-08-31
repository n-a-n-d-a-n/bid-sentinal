# AI & ML Model Governance Rules

## Core Governance Directive
AI and ML models in PROCUREX are strictly **advisory** intelligence tools.

## Mandatory Rules
1. **No Autonomous Disqualification**: AI/ML models MUST NEVER autonomously make final legal qualification or disqualification decisions.
2. **Neutral Language**: Models must use neutral, objective terminology (`PROCUREMENT ANOMALY SCORE`, `Potential shared-control relationship`). Never use accusatory words like `fraud`, `collusion`, or `guilty`.
3. **No Black-Box Scoring**: Every anomaly score or risk score must be accompanied by explicit, evidence-backed explanations.
4. **Deterministic Compliance**: Arithmetic, dates, numeric thresholds, and compliance rules are evaluated by deterministic Python code, never by an LLM or ML model.
5. **UNAVAILABLE ≠ PASS**: API timeouts, unavailability, or missing documents can NEVER be automatically converted into a PASS status.
