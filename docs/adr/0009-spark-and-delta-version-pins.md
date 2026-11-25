# ADR-0009: Pin Spark 4.1 with Delta Lake 4.4

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

Delta Lake ships a JAR built against specific Spark versions, so Spark and Delta cannot be upgraded independently. Other libraries add constraints too. At the time of writing (versions on PyPI):

| Library | Latest | Constraint |
|---|---|---|
| `pyspark` | 4.3.0 | — |
| `delta-spark` | 4.4.1 | requires `pyspark>=4.0.1,<=4.2.0`; publishes JARs for Spark 4.1 and 4.2 (`io.delta:delta-spark_4.1_2.13`, `…_4.2_2.13`) |
| `great-expectations` 1.25 (Spark extra) | — | requires `pyspark<4.2` |

Since Delta 4.1 the Maven artifact name carries the Spark minor version, and `configure_spark_with_delta_pip()` picks it from the installed `pyspark` version.

## Decision

We will use **PySpark 4.1.x** (4.1.4 locked) with **delta-spark 4.4.x** (4.4.1 locked), Scala 2.13, on **Java 17**. `pyproject.toml` declares `pyspark>=4.1,<4.2` and `delta-spark>=4.4,<4.5`; exact versions are in `requirements-lock.txt`.

## Consequences

- + Newest Delta features available for Spark 4.1, while staying compatible with Great Expectations (F07)
- + One rule to remember: upgrade Spark and Delta together, after checking the [Delta compatibility table](https://docs.delta.io/releases/)
- − Not on the newest Spark (4.3); revisit when Great Expectations supports Spark ≥ 4.2
