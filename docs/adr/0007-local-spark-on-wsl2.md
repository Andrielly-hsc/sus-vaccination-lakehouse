# ADR-0007: Develop and run Spark on WSL2 (Codespaces as alternative)

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The author's laptop runs Windows 11 with 8 GB RAM, without Java, Docker or WSL installed. Spark needs Java 17; on native Windows, writing Delta/Parquet also needs Hadoop's `winutils.exe`/`hadoop.dll`, a frequent source of obscure errors. Options:

| Option | Pros | Cons |
|---|---|---|
| Native Windows + winutils | No new OS layer | Fragile, unlike any production setup |
| **WSL2 Ubuntu** | Real Linux, same as CI and production; light | One-time install (`wsl --install`), needs admin rights |
| Docker Desktop | Reproducible images | Requires WSL2 anyway; heavy on 8 GB RAM |
| **GitHub Codespaces** (dev container) | Zero local install, same image for everyone | Free-tier hours; 2–4 cores |
| Databricks Free Edition / Fabric trial | Real platform | Account required; code less portable for reviewers |

## Decision

We will use **WSL2 Ubuntu with Java 17 and Python 3.11** as the primary environment, and ship a **`.devcontainer`** so the project also runs in **GitHub Codespaces**. CI runs on Ubuntu. Native Windows is not supported.

## Consequences

- + Same OS family in development, CI and production
- + Reviewers can open a Codespace and run the pipeline without installing anything
- − One-time WSL2 setup (documented step by step in F01-T02)
- − Data should live inside the WSL filesystem (`~/…`), not on `/mnt/d`, for acceptable I/O speed
