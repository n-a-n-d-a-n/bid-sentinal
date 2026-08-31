# Decision Governance Rules

## Primary Principle
The AI/ML system is purely advisory. The **Procurement Officer** retains complete legal decision authority.

## Governance Directives
1. **System Recommendation vs Officer Decision**: API and UI strictly separate `system_recommendation` from `officer_decision`.
2. **Explicit Overrides**: If an officer approves a bid recommended for `BLOCKED` or `MANUAL_REVIEW_REQUIRED`, the system records `override = True` and requires an `override_reason`.
3. **Immutable Decision Snapshots**: At decision time, an immutable snapshot of evidence, risk, compliance, and model versions is frozen.
