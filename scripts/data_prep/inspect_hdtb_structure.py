"""
Inspect the column structure of one HDTB .dat file.

Usage:
    python scripts/inspect_hdtb_structure.py path/to/file.dat
    python scripts/inspect_hdtb_structure.py path/to/file.dat --output output/report.txt
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import _bootstrap  # noqa: F401


import argparse
import contextlib
from pathlib import Path


INFERRED_COLUMN_NAMES = {
    0: "token_id",
    1: "token",
    2: "lemma",
    3: "coarse_pos",
    4: "fine_pos",
    5: "morph_features",
    6: "head/governor",
    7: "dependency_relation",
    8: "unknown_1",
    9: "unknown_2",
}

TOKEN_COLUMN = 1
HEAD_COLUMN = 6
DEPREL_COLUMN = 7


def read_sentences(filepath):
    """Read a tab-separated HDTB file as blank-line-separated sentences."""
    sentences = []
    current = []

    with open(filepath, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.rstrip("\n")
            if not stripped.strip():
                if current:
                    sentences.append(current)
                    current = []
                continue

            columns = stripped.split("\t")
            current.append({
                "line_number": line_number,
                "columns": columns,
            })

    if current:
        sentences.append(current)

    return sentences


def print_column_legend(max_columns):
    """Print inferred column names for the observed column count."""
    print("Column legend")
    print("-" * 80)
    for index in range(max_columns):
        name = INFERRED_COLUMN_NAMES.get(index, "unknown")
        print(f"column {index} (1-based {index + 1}): {name}")
    print()
    print(f"Token column: column {TOKEN_COLUMN} (1-based {TOKEN_COLUMN + 1})")
    print(f"Head/governor column: column {HEAD_COLUMN} (1-based {HEAD_COLUMN + 1})")
    print(f"Dependency label column: column {DEPREL_COLUMN} (1-based {DEPREL_COLUMN + 1})")
    print()


def get_column(columns, index):
    """Return a column value or an empty string if the row is short."""
    if index >= len(columns):
        return ""
    return columns[index]


def print_sentence(sentence, sentence_number):
    """Print all columns and key inferred columns for one sentence."""
    print(f"Sentence {sentence_number}")
    print("=" * 80)
    print(f"Rows: {len(sentence)}")

    for row_index, row in enumerate(sentence, start=1):
        columns = row["columns"]
        print(f"Row {row_index} | source line {row['line_number']}")
        print(f"Number of columns: {len(columns)}")
        print(f"Token: {get_column(columns, TOKEN_COLUMN)}")
        print(f"Head/governor: {get_column(columns, HEAD_COLUMN)}")
        print(f"Dependency label: {get_column(columns, DEPREL_COLUMN)}")
        print("All columns:")

        for column_index, value in enumerate(columns):
            name = INFERRED_COLUMN_NAMES.get(column_index, "unknown")
            print(f"  column {column_index} (1-based {column_index + 1}) [{name}]: {value}")

        print()


def print_report(filepath, sentence_limit):
    """Print the inspection report for one file."""
    sentences = read_sentences(filepath)

    if not sentences:
        raise SystemExit(f"No sentences found in {filepath}")

    max_columns = max(
        len(row["columns"])
        for sentence in sentences[:sentence_limit]
        for row in sentence
    )

    print(f"File: {filepath}")
    print(f"Total sentences found: {len(sentences)}")
    print()
    print_column_legend(max_columns)

    for sentence_number, sentence in enumerate(sentences[:sentence_limit], start=1):
        print_sentence(sentence, sentence_number)


def main():
    parser = argparse.ArgumentParser(
        description="Inspect column structure of one HDTB .dat file.",
    )
    parser.add_argument("dat_file", help="Path to one HDTB .dat file")
    parser.add_argument(
        "--sentences",
        type=int,
        default=5,
        help="Number of initial sentences to inspect, default: 5",
    )
    parser.add_argument(
        "--output",
        help="Optional path to save the report as Unicode text.",
    )
    args = parser.parse_args()

    filepath = Path(args.dat_file)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-16", newline="") as f:
            with contextlib.redirect_stdout(f):
                print_report(filepath, args.sentences)
        print(f"Saved HDTB structure report to: {output_path}")
    else:
        print_report(filepath, args.sentences)


if __name__ == "__main__":
    main()
