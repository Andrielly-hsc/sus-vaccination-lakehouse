# ADR-0004: File-based streaming simulation (Kafka optional)

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

There is no public live feed of vaccination records, so one must be simulated. Options:

| Option | Pros | Cons |
|---|---|---|
| **Kafka / Redpanda** in Docker | Industry-standard message broker; offsets, partitions | Docker + broker inside an 8 GB Codespace; more moving parts in CI |
| **Azure Event Hubs / IoT Hub** | Matches Fabric/Azure | Cloud account and cost |
| **JSON files written to a landing folder** + Spark file source | Zero infrastructure; replayable; deterministic in tests; same Structured Streaming semantics (offsets = files, checkpoint, exactly-once) | Not a real broker; latency of seconds |

## Decision

We will simulate the RNDS feed with a Python **event replayer** that writes small JSON micro-batch files atomically into `data/landing/sipni/stream/`, read by **Spark Structured Streaming's file source**. The event envelope is broker-agnostic, so a Kafka source can replace the file source later (an optional *Could* task, F04-T06).

## Consequences

- + Runs anywhere, including CI, with deterministic results
- + Teaches the concepts that matter (event time, watermarks, checkpoints, idempotent sinks) without broker operations
- − Latency of seconds, not milliseconds — acceptable for near-real-time public-health monitoring
- − Kafka-specific skills (partitions, consumer groups) are only covered if the optional task is done
