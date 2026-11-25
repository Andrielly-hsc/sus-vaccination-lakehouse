"""Estimate re-identification risk of quasi-identifier combinations in SI-PNI samples.

For each combination of quasi-identifiers, counts how many records fall in an equivalence class
of size 1 (unique) or below k (default 5) — the basis of k-anonymity. Only aggregated shares
are printed.

Samples are a small fraction of the national data, so classes are smaller than in the full
data: the shares are an upper bound, useful to *compare* combinations, not absolute risk.

Usage::

    python -I scripts/discovery/reidentification_risk.py SAMPLE_CSV [...] [--k 5]
"""

from __future__ import annotations

import argparse
import collections
import csv
import sys
from pathlib import Path

#: Quasi-identifier sets to compare, from what gold could publish to what silver holds.
COMBINATIONS: dict[str, tuple[str, ...]] = {
    "municipality": ("co_municipio_paciente",),
    "municipality + sex": ("co_municipio_paciente", "tp_sexo_paciente"),
    "municipality + age": ("co_municipio_paciente", "nu_idade_paciente"),
    "municipality + age + sex": ("co_municipio_paciente", "nu_idade_paciente", "tp_sexo_paciente"),
    "municipality + month + vaccine": ("co_municipio_paciente", "_month", "co_vacina"),
    "municipality + date + age + sex": (
        "co_municipio_paciente",
        "dt_vacina",
        "nu_idade_paciente",
        "tp_sexo_paciente",
    ),
    "municipality + date + age + sex + race": (
        "co_municipio_paciente",
        "dt_vacina",
        "nu_idade_paciente",
        "tp_sexo_paciente",
        "co_raca_cor_paciente",
    ),
    "CEP prefix + date + age + sex": (
        "nu_cep_paciente",
        "dt_vacina",
        "nu_idade_paciente",
        "tp_sexo_paciente",
    ),
}


def load(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        with open(path, encoding="latin-1", newline="") as handle:
            for row in csv.DictReader(handle, delimiter=";"):
                if row.get("co_municipio_paciente"):
                    row["_month"] = row["dt_vacina"][:7]
                    rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("samples", nargs="+", type=Path)
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    rows = load(args.samples)
    print(f"{len(rows):,} records with a residence municipality; k = {args.k}\n")
    print(f"| Quasi-identifiers | classes | records unique | records in classes < {args.k} |")
    print("|---|---:|---:|---:|")
    for label, keys in COMBINATIONS.items():
        classes = collections.Counter(tuple(row[k] for k in keys) for row in rows)
        unique = sum(n for n in classes.values() if n == 1)
        small = sum(n for n in classes.values() if n < args.k)
        print(
            f"| {label} | {len(classes):,} | {unique / len(rows):.1%} | {small / len(rows):.1%} |"
        )

    infants = [r for r in rows if r["nu_idade_paciente"] == "0"]
    cells = collections.Counter(
        (r["co_municipio_paciente"], r["_month"], r["co_vacina"]) for r in infants
    )
    small_cells = sum(1 for n in cells.values() if n < args.k)
    print(
        f"\nInfants (age 0): {len(infants):,} records in {len(cells):,} cells "
        f"municipality x month x vaccine; {small_cells / len(cells):.1%} of cells have < {args.k} "
        "records in the sample."
    )


if __name__ == "__main__":
    main()
