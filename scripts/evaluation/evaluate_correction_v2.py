"""
Evaluate Correction Layer v2.1 for one split.

Compares:
- neural_only: mapper_candidates
- verifier_v1: final_candidates
- correction_v2.1: corrected_candidates
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import _bootstrap  # noqa: F401

from paths import (
    correction_metrics,
    correction_per_karaka,
    stanza_baseline_all,
    stanza_corrected_all,
    udpipe_baseline_all,
    udpipe_corrected_all,
    udpipe_correction_metrics,
    udpipe_per_karaka_comparison,
)


import argparse
from collections import defaultdict, deque
from pathlib import Path

from evaluate_dev_metrics_strict_vs_candidate import (
    MODES,
    compute_mode_metrics,
)
from evaluate_pipeline_against_gold import (
    GOLD_PATH,
    KARAKAS,
    load_csv,
    normalize_token,
    parse_candidates,
    write_csv,
)


SPLITS = {"train", "dev", "test"}
PARSERS = {"stanza", "udpipe"}
SYSTEMS = [
    ("neural_only", "mapper_candidates", "baseline"),
    ("verifier_v1", "final_candidates", "baseline"),
    ("correction_v2.1", "corrected_candidates", "corrected"),
]

OUTPUT_FIELDS = [
    "system",
    "mode",
    "metric_scope",
    "karaka",
    "support",
    "matched_gold_rows",
    "unmatched_gold_rows",
    "tp",
    "fp",
    "fn",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "macro_precision",
    "macro_recall",
    "macro_f1",
]


def split_gold_rows(rows, split):
    """Keep rows for one split where a gold karaka label exists."""
    return [
        row for row in rows
        if row["split"] == split and row["gold_karaka"]
    ]


def build_pipeline_index(rows, split):
    """Index pipeline rows by split, sentence id, and normalized token."""
    index = defaultdict(deque)
    for row in rows:
        key = (
            split,
            row["sent_id"],
            normalize_token(row["token_form"]),
        )
        index[key].append(row)
    return index


def evaluate_rows(gold_rows, pipeline_rows, candidate_column, split):
    """Join gold rows to pipeline rows and parse candidate labels."""
    pipeline_index = build_pipeline_index(pipeline_rows, split)
    evaluated_rows = []
    matched_gold_rows = 0
    unmatched_gold_rows = 0

    for gold_row in gold_rows:
        key = (
            split,
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )
        pipeline_row = pipeline_index[key].popleft() if pipeline_index[key] else None
        candidates = (
            parse_candidates(pipeline_row[candidate_column])
            if pipeline_row
            else set()
        )

        if pipeline_row:
            matched_gold_rows += 1
        else:
            unmatched_gold_rows += 1

        evaluated_rows.append({
            "gold": gold_row["gold_karaka"],
            "candidates": candidates,
        })

    return evaluated_rows, matched_gold_rows, unmatched_gold_rows


def compute_mode_metrics_with_matching(
    system_name,
    mode,
    evaluated_rows,
    matched_gold_rows,
    unmatched_gold_rows,
):
    """Compute overall, macro, and per-karaka metrics with match counts."""
    base_rows = compute_mode_metrics(system_name, mode, evaluated_rows)
    for row in base_rows:
        if row["metric_scope"] == "overall":
            row["matched_gold_rows"] = matched_gold_rows
            row["unmatched_gold_rows"] = unmatched_gold_rows
        else:
            row["matched_gold_rows"] = ""
            row["unmatched_gold_rows"] = ""
    return base_rows


def print_compact_table_with_matching(rows):
    """Print system, mode, accuracy, macro F1, and match counts."""
    print(
        f"{'system':<16} {'mode':<15} {'accuracy':>10} "
        f"{'macro_f1':>10} {'matched':>9} {'unmatched':>10}"
    )
    print("-" * 78)
    for row in rows:
        if row["metric_scope"] != "overall":
            continue
        print(
            f"{row['system']:<16} {row['mode']:<15} "
            f"{row['accuracy']:>10} {row['macro_f1']:>10} "
            f"{row['matched_gold_rows']:>9} {row['unmatched_gold_rows']:>10}"
        )


def resolve_paths(parser: str, split: str):
    """Return baseline, corrected, and metrics paths for one parser branch."""
    if parser == "stanza":
        return (
            stanza_baseline_all(split),
            stanza_corrected_all(split),
            correction_metrics(split),
        )
    return (
        udpipe_baseline_all(split),
        udpipe_corrected_all(split),
        udpipe_correction_metrics(split),
    )


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate Correction Layer v2.1 for one split.",
    )
    parser.add_argument(
        "--split",
        choices=sorted(SPLITS),
        required=True,
        help="Dataset split to evaluate.",
    )
    parser.add_argument(
        "--parser",
        choices=sorted(PARSERS),
        default="stanza",
        help="Parser baseline branch to evaluate, default: stanza.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    split = args.split
    baseline_path, corrected_path, output_path = resolve_paths(args.parser, split)

    gold_rows = split_gold_rows(load_csv(GOLD_PATH), split)
    baseline_rows = load_csv(baseline_path)
    corrected_rows = load_csv(corrected_path)
    output_rows = []

    for system_name, candidate_column, source in SYSTEMS:
        pipeline_rows = baseline_rows if source == "baseline" else corrected_rows
        evaluated_rows, matched_count, unmatched_count = evaluate_rows(
            gold_rows,
            pipeline_rows,
            candidate_column,
            split,
        )
        for mode in MODES:
            output_rows.extend(compute_mode_metrics_with_matching(
                system_name,
                mode,
                evaluated_rows,
                matched_count,
                unmatched_count,
            ))

    write_csv(output_path, output_rows, OUTPUT_FIELDS)
    print_compact_table_with_matching(output_rows)
    print()
    print(f"Saved correction v2.1 metrics to: {output_path}")


if __name__ == "__main__":
    main()
