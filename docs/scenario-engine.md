# Demo Scenario Execution Engine

## Overview
The Scenario Execution Engine powers the execution of scenarios A through W in both `FULL_RUN` and `STEP_BY_STEP` modes.

## Pipeline Architecture
- Creates an isolated `DemoExecutionContext` with a unique `demo_run_id`.
- Executes actual underlying Python engines (PyMuPDF parser, Rule/LLM extractors, Mock Verification adapters, NetworkX Graph builder, IsolationForest Anomaly model, Policy RAG retriever, Audit ledger).
- Compares Expected vs Actual outcomes deterministically.
