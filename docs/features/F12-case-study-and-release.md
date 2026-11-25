# F12 — Case study documentation & release

| Field | Value |
|---|---|
| **Status** | To Do |
| **Priority** | Must (MoSCoW) |
| **Depends on** | [F08](F08-partitioning-skew-performance.md), [F09](F09-catalog-lineage-governance.md), [F10](F10-orchestration-and-operations.md), [F11](F11-accountability-dashboard.md) |
| **Estimate** | 6 h |
| **Created** | 2026-11-25 |

## Goal

Package the project as a portfolio case study a reviewer understands in five minutes, and publish v1.0.0.

## User story

> As a hiring manager at iSYS, I want to see the problem, the architecture and the results quickly, so that I can judge the candidate's data engineering skills.

## Scope

**In scope**

- README as case study (challenge, solution, results)
- Technical report with findings
- Architecture/ADR review
- Release v1.0.0 with changelog

**Out of scope**

- Translation of documentation

## Acceptance criteria

- [ ] README shows the architecture diagram, key findings and how to run in ≤ 5 commands
- [ ] All ADRs reflect the final state
- [ ] Tag `v1.0.0` and GitHub release published

## Tasks

| ID | Task | Estimate | Status |
|---|---|---|---|
| [F12-T01](../tasks/F12-T01-readme-case-study.md) | Rewrite the README as a case study | 2 h | To Do |
| [F12-T02](../tasks/F12-T02-technical-report.md) | Write the technical report | 2 h | To Do |
| [F12-T03](../tasks/F12-T03-architecture-review.md) | Review architecture and ADRs | 1 h | To Do |
| [F12-T04](../tasks/F12-T04-release-v1.md) | Release v1.0.0 | 1 h | To Do |

## Syllabus topics covered

- Ops 4.6 Communicating results and uncertainties
- Ops 4.2 Prioritisation, acceptance criteria and indicators

## Definition of Done

- All *Must* tasks are **Done** and their acceptance criteria are met
- Code merged to `main` through a Pull Request with green CI
- Documentation (README / docs) updated
- [ARCHITECTURE.md](../ARCHITECTURE.md) conventions followed (or an ADR records the deviation)
