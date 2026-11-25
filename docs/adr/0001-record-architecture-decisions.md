# ADR-0001: Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

Design choices (engine, table format, quality tool, environment) shape every task. Months later, nobody remembers *why* they were made, and reviewers of a portfolio want to see reasoning, not only results.

## Decision

We will record each significant decision as a short **Architecture Decision Record** (Michael Nygard format: context, decision, consequences) in `docs/adr/`, numbered and never deleted — a changed decision gets a new ADR that supersedes the old one.

## Consequences

- + Decisions and trade-offs are visible and reviewable in Pull Requests
- + Same practice as project 1 (lead-funnel-analytics) — consistent portfolio
- − Small writing overhead per decision
