# F09-T01 — Register tables in the catalog

| Field | Value |
|---|---|
| **Feature** | [F09 — Catalog, lineage & governance](../features/F09-catalog-lineage-governance.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F06-T01](F06-T01-gold-dimensional-model.md) |
| **Branch** | `feat/F09-T01-metastore-catalog` |

## Description

Databases `bronze`, `silver`, `gold`, `ops` with table and column comments from contracts.

## Steps

1. Local metastore location from config
2. `register_tables()` creating/altering tables with `COMMENT` and `TBLPROPERTIES` (owner, layer, contract_version, classification)
3. Test that comments match contracts

## Acceptance criteria

- [ ] `DESCRIBE TABLE EXTENDED` shows descriptions and properties for every table

## Deliverables

- `src/vaccination_lakehouse/governance/catalog.py`

## Why this matters (best practice)

Three-level names (`catalog.schema.table`) and metadata on the table itself are how Unity Catalog and Fabric expose data to users. Metadata that lives with the data does not go stale in a wiki.

## Notes

_Add decisions, problems found and links to the PR here while working._
