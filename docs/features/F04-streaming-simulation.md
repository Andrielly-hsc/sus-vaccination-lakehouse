# F04 — Real-time feed simulation & streaming bronze

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F03](F03-batch-ingestion-bronze.md) |
| **Estimate** | 15.5 h |
| **Created** | 2026-11-25 |

## Goal

Simulate the live RNDS feed from real records — with authentic late, duplicated and out-of-order events — and ingest it into bronze with exactly-once guarantees.

## User story

> As a health-surveillance analyst, I want doses to appear in the lakehouse within seconds of being sent, so that I can monitor campaigns while they happen.

## Scope

**In scope**

- Broker-agnostic event envelope contract
- Deterministic event replayer (speed factor, real lags, duplicates, disorder)
- Structured Streaming file source → bronze Delta
- Fault tolerance and restart semantics
- Streaming metrics listener
- Optional Kafka/Redpanda source (Could)

**Out of scope**

- Production message broker operations
- Sub-second latency

## Acceptance criteria

- [ ] A replay of one month lands in `bronze.sipni_dose_events_raw` with every event exactly once
- [ ] Killing and restarting the stream loses and duplicates nothing
- [ ] Streaming metrics (input rate, batch duration, watermark) are logged per micro-batch

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F04-T01](../tasks/F04-T01-event-envelope-contract.md) | Define the event envelope contract | 1.5 h | To Do |
| [F04-T02](../tasks/F04-T02-event-replayer.md) | Build the event replayer | 4 h | To Do |
| [F04-T03](../tasks/F04-T03-streaming-bronze.md) | Stream events into bronze | 3 h | To Do |
| [F04-T04](../tasks/F04-T04-fault-tolerance.md) | Prove fault tolerance and exactly-once | 2 h | To Do |
| [F04-T05](../tasks/F04-T05-streaming-monitoring.md) | Monitor streaming queries | 2 h | To Do |
| [F04-T06](../tasks/F04-T06-kafka-source-optional.md) | (Could) Kafka/Redpanda source | 3 h | To Do |

## Syllabus topics covered

- Eng 3.1 ETL/ELT; batch, full and incremental; formats; failures, reprocessing and consistency
- Eng 3.1 Formats CSV, JSON, Parquet
- 4.1 Python 3: modules, files, exceptions; modular organisation, tests, reproducibility

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
