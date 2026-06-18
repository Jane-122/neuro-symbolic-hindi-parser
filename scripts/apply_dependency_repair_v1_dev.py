"""
Apply dependency-label repair v1 to the Stanza dev corrected-v2 output.
"""

import csv
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = PROJECT_ROOT / "src" / "pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

from dependency_repair_v1 import apply_dependency_repair


INPUT_PATH = Path("results/stanza_dev_corrected_v2_all.csv")
OUTPUT_PATH = Path("results/stanza_dev_dependency_repaired_v1_all.csv")

APPENDED_FIELDS = [
    "corrected_deprel",
    "dependency_repair_applied",
    "dependency_repair_rule_id",
    "dependency_repair_type",
]


def load_csv(filepath):
    """Load a UTF-8 CSV file as dictionaries."""
    with open(filepath, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(filepath, rows, fieldnames):
    """Write dictionaries to a UTF-8 CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_counts(title, counts):
    """Print one count table."""
    print(title)
    print("=" * len(title))
    for label, count in counts.most_common():
        print(f"{label if label else '(blank)'}: {count}")
    print()


def main():
    rows = load_csv(INPUT_PATH)
    repaired_rows = [apply_dependency_repair(row) for row in rows]
    output_fields = list(rows[0].keys()) + APPENDED_FIELDS

    write_csv(OUTPUT_PATH, repaired_rows, output_fields)

    repair_counts = Counter(row["dependency_repair_rule_id"] for row in repaired_rows)
    print_counts("Counts by dependency_repair_rule_id", repair_counts)
    print(f"Saved dependency-repaired dev baseline to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
