# F10-T04 — End-to-end CI job

| Field | Value |
|---|---|
| **Feature** | [F10 — Pipeline orchestration & operations](../features/F10-orchestration-and-operations.md) |
| **Status** | To Do |
| **Estimate** | 2 h |
| **Depends on** | [F10-T03](F10-T03-run-log-and-observability.md), [F07-T03](F07-T03-quality-gates-in-pipeline.md) |
| **Branch** | `feat/F10-T04-end-to-end-ci` |

## Description

Run the whole pipeline on fixtures in CI, twice, plus the streaming path.

## Steps

1. Job `e2e`: run-all on `ci` profile; replay + stream with `availableNow`
2. Second run; assert gold tables identical (content hash)
3. Upload GX results and run log as CI artefacts

## Acceptance criteria

- [ ] E2E job green and under ~10 minutes

## Deliverables

- `.github/workflows/ci.yml (e2e job)`

## Why this matters (best practice)

Unit tests prove parts; an end-to-end idempotency check proves the system. Artefacts make CI failures debuggable without re-running locally.

## Notes

_Add decisions, problems found and links to the PR here while working._
