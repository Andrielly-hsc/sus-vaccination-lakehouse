# ADR-0006: Data contracts in the Open Data Contract Standard (ODCS)

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

Schemas would otherwise be duplicated in Spark code, quality suites, table comments and documentation — and drift apart. We also want explicit agreements on ownership, freshness and quality between layers. Options: ad-hoc YAML (as in project 1), JSON Schema, dbt model contracts, **ODCS v3**.

## Decision

We will describe each source and table in an **ODCS v3** YAML contract under `contracts/`, and **generate** Spark schemas, GX expectations, table/column comments and catalog docs from it. Contracts are versioned with SemVer; CI rejects breaking changes without a major version bump.

## Consequences

- + One source of truth; a standard format readable by other tools (Data Contract CLI, catalogs)
- + Schema evolution becomes an explicit, reviewed decision
- − ODCS is broad; we use a documented subset
- − Small generator code to maintain
