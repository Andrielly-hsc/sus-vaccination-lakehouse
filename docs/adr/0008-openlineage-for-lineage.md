# ADR-0008: OpenLineage for lineage, catalog as code

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

We want table- and column-level lineage and a browsable catalog. Full catalog platforms (DataHub, OpenMetadata, Unity Catalog OSS, Microsoft Purview) need servers or cloud accounts. Lineage can instead be captured by an engine listener and stored in an open format.

## Decision

1. Capture lineage with the **OpenLineage Spark listener** (`openlineage-spark`), writing events to files (file transport) by default; **Marquez** in Docker is an optional viewer.
2. Register all tables in the **Spark catalog** (`bronze`, `silver`, `gold`, `ops` databases) with comments and table properties generated from the contracts.
3. Generate `docs/lineage.md` (Mermaid) and `docs/catalog/` from lineage events and contracts.

## Consequences

- + Open standard used by Purview, Unity Catalog, DataHub and Marquez — the events plug into any of them
- + No server needed; docs are versioned in git
- − No interactive catalog UI unless Marquez is started
- − Compatibility between `openlineage-spark` and Spark 4 must be checked when pinning versions
