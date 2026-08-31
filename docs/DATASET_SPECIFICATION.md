# Synthetic Dataset Specification

## Overview
PROCUREX uses a synthetic dataset generator (`scripts/generate_synthetic_dataset.py`) to create realistic but fictional procurement observations across 7 populations.

## Behavioral Populations
1. `NORMAL`: Standard compliant bidding behavior.
2. `LOW_VARIATION`: Minor variances in non-mandatory fields.
3. `HIGH_PARTICIPATION`: Bidders participating across numerous tenders.
4. `NETWORK_CONCENTRATION`: Elevated shared address or director counts.
5. `VERIFICATION_INCONSISTENCY`: Identifiers returning verification mismatches.
6. `DOCUMENT_CONTRADICTION`: Financial turnover variances across documents.
7. `MIXED_SIGNAL`: Combination of network signals and requirement failures.

## Data Disclaimer
All generated records contain explicit metadata marking: `is_synthetic = True` and `disclaimer = "SYNTHETIC DEMONSTRATION DATA"`.
