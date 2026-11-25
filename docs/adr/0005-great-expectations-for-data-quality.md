# ADR-0005: Great Expectations for data quality

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The project must test completeness, validity and uniqueness at each layer, keep results over time and produce human-readable quality documentation. Candidates: **Great Expectations (GX Core)**, **Soda Core** (SodaCL YAML), hand-written PySpark checks, Delta `CHECK` constraints.

## Decision

We will use **Great Expectations Core 1.x** with Spark DataFrames, with expectation suites **generated from the data contracts** where possible, and add **Delta `CHECK` constraints** for invariants that must never be violated (e.g. `doses >= 0`).

## Consequences

- + Most widely adopted open-source data-quality framework — frequent in job descriptions
- + Data Docs give browsable quality documentation
- + Contracts remain the single source of truth for rules
- − GX's API changed substantially in 1.0; examples written for 0.x must be ignored
- − Heavier than Soda; SodaCL is a reasonable alternative and is mentioned in the docs
