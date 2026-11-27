# Performance experiments

Every optimisation in this project starts with a measurement and ends with a number here
(ARCHITECTURE §6.7). Format: hypothesis → change → before/after → decision. Environment unless
stated: WSL2 Ubuntu, 8 logical cores, WSL memory 5 GB, Spark driver 3 GB, `local[*]`,
Spark 4.1.4 + Delta 4.4.1.

## Experiment 1 — slow bronze ingestion (F03, 2026-11-27)

**Symptom.** The first real `vaxlake ingest` of one month (Jan/2025, ES + SP: 2 748 844 rows,
6 gzip parts, 362 MB) took **14 min 28 s**. At that speed 24 months would take ~6 hours.

**Method.** Time each stage separately on the same files.

| Measurement | Time | Reading |
|---|---:|---|
| CSV read, `count()` (columns pruned) | 19.0 s | Reading the files is not the problem |
| Full parse of all 63 columns, Latin-1 (`noop` sink), ES only | 14.9 s | |
| Same, but decoding as UTF-8 | 5.9 s | Non-UTF-8 decoding costs ~2.5× in parsing — noted, acceptable |
| Plain Parquet write, all files, not partitioned | 92.4 s | |
| JVM garbage collection during the tests | 9.1 s | Not memory pressure |
| **Delta append, all files, partitioned by `_ingest_date`** | **604.0 s** | The bottleneck |
| Same, data-skipping statistics on 1 column instead of 32 | 500.4 s | Statistics are a minor part |
| Delta append, **not** partitioned | 73.2 s | Partitioning is the cause |
| **Delta append, partitioned, `spark.sql.maxConcurrentOutputFileWriters=4`** | **64.4 s** | **9.4× faster** |

**Cause.** For partitioned writes, Spark's default plan **sorts all rows by the partition
columns** inside each task, so that it can write one partition after another with a single open
file. Bronze writes a single `_ingest_date` per micro-batch, so the sort orders identical values
— but it still buffers 500 000 rows × 63 text columns per task in a 3 GB heap and spills to disk.
With `maxConcurrentOutputFileWriters > 0`, Spark keeps up to that many files open per task and
skips the sort when the number of partitions per task is small (here: one).

**Decision.** Keep partitioning bronze by ingestion date (useful to reprocess a load window) and
set `spark.sql.maxConcurrentOutputFileWriters: 4` in `conf/base.yaml`.

**Result.** The real job went from 14 min 28 s to 9 min 23 s — better, but far from the 64 s of
the isolated write. Something else in the job was slow: see experiment 2.

**Lesson.** "Partition the table" has a write-side cost that does not show up on small tests.
Measuring stage by stage (read → parse → write → partitioned write) found the cause in four runs
instead of guessing (the first guess, data-skipping statistics, explained only ~15 %).

## Experiment 2 — caching the micro-batch (F03, 2026-11-27)

**Symptom.** After experiment 1 the job still took 9 min 23 s, and a re-run with **no new data**
took 118 s.

**Hypothesis.** `foreachBatch` called `batch.persist()` so it could first `collect()` the list of
files in the micro-batch (to hash them) and then write the rows. Caching 2.7 M rows × 63 text
columns in a 3 GB heap spills to disk, and the batch is effectively processed twice.

**Change.** Redesign instead of tuning:

- Before the stream starts, compare the manifest with the files already in bronze and re-hash
  **only the new files** (integrity check, `verify_new_files`).
- Inside the micro-batch, take `_file_hash` from a map built from the manifest (`create_map` +
  file name): no cache, no second scan. A file missing from the manifest gets a null hash and the
  `NOT NULL` constraint of the contract rejects the write.

| Run (Jan/2025, ES + SP, 2 748 844 rows) | Before | After |
|---|---:|---:|
| Full ingestion (`--full-refresh`), end to end | 9 min 23 s | **3 min 41 s** |
| of which: pre-flight (Spark warm-up + hashing 6 new files, 362 MB) | — | 33 s |
| of which: Delta write of the micro-batch | — | 160 s |
| Re-run with nothing new (`+0 rows`) | 118 s | **74 s** |

**Side effect found by the tests.** In the crash-after-commit test, the replayed micro-batch now
reports **0 input rows**: Delta sees that `(txnAppId, txnVersion)` is already committed and skips
the write *without reading the data*. The old `collect()` had been forcing a useless read. The
test now checks that batch 1 appears in the restarted query's progress and that Delta has only
two `WRITE` commits.

**Cumulative.** 14 min 28 s → 3 min 41 s (**3.9×**) for one month; ~1.5 h instead of ~6 h for the
24-month Southeast scope.

**Still open (F08).** The idle re-run spends ~30 s reading bronze's `_source_file` column for the
pre-flight and again for the reconciliation; both could use Delta file statistics or a small
`ops` table of loaded files.
