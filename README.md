# Real-Time SUS Vaccination Lakehouse

> **Does every municipality reach its vaccination targets — and register doses on time?**
> A bronze/silver/gold lakehouse on public Brazilian health data (SUS / SI-PNI), with batch
> and simulated real-time ingestion in PySpark + Delta Lake, data contracts, quality gates,
> partition-skew analysis, catalog and lineage.

![Status](https://img.shields.io/badge/status-planning-lightgrey)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Spark](https://img.shields.io/badge/Apache%20Spark-4.x-orange)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-4.x-00ADD4)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## The problem

Brazil's public health system (SUS) registers every vaccine dose applied in the country.
Municipalities are accountable for reaching the National Immunisation Programme (PNI)
coverage targets and for registering doses promptly — but the open data is large, messy
and arrives late: duplicates, invalid codes, two municipality-code formats, and doses that
reach the national system days or weeks after they were applied.

## What this project builds

```mermaid
flowchart LR
    SRC["OpenDataSUS<br/>SI-PNI records"] -->|batch backfill| B["Bronze<br/>raw Delta"]
    SRC -->|"replayed as a<br/>live event feed"| B
    B -->|"validate · dedupe · MERGE<br/>watermark late data"| S["Silver<br/>one row per dose"]
    S -->|"Change Data Feed<br/>(incremental)"| G["Gold<br/>coverage · dropout ·<br/>timeliness · real-time"]
    G --> D["Accountability<br/>dashboard"]
```

- **Batch + streaming with one engine** — Spark Structured Streaming, `availableNow` for backfill, micro-batches for the live feed
- **Incremental and idempotent** — checkpoints, Delta MERGE, idempotent stream writes, re-runs change nothing
- **Data contracts** (ODCS) → schemas, quality rules and docs generated from one source of truth
- **Quality gates** with Great Expectations — completeness, validity, uniqueness at every layer
- **Partitioning & skew** — São Paulo vs Espírito Santo as a real skew case, measured in the Spark UI
- **Catalog & lineage** — OpenLineage events, Delta history as audit trail, LGPD-aware publishing

## Status

🚧 **Planning complete, implementation starting.** The full design lives in [`docs/`](docs/):

- [Architecture](docs/ARCHITECTURE.md) — design and market-standard conventions per technology
- [Backlog](docs/README.md) — 12 features, 63 tasks
- [Architecture Decision Records](docs/adr/)

## Data

Public, anonymised data from the Brazilian Ministry of Health (OpenDataSUS — SI-PNI),
IBGE and SINASC. No raw records are stored in this repository. See
[ADR-0003](docs/adr/0003-public-sus-vaccination-data.md).

## License

Code: [MIT](LICENSE). Data remains under the terms of its original publishers.
