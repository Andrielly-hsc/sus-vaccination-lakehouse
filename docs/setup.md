# Development environment setup

Two ways to run the project, for two audiences ([ADR-0010](adr/0010-wsl2-for-development-dev-container-for-visitors.md)):

| Who | Environment | Section |
|---|---|---|
| The author, developing | **WSL2 Ubuntu** on the Windows laptop | [1](#1-wsl2-development-environment) |
| Visitors and reviewers | **GitHub Codespaces** (dev container, zero install) | [2](#2-github-codespaces-for-visitors) |

Both use Java 17, Python 3.11 and the same `requirements-lock.txt`; CI checks the same versions.
Native Windows is not supported (Spark needs Hadoop `winutils` there).

---

## 1. WSL2 development environment

### 1.1 Install WSL2 and Ubuntu (once, needs admin rights)

In **PowerShell as Administrator**:

```powershell
wsl --install -d Ubuntu-24.04
```

Restart Windows when asked. Ubuntu then opens and asks for a **Linux user name and password**
(they are independent from your Windows account; the password is used by `sudo`).

### 1.2 Cap WSL's memory (recommended on an 8 GB laptop)

WSL may otherwise take up to half of the RAM and keep it. Create `%UserProfile%\.wslconfig`:

```ini
[wsl2]
memory=5GB
swap=4GB
```

Apply it with `wsl --shutdown` in PowerShell (Ubuntu restarts on next use).

### 1.3 Install the project inside Ubuntu

In the Ubuntu terminal:

```bash
cd "/mnt/d/Pos_Ciencia-de-dados/Portifólio/sus-vaccination-lakehouse"
bash scripts/wsl_setup.sh
source ~/.bashrc
```

The script ([`scripts/wsl_setup.sh`](../scripts/wsl_setup.sh)) installs OpenJDK 17 and Python 3.11,
creates the virtual environment in `~/.venvs/vaxlake`, installs the locked dependencies and adds a
`vaxenv` shortcut plus `JAVA_HOME` and `VAXLAKE_PATHS__DATA_DIR` to `~/.bashrc`.

### 1.4 Check it works

```bash
vaxenv                 # activate the venv and go to the repository
java -version          # openjdk 17...
vaxlake info           # versions and active profile
pytest                 # unit + Spark tests, nothing skipped
vaxlake smoke-test     # starts Spark, writes and reads a Delta table
```

### 1.5 Where things live

| What | Where | Why |
|---|---|---|
| Code (git repository) | `D:\Pos_Ciencia-de-dados\Portifólio\sus-vaccination-lakehouse` = `/mnt/d/...` in Ubuntu | Editable from Windows (VS Code, Explorer) |
| Virtual environment | `~/.venvs/vaxlake` (Linux filesystem) | Thousands of small files: fast only on ext4 |
| Data, Delta tables, checkpoints, metastore | `~/vaxlake-data` (`VAXLAKE_PATHS__DATA_DIR`) | Spark I/O through `/mnt/d` is several times slower |
| Spark/Delta JARs | `~/.ivy2.5.2` | Downloaded once on the first Spark start |

From Windows, the Linux files are visible in Explorer at `\\wsl$\Ubuntu-24.04\home\<user>`.

### 1.6 Working rules

- **Run git on the Windows side only** (PowerShell, VS Code, GitHub Desktop). Mixing Windows and
  Linux git on the same folder creates false "file mode" changes and can break the pre-commit hook.
- Run **Spark, pytest and `vaxlake`** in Ubuntu.
- Spark UI: while a job runs, open <http://localhost:4040> in the Windows browser (WSL forwards it).
- If Windows becomes slow during a heavy run, lower `spark.driver.memory`
  (`VAXLAKE_SPARK__DRIVER_MEMORY=2g`) or close other applications.

### 1.7 Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `wsl --install` says virtualisation is disabled | Virtualisation off in BIOS/UEFI | Enable *Intel VT-x / AMD-V* in the BIOS, retry |
| `java.lang.OutOfMemoryError` / Ubuntu freezes | Driver memory too high for the WSL cap, or `collect()`/`toPandas()` on a large DataFrame | Keep driver memory ≤ 3g with `memory=5GB`; aggregate before collecting |
| First Spark start is slow | Delta JARs downloaded to `~/.ivy2.5.2` | Wait once; later starts are fast |
| `JAVA_HOME is not set` | New terminal did not load `~/.bashrc` | `source ~/.bashrc`, or re-run the setup script |
| Pipeline very slow | Data on `/mnt/d` instead of `~/vaxlake-data` | Check `echo $VAXLAKE_PATHS__DATA_DIR` |
| Tests skipped with "Java 17 not found" | Running pytest from Windows instead of Ubuntu | Run it in Ubuntu |

---

## 2. GitHub Codespaces (for visitors)

Anyone can run the project without installing anything:

1. On the repository page click **Open in GitHub Codespaces** (README badge), or
   **Code → Codespaces → Create codespace on main**. Choose the 2-core machine.
2. The dev container ([`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json))
   installs Java 17 (Temurin), Python 3.11 and the locked dependencies (`scripts/post_create.sh`).
3. In the codespace terminal: `pytest` and `vaxlake smoke-test`. The Spark UI is in the
   **PORTS** tab (port 4040).

A codespace runs on the free quota **of the person who creates it** (GitHub Free: 120 core-hours
and 15 GB-month per month at the time of writing — see
[GitHub's billing docs](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-codespaces/about-billing-for-github-codespaces)).
Stop it when finished and delete it when no longer needed; data inside it (`data/`) is lost on
deletion but can be rebuilt with the pipeline commands.

The same dev container also opens locally with Docker and VS Code (*Dev Containers: Reopen in Container*).
