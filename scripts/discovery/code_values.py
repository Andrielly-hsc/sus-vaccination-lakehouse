"""List the code systems of a SI-PNI sample as Markdown tables (aggregated counts only).

For each code column (optionally with its description columns) prints every observed value,
its count, and flags codes that map to more than one description (an inconsistency).

Usage::

    python -I scripts/discovery/code_values.py SAMPLE_CSV [SAMPLE_CSV ...] > code_values.md
"""

from __future__ import annotations

import argparse
import collections
import csv
import sys
from pathlib import Path

#: (code column, description columns...) — only non-personal, low-cardinality code systems.
CODE_SYSTEMS: list[tuple[str, ...]] = [
    ("tp_sexo_paciente",),
    ("co_raca_cor_paciente", "no_raca_cor_paciente"),
    ("ds_nacionalidade_paciente",),
    ("co_pais_paciente", "no_pais_paciente"),
    ("co_dose_vacina", "ds_tipo_dose"),
    ("co_estrategia_vacinacao", "no_estrategia"),
    ("co_origem_registro", "ds_origem_registro"),
    ("co_local_aplicacao", "ds_local_aplicacao"),
    ("co_via_administracao", "ds_via_administracao"),
    ("co_tipo_estabelecimento", "ds_tipo_estabelecimento"),
    ("co_natureza_estabelecimento", "ds_natureza_estabelecimento"),
    ("co_condicao_maternal", "ds_condicao_maternal"),
    ("co_categoria", "ds_categoria"),
    ("st_documento",),
    ("co_sistema_origem", "ds_sistema_origem"),
    ("co_vacina", "sg_imunobiologico", "ds_nome"),
]
MAX_ROWS = 80


def read_rows(paths: list[Path]) -> tuple[list[str], list[list[str]]]:
    header: list[str] = []
    rows: list[list[str]] = []
    for path in paths:
        with open(path, encoding="latin-1", newline="") as handle:
            reader = csv.reader(handle, delimiter=";")
            header = next(reader)
            rows.extend(row for row in reader if len(row) == len(header))
    return header, rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("samples", nargs="+", type=Path)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Markdown output, whatever the console encoding
    header, rows = read_rows(args.samples)
    col = {name: i for i, name in enumerate(header)}
    print(f"_{len(rows):,} sample rows from {len(args.samples)} file(s)._\n")

    for system in CODE_SYSTEMS:
        code, *descriptions = system
        counts = collections.Counter(tuple(row[col[c]] for c in system) for row in rows)
        per_code = collections.defaultdict(set)
        for key in counts:
            per_code[key[0]].add(key[1:])
        inconsistent = sorted(c for c, d in per_code.items() if len(d) > 1)
        print(
            f"#### `{code}`"
            + (f" → {', '.join(f'`{d}`' for d in descriptions)}" if descriptions else "")
        )
        print(
            f"\n{len(per_code)} codes; "
            f"codes with more than one description: {inconsistent or 'none'}\n"
        )
        print("| " + " | ".join(system) + " | rows |")
        print("|" + "---|" * (len(system) + 1))
        for key, n in sorted(counts.items(), key=lambda kv: -kv[1])[:MAX_ROWS]:
            cells = [value if value else "*(empty)*" for value in key]
            print("| " + " | ".join(cells) + f" | {n:,} |")
        if len(counts) > MAX_ROWS:
            print(f"| … {len(counts) - MAX_ROWS} more | |")
        print()

    ages = [row[col["nu_idade_paciente"]] for row in rows]
    numeric = [int(a) for a in ages if a.isdigit()]
    print(
        f"`nu_idade_paciente`: non-numeric={len(ages) - len(numeric)}, "
        f"min={min(numeric)}, max={max(numeric)}, >120: {sum(a > 120 for a in numeric)}"
    )
    doc_ids = collections.Counter(row[col["co_documento"]] for row in rows)
    print(f"`co_documento` repeated: {sum(n > 1 for n in doc_ids.values())}")
    replaced = {row[col["co_troca_documento"]] for row in rows if row[col["co_troca_documento"]]}
    print(
        f"`co_troca_documento` pointing to a document present in the sample: "
        f"{len(replaced & set(doc_ids))} of {len(replaced)}"
    )
    for column in (
        "co_municipio_paciente",
        "co_municipio_estabelecimento",
        "co_cnes_estabelecimento",
    ):
        lengths = collections.Counter(len(row[col[column]]) for row in rows)
        print(f"`{column}` lengths: {dict(lengths)}")


if __name__ == "__main__":
    main()
