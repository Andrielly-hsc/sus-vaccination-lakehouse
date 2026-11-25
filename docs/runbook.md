# Runbook

How to operate the pipeline. Each section belongs to the feature that introduced it; commands
run in WSL2 Ubuntu after `vaxenv` ([setup.md](setup.md)).

## 1. Ingestion (F03)

### 1.1 Normal run

```bash
vaxlake download                 # land the configured months (conf/*.yaml scope)
vaxlake download --months 2025-04:2025-06
vaxlake reference                # IBGE, SINASC (aggregated), seeds → bronze.ref_*
vaxlake ingest                   # landing → bronze.sipni_doses_raw, then reconcile
```

Every command is **idempotent**: running it again does nothing new unless the source changed.

| Command | Skips work when… | Evidence |
|---|---|---|
| `download` | the manifest has the month with the **same ETag** and a scope that covers the UFs | `_manifest.jsonl` (`kind: source`) |
| `reference` | SINASC year has the same ETag; IBGE already downloaded today | `reference/sinasc/_manifest.jsonl` |
| `ingest` | the checkpoint already lists the file | `data/checkpoints/bronze_sipni_batch/` |

### 1.2 What "exactly once" relies on

1. **Landing is immutable** and written atomically (hidden temp name + rename). A re-published
   month gets new file names (source ETag in the name); old files stay.
2. The **checkpoint** of the file-source query lists every file already read.
3. Each micro-batch is written with **Delta idempotent writes** (`txnAppId` + `txnVersion`): if
   the process dies after the Delta commit but before the checkpoint commit, the replayed batch
   is skipped by Delta (tested in `test_crash_after_delta_commit_does_not_duplicate_on_restart`).
4. `ingest` ends with a **reconciliation**: rows per landing file in bronze = rows in the manifest.

### 1.3 Scenarios

| Situation | What to do |
|---|---|
| Download interrupted (network, laptop closed) | Run `vaxlake download` again: it resumes the `.part` file with HTTP `Range` |
| Source re-published a month (new ETag) | `vaxlake download --months YYYY-MM` lands the new version beside the old; `vaxlake ingest` appends it to bronze; silver (F05) keeps the latest version per dose |
| `ingest` crashed | Run it again; no cleanup needed |
| Header of a source file changed | `download` fails with `SourceSchemaError` before writing anything: update the source contract (new version), then the code |
| `LandingIntegrityError` (file changed after landing) | Landing must never be edited. Delete the month folder and its manifest lines, then download again |
| Reconciliation reports a mismatch | Inspect `_corrupt_record` and the file; run `vaxlake ingest --full-refresh` after fixing the cause |
| Need to rebuild bronze from landing | `vaxlake ingest --full-refresh --yes` (drops the table **and** its checkpoint; landing is untouched) |

### 1.4 Never do

- Delete a checkpoint alone: the table and its checkpoint must be reset together (`--full-refresh`).
- Edit or move files inside `data/landing/`.
- Put anything from `data/` in git (P4 of the [privacy assessment](data/privacy_assessment.md)).
