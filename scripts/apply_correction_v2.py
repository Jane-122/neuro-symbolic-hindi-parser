"""
Apply Correction Layer v2.1 to one Stanza baseline split.

Only H1_NMOD_LOCATIVE_ADHIKARANA is allowed to modify corrected_candidates.
Dependency repair and passive correction rules are not applied here.
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = PROJECT_ROOT / "src" / "pipeline"
sys.path.insert(0, str(PIPELINE_DIR))

from correction_layer_v2 import CORRECTION_RULE_ID, apply_correction


SPLITS = {"train", "dev", "test"}
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


def validate_correction_scope(rows):
    """Confirm only H1 changes corrected_candidates."""
    for row in rows:
        changed = row["corrected_candidates"] != row["final_candidates"]
        if changed and row["correction_rule_id"] != CORRECTION_RULE_ID:
            raise ValueError(
                "Unexpected correction modified corrected_candidates: "
                f"{row['correction_rule_id']}"
            )


def print_counts(title, counts):
    """Print one count table."""
    print(title)
    print("=" * len(title))
    for label, count in counts.most_common():
        print(f"{label if label else '(blank)'}: {count}")
    print()


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Apply Correction Layer v2.1 to one split.",
    )
    parser.add_argument(
        "--split",
        choices=sorted(SPLITS),
        required=True,
        help="Dataset split to process.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    split = args.split
    input_path = Path(f"results/stanza_{split}_baseline_all.csv")
    output_path = Path(f"results/stanza_{split}_corrected_v2_all.csv")

    rows = load_csv(input_path)
    corrected_rows = [apply_correction(row) for row in rows]
    validate_correction_scope(corrected_rows)
    output_fields = list(rows[0].keys()) + APPENDED_FIELDS

    write_csv(output_path, corrected_rows, output_fields)

    correction_counts = Counter(row["correction_rule_id"] for row in corrected_rows)
    diagnostic_counts = Counter(row["diagnostic_flag"] for row in corrected_rows)

    print_counts("Counts by correction_rule_id", correction_counts)
    print_counts("Counts by diagnostic_flag", diagnostic_counts)
    print(f"Confirmed only {CORRECTION_RULE_ID} can modify corrected_candidates.")
    print(f"Saved corrected {split} baseline to: {output_path}")


if __name__ == "__main__":
    main()
