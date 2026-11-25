# ADR-0003: Public SUS vaccination data (SI-PNI) as the data source

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The original portfolio plan used the UCI *Condition monitoring of hydraulic systems* sensor dataset. The author decided to use **real Brazilian public health data** instead, with an accountability angle (*prestação de contas*): does each municipality reach its vaccination targets and register doses on time?

The SI-PNI "doses applied" open data (OpenDataSUS) offers individual, anonymised records from 2020 onwards, published as monthly national CSV files of roughly 1.4 GB each. Records carry both the **vaccination date** (event time) and the **registration date** in the national network (processing time) — exactly the two clocks a streaming project needs.

## Decision

1. Use **SI-PNI doses applied** as the fact source, with IBGE municipalities, SINASC live births and PNI targets as reference data.
2. Default scope: **Southeast region (SP, MG, RJ, ES)**, **24 months**, configurable in `conf/`. The region is chosen *because* it is skewed (SP ≫ ES), which the partitioning feature (F08) studies.
3. Older months are loaded in batch (backfill); the most recent months are **replayed** as a simulated real-time feed (ADR-0004).
4. Coverage indicators focus on **routine childhood vaccines**, where PNI targets and SINASC denominators are well defined.

## Consequences

- + Real, messy data: duplicates, invalid codes, 6- vs 7-digit municipality codes, late registrations
- + A socially relevant story (public accountability) that is easy to explain
- + Late data comes from the real registration lag, not from an invented distribution
- − Large files: the downloader must filter while streaming; CI uses fixtures only
- − Sensitive domain (health data): requires a privacy assessment, minimisation and small-cell suppression (F02-T06)
- − External availability risk: URLs and columns may change; discovery is documented (F02-T01)
- − Project 4 of the portfolio (predictive maintenance) assumed the hydraulic dataset; its scope must be revisited before it starts
