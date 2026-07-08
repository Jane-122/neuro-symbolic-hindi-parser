"""
Apply correction layer v2 to the Stanza train baseline output.
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import _bootstrap  # noqa: F401

from paths import (
    OUTPUTS_ALIGNMENT,
    OUTPUTS_ERROR_ANALYSIS,
    OUTPUTS_GOLD,
    OUTPUTS_METRICS,
    OUTPUTS_REJECTED_DR1,
    REJECTED_DR1,
    STANZA_BASELINE,
    STANZA_CORRECTED,
    STANZA_GOLD_UD,
    correction_metrics,
    correction_per_karaka,
    stanza_baseline_all,
    stanza_corrected_all,
)


import csv
import sys
from collections import Counter
from pathlib import Path


# pipeline imports handled by _bootstrap

from correction_layer_v2 import apply_correction


INPUT_PATH = STANZA_BASELINE / 'stanza_train_baseline_all.csv'
OUTPUT_PATH = STANZA_CORRECTED / 'stanza_train_corrected_v2_all.csv'

APPENDED_FIELDS = [
    "corrected_candidates",
    "correction_applied",
    "correction_rule_id",
    "correction_type",
    "diagnostic_flag",
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
    corrected_rows = [apply_correction(row) for row in rows]
    output_fields = list(rows[0].keys()) + APPENDED_FIELDS

    write_csv(OUTPUT_PATH, corrected_rows, output_fields)

    correction_counts = Counter(row["correction_rule_id"] for row in corrected_rows)
    diagnostic_counts = Counter(row["diagnostic_flag"] for row in corrected_rows)

    print_counts("Counts by correction_rule_id", correction_counts)
    print_counts("Counts by diagnostic_flag", diagnostic_counts)
    print(f"Saved corrected train baseline to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
