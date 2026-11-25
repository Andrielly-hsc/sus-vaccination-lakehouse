"""Landing zone: layout, atomic file writes and the manifest (F03-T02).

The landing zone holds files exactly as the pipeline received them. Rules:

* **Immutable** — a file is never modified after it is written; a re-published source month
  produces new files (the source ETag is part of the name) next to the old ones.
* **Atomic** — files are written under a hidden temporary name (leading ``.``) and renamed when
  complete. Spark's file source ignores names starting with ``.`` or ``_``, so a reader never
  sees a half-written file.
* **Described** — every file has a line in ``_manifest.jsonl`` (rows, SHA-256, source URL and
  version), so completeness can be checked against bronze.

Layout::

    data/landing/
      sipni/
        _manifest.jsonl
        batch/<yyyy-mm>/sipni_<yyyy-mm>_<UF>_<etag8>_part-<nnnn>.csv.gz
      reference/
        ibge_municipalities/<yyyy-mm-dd>.json
        sinasc/sinasc_<yyyy>_<etag8>.csv
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Any

MANIFEST_NAME = "_manifest.jsonl"


def sipni_dir(landing_dir: Path) -> Path:
    return landing_dir / "sipni"


def sipni_batch_dir(landing_dir: Path) -> Path:
    return sipni_dir(landing_dir) / "batch"


def reference_dir(landing_dir: Path, name: str) -> Path:
    return landing_dir / "reference" / name


def short_etag(etag: str | None) -> str:
    """First 8 hex characters of an HTTP ETag (S3 multipart ETags look like ``"abc…-106"``)."""
    cleaned = (etag or "noetag").strip('"').split("-")[0]
    return cleaned[:8]


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


@contextlib.contextmanager
def atomic_write(path: Path, mode: str = "wb") -> Iterator[IO[Any]]:
    """Write to ``.<name>.tmp`` in the same folder and rename into place on success."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    try:
        with open(tmp, mode) as handle:
            yield handle
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)  # atomic on the same filesystem
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


@dataclass(frozen=True)
class ManifestEntry:
    """One landing file (``kind='file'``) or a completed source download (``kind='source'``)."""

    kind: str
    dataset: str
    period: str
    path: str = ""
    rows: int = 0
    sha256: str = ""
    source_url: str = ""
    source_etag: str = ""
    source_last_modified: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
    recorded_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class Manifest:
    """Append-only JSON-lines manifest. Appends are small single writes, so a crash can lose
    at most the last line — never corrupt earlier ones."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def entries(self) -> list[ManifestEntry]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [ManifestEntry(**json.loads(line)) for line in lines if line.strip()]

    def append(self, *entries: ManifestEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = "".join(json.dumps(asdict(e), ensure_ascii=False) + "\n" for e in entries)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

    def completed_source(self, dataset: str, period: str) -> ManifestEntry | None:
        """Latest completed download of a source period, if any."""
        done = [e for e in self.entries() if e.kind == "source" and e.dataset == dataset]
        done = [e for e in done if e.period == period]
        return done[-1] if done else None

    def files(self, dataset: str | None = None) -> list[ManifestEntry]:
        return [e for e in self.entries() if e.kind == "file" and dataset in (None, e.dataset)]
