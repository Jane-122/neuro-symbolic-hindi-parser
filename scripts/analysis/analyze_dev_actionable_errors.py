"""
Filter dev neural-only errors to actionable syntactic/case-marker patterns.
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
from collections import Counter
from pathlib import Path


INPUT_PATH = OUTPUTS_ERROR_ANALYSIS / 'dev_neural_only_errors.csv'
ACTIONABLE_ERRORS_PATH = OUTPUTS_ERROR_ANALYSIS / 'dev_actionable_neural_errors.csv'
SUMMARY_PATH = OUTPUTS_ERROR_ANALYSIS / 'dev_actionable_error_summary.csv'

ACTIONABLE_DEPRELS = {"nsubj", "obj", "iobj", "obl", "nmod"}
ACTIONABLE_CASE_MARKERS = {"ने", "को", "से", "में", "पर"}
TOP_N = 30

SUMMARY_FIELDS = [
    "summary_type",
    "pattern",
    "count",
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


def clean(value):
    """Use a stable display value for blank CSV cells."""
    return value if value else "(blank)"


def is_actionable(row):
    """Return true if the error matches the requested actionable filters."""
    return (
        row["deprel"] in ACTIONABLE_DEPRELS
        or row["case_marker"] in ACTIONABLE_CASE_MARKERS
    )


def pattern(*values):
    """Build a compact pattern string for grouped summaries."""
    return " | ".join(clean(value) for value in values)


def verifier_effect(row):
    """Describe how final_candidates differs from mapper_candidates."""
    mapper = row["mapper_candidates"]
    final = row["final_candidates"]

    if mapper == final:
        return "unchanged"
    if not mapper and final:
        return "added_final_candidate"
    if mapper and not final:
        return "removed_mapper_candidate"
    return "changed_candidate_set"


def build_summary_rows(rows):
    """Build top-N summary rows for the requested actionable patterns."""
    counters = {
        "gold_karaka + deprel + case_marker": Counter(
            pattern(row["gold_karaka"], row["deprel"], row["case_marker"])
            for row in rows
        ),
        "gold_karaka + mapper_candidates": Counter(
            pattern(row["gold_karaka"], row["mapper_candidates"])
            for row in rows
        ),
        "deprel + case_marker + mapper_candidates": Counter(
            pattern(row["deprel"], row["case_marker"], row["mapper_candidates"])
            for row in rows
        ),
        "final_candidates vs mapper_candidates": Counter(
            pattern(
                f"mapper={clean(row['mapper_candidates'])}",
                f"final={clean(row['final_candidates'])}",
                verifier_effect(row),
            )
            for row in rows
        ),
    }

    summary_rows = []
    for summary_type, counts in counters.items():
        for pattern_text, count in counts.most_common(TOP_N):
            summary_rows.append({
                "summary_type": summary_type,
                "pattern": pattern_text,
                "count": count,
            })
    return summary_rows


def print_top_patterns(summary_rows):
    """Print the top 30 patterns per summary type."""
    current_type = None
    for row in summary_rows:
        if row["summary_type"] != current_type:
            current_type = row["summary_type"]
            print()
            print(current_type)
            print("=" * len(current_type))
        print(f"{row['count']:>5}  {row['pattern']}")


def main():
    rows = load_csv(INPUT_PATH)
    actionable_rows = [row for row in rows if is_actionable(row)]
    summary_rows = build_summary_rows(actionable_rows)

    write_csv(ACTIONABLE_ERRORS_PATH, actionable_rows, rows[0].keys())
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_FIELDS)

    print(f"Total neural-only errors: {len(rows)}")
    print(f"Actionable neural-only errors: {len(actionable_rows)}")
    print_top_patterns(summary_rows)
    print()
    print(f"Saved actionable errors to: {ACTIONABLE_ERRORS_PATH}")
    print(f"Saved actionable summary to: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
