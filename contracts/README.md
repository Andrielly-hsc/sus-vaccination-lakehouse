# Data contracts

Each file here is a **data contract** in the [Open Data Contract Standard (ODCS) v3.2.0](https://bitol-io.github.io/open-data-contract-standard/)
([ADR-0006](../docs/adr/0006-odcs-data-contracts.md)). A contract is the agreement between whoever
produces a table and whoever consumes it: the schema, what each column means, which values are
valid, how fresh the data is and who owns it. It is the **single source of truth**: Spark schemas,
Great Expectations suites, table comments and catalog pages are generated from these files
(F02-T05, F07, F09), never written by hand.

## Layout

| Folder | Describes | Status |
|---|---|---|
| `source/` | External data we do not control (OpenDataSUS, IBGE) — what we *expect* to receive | `active` |
| `bronze/` | Raw copies in the lakehouse: source columns as strings + ingestion metadata | `proposed` until built |
| `silver/` | Cleaned, typed, conformed tables | `proposed` until built |
| `gold/` | Star schema, indicators and real-time aggregates | `proposed` until built |
| `schema/` | The official ODCS JSON Schema (Apache-2.0, © The Bitol Contributors), used by the validator | — |

One file per table, `<layer>/<table>.odcs.yaml`. Closely related tables that are always built
together share a file with several schema objects (gold dimensions, gold indicators, bronze seeds).
The event-stream contract (`bronze/sipni_dose_events_raw`) is written in F04-T01.

## ODCS subset we use

| Section | Use in this project |
|---|---|
| Fundamentals | `apiVersion: v3.2.0`, `kind: DataContract`, `id`, `name`, `version`, `status`, `domain: public-health-immunisation`, `dataProduct: sus-vaccination-lakehouse`, `description.purpose/usage/limitations` |
| `servers` | Where the data lives: `s3`/`api` for sources, `local` (Delta on disk) for lakehouse tables |
| `schema` | One object per table with `physicalName` (`layer.table`), `dataGranularityDescription` (the grain) and `properties` |
| Property fields | `logicalType`, `physicalType` (Spark type), `required`, `unique`, `primaryKey`, `partitioned`, `classification`, `criticalDataElement`, `description`, `examples`, `enum`, `transformSourceObjects` / `transformLogic` (column lineage) |
| `quality` | Library metrics (`nullValues`, `missingValues`, `invalidValues`, `duplicateValues`, `rowCount`) and `sql` rules; `dimension` and `severity` set on every rule |
| `slaProperties` | `frequency`, `latency`, `retention` |
| `team`, `support` | Owner and where to report problems |
| `customProperties` | `layer` (required, equals the folder) and project-specific metadata |

Not used: pricing, roles (single-user project; access control is discussed in F09).

## Conventions

| Topic | Rule |
|---|---|
| `id` | `vaxlake-<layer>-<table>` (no dots: ODCS ids cannot contain them) |
| `physicalName` | `<layer>.<table>` for lakehouse tables |
| Names | English `snake_case`; bronze keeps the **source** names unchanged |
| Keys | Silver and gold objects declare a `primaryKey`; bronze is append-only and has none |
| `classification` | Privacy class from the [data dictionary](../docs/data/data_dictionary.md#1-how-to-read-this-dictionary): `id`, `pseudonym`, `quasi`, `sensitive`, `org`, `operational`, plus `aggregate` (gold counts) and `technical` (metadata columns) |
| `severity` | `error` = blocks the pipeline (critical); `warning` = reported only |
| Placeholders in SQL rules | `${object}` is the table being checked |

## Versioning (Semantic Versioning)

| Change | Version bump | Example |
|---|---|---|
| Remove, rename or retype a column; make a column required; tighten a rule | **major** (breaking) | `1.4.2 → 2.0.0` |
| Add a nullable column; add a rule with `severity: warning` | minor | `1.4.2 → 1.5.0` |
| Descriptions, examples, typos | patch | `1.4.2 → 1.4.3` |

Lakehouse contracts start at `0.1.0` (`status: proposed`) and become `1.0.0` (`status: active`)
when the table is first built and tested. CI rejects breaking changes without a major bump (F02-T05).

## Validate

```bash
python scripts/validate_contracts.py
```

Runs the official JSON Schema plus the conventions above; also executed by `pytest`
(`tests/unit/test_contracts_valid.py`), so CI fails on an invalid contract.
