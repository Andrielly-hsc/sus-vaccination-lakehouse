"""Build the vaccine and dose code seeds from SI-PNI samples.

Writes ``seeds/vaccines.csv`` and ``seeds/doses.csv`` (UTF-8, comma-separated) with every code
observed in the samples plus derived classification columns. Re-run it with newer samples when
the source starts using new codes (the silver layer warns about unknown codes, F05-T02).

Usage::

    python -I scripts/discovery/build_code_seeds.py SAMPLE_CSV [SAMPLE_CSV ...] --out seeds
"""

from __future__ import annotations

import argparse
import collections
import csv
import re
from pathlib import Path

ORDINAL = re.compile(r"^(\d)[ªº]")


def product_type(name: str) -> str:
    lowered = name.lower()
    if lowered.startswith("vacina"):
        return "vaccine"
    if lowered.startswith("soro"):
        return "serum"
    if lowered.startswith("imunoglobulina"):
        return "immunoglobulin"
    return "monoclonal_antibody" if "nirsevimab" in lowered else "other"


def dose_kind(name: str) -> tuple[str, str]:
    """Return (kind, number) for a dose description; number is '' when not applicable."""
    lowered = name.lower()
    match = ORDINAL.match(name)
    number = match.group(1) if match else ""
    if lowered.startswith(("profilaxia", "tratamento")):
        return "treatment", ""
    if "revacinação" in lowered:
        return "revaccination", number or "1"
    if "reforço" in lowered:
        return "booster", number or "1"
    if lowered == "única":
        return "single", "1"
    if lowered == "dose zero":
        return "zero", "0"
    if lowered == "dose inicial":
        return "initial", ""
    if lowered == "dose adicional":
        return "additional", ""
    if number:
        return "primary", number
    return "unspecified", ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("samples", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=Path("seeds"))
    args = parser.parse_args()

    vaccines: collections.Counter = collections.Counter()
    doses: collections.Counter = collections.Counter()
    for path in args.samples:
        with open(path, encoding="latin-1", newline="") as handle:
            for row in csv.DictReader(handle, delimiter=";"):
                vaccines[(row["co_vacina"], row["sg_imunobiologico"], row["ds_nome"])] += 1
                doses[(row["co_dose_vacina"], row["ds_tipo_dose"])] += 1

    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "vaccines.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["vaccine_code", "vaccine_acronym", "vaccine_name", "product_type"])
        for code, acronym, name in sorted(vaccines, key=lambda key: int(key[0])):
            writer.writerow([code, acronym, name, product_type(name)])

    with open(args.out / "doses.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["dose_code", "dose_name", "dose_kind", "dose_number"])
        for code, name in sorted(doses, key=lambda key: int(key[0])):
            writer.writerow([code, name, *dose_kind(name)])

    print(f"{len(vaccines)} vaccines, {len(doses)} doses written to {args.out}")


if __name__ == "__main__":
    main()
