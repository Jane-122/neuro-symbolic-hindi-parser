"""
Analyze neural-only mapper errors on the dev split.

Compares gold_karaka from aligned HDTB labels against mapper_candidates from
the Stanza dev baseline output.
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


from collections import Counter
from pathlib import Path

from evaluate_pipeline_against_gold import (
    DEV_SPLIT,
    GOLD_PATH,
    STANZA_PIPELINE_PATH,
    build_pipeline_index,
    dev_gold_rows,
    load_csv,
    normalize_token,
    parse_candidates,
    prediction_label,
    write_csv,
)


ERRORS_PATH = OUTPUTS_ERROR_ANALYSIS / 'dev_neural_only_errors.csv'
SUMMARY_PATH = OUTPUTS_ERROR_ANALYSIS / 'dev_neural_error_summary.csv'

ERROR_FIELDS = [
    "sent_id",
    "sentence_text",
    "token_form",
    "gold_karaka",
    "mapper_candidates",
    "deprel",
    "case_marker",
    "verifier_candidates",
    "final_candidates",
    "verifier_rule_id",
]

SUMMARY_FIELDS = [
    "summary_type",
    "label",
    "count",
]


def find_errors(gold_rows, pipeline_rows):
    """Return all dev rows where mapper_candidates miss the gold karaka."""
    pipeline_index = build_pipeline_index(pipeline_rows)
    errors = []

    for gold_row in gold_rows:
        key = (
            DEV_SPLIT,
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )
        pipeline_row = pipeline_index[key].popleft() if pipeline_index[key] else None
        candidates = (
            parse_candidates(pipeline_row["mapper_candidates"])
            if pipeline_row
            else set()
        )

        if gold_row["gold_karaka"] in candidates:
            continue

        errors.append({
            "sent_id": gold_row["ud_sent_id"],
            "sentence_text": pipeline_row["sentence_text"] if pipeline_row else "",
            "token_form": pipeline_row["token_form"] if pipeline_row else gold_row["token"],
            "gold_karaka": gold_row["gold_karaka"],
            "mapper_candidates": pipeline_row["mapper_candidates"] if pipeline_row else "",
            "deprel": pipeline_row["deprel"] if pipeline_row else "",
            "case_marker": pipeline_row["case_marker"] if pipeline_row else "",
            "verifier_candidates": pipeline_row["verifier_candidates"] if pipeline_row else "",
            "final_candidates": pipeline_row["final_candidates"] if pipeline_row else "",
            "verifier_rule_id": pipeline_row["verifier_rule_id"] if pipeline_row else "",
        })

    return errors


def add_counter_rows(summary_rows, summary_type, counts):
    """Append sorted Counter rows to a summary table."""
    for label, count in counts.most_common():
        summary_rows.append({
            "summary_type": summary_type,
            "label": label if label else "(blank)",
            "count": count,
        })


def build_summary_rows(errors):
    """Build requested aggregate summaries for neural-only errors."""
    by_gold = Counter(row["gold_karaka"] for row in errors)
    by_deprel = Counter(row["deprel"] for row in errors)
    by_case_marker = Counter(row["case_marker"] for row in errors)
    confusion_pairs = Counter(
        (
            row["gold_karaka"],
            prediction_label(parse_candidates(row["mapper_candidates"])),
        )
        for row in errors
    )

    summary_rows = []
    add_counter_rows(summary_rows, "errors_by_gold_karaka", by_gold)
    add_counter_rows(summary_rows, "errors_by_deprel", by_deprel)
    add_counter_rows(summary_rows, "errors_by_case_marker", by_case_marker)
    add_counter_rows(
        summary_rows,
        "common_confusion_pairs",
        Counter({
            f"{gold} -> {predicted}": count
            for (gold, predicted), count in confusion_pairs.items()
        }),
    )
    return summary_rows


def print_compact_summary(errors):
    """Print a short terminal summary."""
    print("Dev neural-only error summary")
    print("=" * 29)
    print(f"Total errors: {len(errors)}")
    print()

    for title, counts in [
        ("Errors by gold_karaka", Counter(row["gold_karaka"] for row in errors)),
        ("Errors by deprel", Counter(row["deprel"] for row in errors)),
        ("Errors by case_marker", Counter(row["case_marker"] for row in errors)),
    ]:
        print(title)
        for label, count in counts.most_common(10):
            print(f"  {label if label else '(blank)'}: {count}")
        print()


def main():
    gold_rows = dev_gold_rows(load_csv(GOLD_PATH))
    pipeline_rows = load_csv(STANZA_PIPELINE_PATH)

    errors = find_errors(gold_rows, pipeline_rows)
    summary_rows = build_summary_rows(errors)

    write_csv(ERRORS_PATH, errors, ERROR_FIELDS)
    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_FIELDS)

    print_compact_summary(errors)
    print(f"Saved detailed errors to: {ERRORS_PATH}")
    print(f"Saved error summary to: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
