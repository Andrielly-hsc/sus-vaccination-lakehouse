# F04-T06 — (Could) Kafka/Redpanda source

| Field | Value |
|---|---|
| **Feature** | [F04 — Real-time feed simulation & streaming bronze](../features/F04-streaming-simulation.md) |
| **Status** | To Do |
| **Priority** | Could (optional) |
| **Estimate** | 3 h |
| **Depends on** | [F04-T04](F04-T04-fault-tolerance.md) |
| **Branch** | `feat/F04-T06-kafka-source-optional` |

## Description

Optional: publish replayed events to Redpanda in Docker and read them with Spark's Kafka source.

## Steps

1. `docker-compose.yml` with a single-node Redpanda
2. Replayer `--sink kafka` producing keyed by `establishment_code`
3. Bronze query with `format('kafka')`, same downstream code
4. Compare file vs Kafka semantics in an ADR

## Acceptance criteria

- [ ] Same bronze result from Kafka as from files for the same seed

## Deliverables

- `docker-compose.yml`
- `docs/adr/00xx-kafka-source.md`

## Why this matters (best practice)

Kafka is the most common streaming backbone. Keeping the envelope broker-agnostic means swapping the source is a configuration change — a good test of the architecture.

## Notes

_Add decisions, problems found and links to the PR here while working._
