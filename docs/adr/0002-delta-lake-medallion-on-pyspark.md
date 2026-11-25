# ADR-0002: Medallion architecture on Delta Lake with PySpark

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

We need a processing engine and a table format that support batch and streaming with the same code, ACID upserts (for idempotent, exactly-once pipelines), time travel (audit), and that match what employers use. The target company works with **Microsoft Fabric**, whose Lakehouse is Spark + Delta tables in OneLake.

Options considered:

| Option | Pros | Cons |
|---|---|---|
| Plain Parquet + pandas/DuckDB | Simple, fast on a laptop | No ACID, no MERGE, no streaming; not the skill this project should show |
| Spark + **Apache Iceberg** | Open, engine-neutral, strong in AWS/Snowflake | Less native in Fabric/Databricks; more catalog setup locally |
| Spark + **Delta Lake** | Native in Fabric and Databricks; MERGE, Change Data Feed, time travel, streaming source/sink; works locally with `delta-spark` | Tied to the Spark ecosystem (mitigated by delta-rs readers) |

## Decision

We will use **PySpark (Spark 4.x, local mode)** with **Delta Lake** and organise tables in **bronze / silver / gold** layers as described in ARCHITECTURE.md §2.

## Consequences

- + The same code would run on Fabric or Databricks with only path/catalog changes
- + ACID MERGE and idempotent stream writes make re-runs safe
- + Change Data Feed enables incremental gold
- − Spark on a laptop is heavier than DuckDB; requires Java 17 and a Linux-like environment (ADR-0007)
- − Spark and Delta versions must be kept as a compatible pair
