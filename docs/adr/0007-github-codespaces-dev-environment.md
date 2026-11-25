# ADR-0007: GitHub Codespaces as the development environment

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The author's laptop runs Windows 11 with 8 GB RAM, without Java, Docker or WSL installed. Spark needs Java 17; on native Windows, writing Delta/Parquet also needs Hadoop's `winutils.exe`/`hadoop.dll`, a frequent source of obscure errors. Options:

| Option | Pros | Cons |
|---|---|---|
| Native Windows + winutils | No new OS layer | Fragile, unlike any production setup |
| WSL2 Ubuntu | Real Linux on the laptop; works offline | One-time install with admin rights; shares the laptop's 8 GB RAM with Windows |
| Docker Desktop | Reproducible images | Requires WSL2 anyway; heavy on 8 GB RAM |
| **GitHub Codespaces** (dev container) | Nothing to install locally; Linux VM with its own RAM; the same `devcontainer.json` works for reviewers, VS Code and CI-like reproducibility | Monthly free quota (core-hours and storage); needs internet; files live in the codespace, not on the laptop |
| Databricks Free Edition / Fabric trial | Real platform | Account required; code less portable for reviewers |

## Decision

We will develop and run the project in **GitHub Codespaces**, defined by a **dev container** (`.devcontainer/devcontainer.json`: Python 3.11 + Java 17 + project dependencies). The default machine is **2 cores / 8 GB RAM**; a 4-core machine is used only for heavier runs (full Southeast backfill, skew experiments). CI runs on Ubuntu with the same Java and Python versions. Native Windows is not supported; WSL2 remains a documented fallback because the dev container is standard and also opens locally in VS Code.

## Consequences

- + The laptop only needs a browser or VS Code; Spark gets the codespace's own memory
- + Reviewers open the repository in a Codespace and run the pipeline with zero setup — the dev container is the executable version of the setup guide
- + Development, CI and production all run on Linux
- − **Quota management is part of the job:** stop the codespace when not in use (idle timeout ≤ 30 min), prefer the 2-core machine, keep the downloaded scope small, and delete unused codespaces. Usage is checked in GitHub *Settings → Billing*
- − Data, Delta tables and checkpoints live inside the codespace (`/workspaces/…/data`, git-ignored). Deleting the codespace deletes them — acceptable because everything is reproducible from the source, but the full backfill should not be redone casually
- − Requires internet; heavy downloads from OpenDataSUS go from GitHub's servers, not the laptop
