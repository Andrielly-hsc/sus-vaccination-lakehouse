"""Sample the first lines of a CSV inside a remote ZIP without downloading the whole file.

S3 (and most HTTP servers) accept ``Range`` requests. A ZIP keeps its directory at the end,
and DEFLATE decompresses from the start, so reading the directory plus the first few MB is
enough to see the header, the encoding and thousands of sample rows.

Usage (writes ``sample_head.csv`` and ``zip_info.json`` into OUT_DIR)::

    python -I scripts/discovery/remote_zip_sample.py URL OUT_DIR --lines 50000

Discovery tool for F02-T01; the production downloader lives in the package (F03-T01).
Samples contain anonymised personal data: keep them outside the repository.
"""

from __future__ import annotations

import argparse
import io
import json
import urllib.request
import zipfile
from pathlib import Path

HEADERS = {"User-Agent": "vaccination-lakehouse-discovery/0.1"}
TIMEOUT_S = 120


class HttpRangeFile(io.RawIOBase):
    """Read-only, seekable file object backed by HTTP Range requests (cached in chunks)."""

    def __init__(self, url: str, chunk_size: int = 4 * 1024 * 1024) -> None:
        self.url, self.chunk_size, self.pos = url, chunk_size, 0
        head = urllib.request.Request(url, method="HEAD", headers=HEADERS)
        with urllib.request.urlopen(head, timeout=TIMEOUT_S) as response:
            self.size = int(response.headers["Content-Length"])
            self.last_modified = response.headers.get("Last-Modified")
            self.etag = response.headers.get("ETag")
        self._cache_start, self._cache = -1, b""
        self.bytes_fetched = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        base = {io.SEEK_SET: 0, io.SEEK_CUR: self.pos, io.SEEK_END: self.size}[whence]
        self.pos = base + offset
        return self.pos

    def _fetch(self, start: int) -> None:
        end = min(start + self.chunk_size, self.size) - 1
        request = urllib.request.Request(
            self.url, headers={**HEADERS, "Range": f"bytes={start}-{end}"}
        )
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            self._cache = response.read()
        self._cache_start = start
        self.bytes_fetched += len(self._cache)

    def readinto(self, buffer) -> int:  # type: ignore[override]
        if self.pos >= self.size:
            return 0
        if not self._cache_start <= self.pos < self._cache_start + len(self._cache):
            self._fetch(self.pos)
        offset = self.pos - self._cache_start
        data = self._cache[offset : offset + len(buffer)]
        buffer[: len(data)] = data
        self.pos += len(data)
        return len(data)


def sample(url: str, out_dir: Path, lines: int) -> dict:
    remote = HttpRangeFile(url)
    archive = zipfile.ZipFile(io.BufferedReader(remote, buffer_size=4 * 1024 * 1024))
    member = max(archive.infolist(), key=lambda info: info.file_size)
    out_dir.mkdir(parents=True, exist_ok=True)
    with archive.open(member) as source, open(out_dir / "sample_head.csv", "wb") as target:
        for number, line in enumerate(source):
            if number > lines:  # header + `lines` rows
                break
            target.write(line)
    info = {
        "url": url,
        "zip_bytes": remote.size,
        "last_modified": remote.last_modified,
        "etag": remote.etag,
        "member": member.filename,
        "member_uncompressed_bytes": member.file_size,
        "bytes_fetched": remote.bytes_fetched,
        "sampled_rows": lines,
    }
    (out_dir / "zip_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("url")
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--lines", type=int, default=50_000)
    args = parser.parse_args()
    print(json.dumps(sample(args.url, args.out_dir, args.lines), indent=2))


if __name__ == "__main__":
    main()
