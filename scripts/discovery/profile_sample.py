"""Profile a sampled SI-PNI CSV: format, per-column completeness/patterns and registration lag.

Usage::

    python -I scripts/discovery/profile_sample.py SAMPLE_CSV [--encoding latin-1] [--sep ";"]

Prints a report used to write docs/data/sources.md (F02-T01). Values that could identify a
person (patient hash, CEP prefix) are only counted, never printed.
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import re
import statistics
from pathlib import Path

#: Columns whose values are never printed, only profiled.
SENSITIVE = {"co_paciente", "co_documento", "co_troca_documento", "nu_cep_paciente"}


def shape(value: str) -> str:
    """Replace letters by 'a' and digits by '9' to show the format of a value."""
    return re.sub(r"\d", "9", re.sub(r"[^\W\d_]", "a", value))[:25]


def profile(path: Path, encoding: str, sep: str) -> None:
    raw = path.read_bytes()
    crlf_lines = raw.count(b"\r\n")
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    print(f"bytes={len(raw):,} crlf_lines={crlf_lines:,} bom={has_bom}")
    try:
        raw.decode("utf-8")
        print("encoding: valid UTF-8")
    except UnicodeDecodeError as exc:
        print(f"encoding: NOT UTF-8 ({exc.reason} at byte {exc.start}); reading as {encoding}")

    with open(path, encoding=encoding, newline="") as handle:
        rows = list(csv.reader(handle, delimiter=sep))
    header, data = rows[0], rows[1:-1]  # the last line of a sample may be truncated
    data = [row for row in data if len(row) == len(header)]
    print(f"columns={len(header)} rows={len(data):,}")

    for position, name in enumerate(header):
        values = [row[position] for row in data]
        counts = collections.Counter(values)
        empty = sum(not v.strip() for v in values) / len(values)
        formats = collections.Counter(shape(v) for v in values).most_common(2)
        top = "<hidden>" if name in SENSITIVE else [(k[:30], n) for k, n in counts.most_common(3)]
        print(
            f"{name:<34} distinct={len(counts):<6} empty={empty:6.1%} formats={formats} top={top}"
        )

    col = {name: i for i, name in enumerate(header)}
    lags = [
        (
            dt.date.fromisoformat(row[col["dt_entrada_rnds"]][:10])
            - dt.date.fromisoformat(row[col["dt_vacina"]])
        ).days
        for row in data
    ]
    q = statistics.quantiles(lags, n=100)
    print(
        f"\nregistration lag (days): min={min(lags)} p50={q[49]} p90={q[89]} "
        f"p99={q[98]} max={max(lags)}"
    )
    for limit in (0, 1, 7, 30, 60):
        share = sum(0 <= lag <= limit for lag in lags) / len(lags)
        print(f"  within {limit:>2} days: {share:.1%}")
    print(f"  negative (registered before vaccination): {sum(lag < 0 for lag in lags)}")

    uf = collections.Counter(row[col["sg_uf_estabelecimento"]] for row in data)
    southeast = {k: uf[k] for k in ("SP", "MG", "RJ", "ES")}
    print(f"\nfacility UF, Southeast share={sum(southeast.values()) / len(data):.1%} {southeast}")
    lengths = collections.Counter(len(row[col["co_municipio_paciente"]]) for row in data)
    print(f"residence municipality code lengths: {dict(lengths)}")
    print(f"avg bytes per row: {len(raw) / (len(data) + 1):.0f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv", type=Path)
    parser.add_argument("--encoding", default="latin-1")
    parser.add_argument("--sep", default=";")
    args = parser.parse_args()
    profile(args.csv, args.encoding, args.sep)


if __name__ == "__main__":
    main()
