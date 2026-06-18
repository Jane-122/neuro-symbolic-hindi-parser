"""
Evaluate correction layer v2 against train gold Karaka labels.

Compares:
- neural_only: mapper_candidates
- verifier_v1: final_candidates
- correction_v2: corrected_candidates
"""

from collections import defaultdict, deque
from pathlib import Path

from evaluate_dev_metrics_strict_vs_candidate import (
    MODES,
    OUTPUT_FIELDS,
    compute_mode_metrics,
    print_compact_table,
)
from evaluate_pipeline_against_gold import (
    GOLD_PATH,
    load_csv,
    normalize_token,
    parse_candidates,
    write_csv,
)


TRAIN_SPLIT = "train"
BASELINE_PATH = Path("results/stanza_train_baseline_all.csv")
CORRECTED_PATH = Path("results/stanza_train_corrected_v2_all.csv")
OUTPUT_PATH = Path("output/train_correction_v2_metrics.csv")

SYSTEMS = [
    ("neural_only", "mapper_candidates", BASELINE_PATH),
    ("verifier_v1", "final_candidates", BASELINE_PATH),
    ("correction_v2", "corrected_candidates", CORRECTED_PATH),
]


def train_gold_rows(rows):
    """Keep train rows where a gold karaka label exists."""
    return [
        row for row in rows
        if row["split"] == TRAIN_SPLIT and row["gold_karaka"]
    ]


def build_pipeline_index(rows):
    """Index pipeline rows by split, sentence id, and normalized token."""
    index = defaultdict(deque)
    for row in rows:
        key = (
            TRAIN_SPLIT,
            row["sent_id"],
            normalize_token(row["token_form"]),
        )
        index[key].append(row)
    return index


def evaluate_rows(gold_rows, pipeline_rows, candidate_column):
    """Join train gold rows to pipeline rows and parse candidate labels."""
    pipeline_index = build_pipeline_index(pipeline_rows)
    evaluated_rows = []

    for gold_row in gold_rows:
        key = (
            TRAIN_SPLIT,
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )
        pipeline_row = pipeline_index[key].popleft() if pipeline_index[key] else None
        candidates = (
            parse_candidates(pipeline_row[candidate_column])
            if pipeline_row
            else set()
        )

        evaluated_rows.append({
            "gold": gold_row["gold_karaka"],
            "candidates": candidates,
        })

    return evaluated_rows


def main():
    gold_rows = train_gold_rows(load_csv(GOLD_PATH))
    output_rows = []

    for system_name, candidate_column, input_path in SYSTEMS:
        pipeline_rows = load_csv(input_path)
        evaluated_rows = evaluate_rows(gold_rows, pipeline_rows, candidate_column)
        for mode in MODES:
            output_rows.extend(compute_mode_metrics(system_name, mode, evaluated_rows))

    write_csv(OUTPUT_PATH, output_rows, OUTPUT_FIELDS)
    print_compact_table(output_rows)
    print()
    print(f"Saved train correction v2 metrics to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
