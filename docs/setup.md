# Development environment setup

The project runs in **GitHub Codespaces**: a Linux virtual machine in the cloud, built from
[`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json). Nothing needs to be
installed on your own computer — a browser is enough (VS Code desktop is optional).
Why this choice: [ADR-0007](adr/0007-github-codespaces-dev-environment.md).

## 1. Create a codespace

1. On the repository page: **Code → Codespaces → Create codespace on main**
   (or a branch you are working on).
2. Machine type: **2-core** (default, enough for development). Use 4-core only for heavy runs.
3. The first build takes a few minutes. It installs Java 17 (Temurin), Python 3.11 and the
   project's locked dependencies (`scripts/post_create.sh`).
4. Check it worked, in the codespace terminal:

   ```bash
   java -version        # openjdk 17...
   python --version     # Python 3.11...
   pyspark --version    # after F01-T03
   pytest               # after F01-T06
   ```

## 2. Daily use

| Action | How |
|---|---|
| Reopen | github.com/codespaces → click the codespace (state, files and `data/` are kept) |
| **Stop** when you finish | github.com/codespaces → `…` → *Stop codespace* (or let the idle timeout stop it) |
| Open in VS Code desktop | `…` → *Open in Visual Studio Code* (needs the *GitHub Codespaces* extension) |
| Spark UI | While a Spark job runs, open the **PORTS** tab → port **4040** (“Spark UI”) |
| Dashboard | Port **8501** (“Streamlit dashboard”), from F11 |
| Rebuild after changing `.devcontainer/` | Command palette → *Codespaces: Rebuild Container* |

## 3. Managing the free quota

Personal accounts get a monthly free quota of **core-hours** and **storage** (GitHub Free: 120
core-hours and 15 GB-month at the time of writing — check
[GitHub's billing docs](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)).
A 2-core machine running for 1 hour uses 2 core-hours, so the free quota is about **60 hours
a month** on the default machine.

- Set the idle timeout to **30 minutes**: github.com/settings/codespaces → *Default idle timeout*.
- Set a **spending limit of 0** (the default for personal accounts) so you are never charged.
- **Stop** the codespace at the end of each session; **delete** codespaces you no longer use
  (storage is billed while a codespace exists, even when stopped).
- Keep the data scope small during development (`conf/dev.yaml`); the full Southeast backfill
  is done once.
- Check usage: github.com/settings/billing → *Codespaces*.

## 4. Where things live

| Path in the codespace | Content | In git? |
|---|---|---|
| `/workspaces/sus-vaccination-lakehouse` | The repository | yes |
| `…/data/landing`, `…/data/lakehouse`, `…/data/checkpoints` | Downloaded files, Delta tables, streaming state | **no** (git-ignored) |
| `~/.ivy2` | Delta / OpenLineage JARs downloaded by Spark | no |

Deleting the codespace deletes `data/`. Everything there can be rebuilt from the public
sources with the pipeline commands (see the runbook, F10).

## 5. Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `java.lang.OutOfMemoryError` / codespace freezes | Driver memory too high for 8 GB, or `collect()`/`toPandas()` on a large DataFrame | Keep `spark.driver.memory` ≤ 3g (`conf/dev.yaml`); aggregate before collecting |
| First Spark start is slow | Delta JARs are downloaded to `~/.ivy2` once | Wait; later starts are fast |
| `JAVA_HOME is not set` | Container built without the Java feature | Rebuild the container |
| "You have used your included usage" | Quota exhausted | Wait for the monthly reset; stop/delete idle codespaces |
| Port 4040 not listed | No Spark job is running (the UI exists only while a SparkSession is alive) | Start a job, or use a notebook with an open session |

## 6. Running locally instead (optional)

The same dev container works on any machine with Docker and VS Code (*Dev Containers:
Reopen in Container*), or on WSL2 Ubuntu with Java 17 and Python 3.11 installed manually.
Native Windows is not supported (Spark needs Hadoop `winutils` there).
