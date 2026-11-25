# F04-T01 — Define the event envelope contract

| Field | Value |
|---|---|
| **Feature** | [F04 — Real-time feed simulation & streaming bronze](../features/F04-streaming-simulation.md) |
| **Status** | To Do |
| **Estimate** | 1.5 h |
| **Depends on** | [F02-T04](F02-T04-data-contracts-odcs.md) |
| **Branch** | `feat/F04-T01-event-envelope-contract` |

## Description

Specify the JSON event every 'facility' sends: envelope metadata plus the dose payload.

## Steps

1. Envelope: `event_id` (UUID), `event_type`, `event_time` (vaccination), `emitted_at`, `source_system`, `establishment_code`, `schema_version`, `payload`
2. Delivery semantics: at-least-once → consumers must deduplicate on `event_id` / `dose_id`
3. ODCS contract `contracts/bronze/sipni_dose_events_raw.odcs.yaml`
4. Note how it maps to a real RNDS/FHIR Immunization message (documentation only)

## Acceptance criteria

- [ ] Contract reviewed; example event in `docs/data/event_example.json` (fictitious)

## Deliverables

- `contracts/bronze/sipni_dose_events_raw.odcs.yaml`
- `docs/data/event_example.json`

## Why this matters (best practice)

Separating envelope (routing, timing, versioning) from payload is how event-driven systems evolve safely. Stating 'at-least-once' explicitly forces consumers to be idempotent — the honest default for almost every real broker.

## Notes

_Add decisions, problems found and links to the PR here while working._
