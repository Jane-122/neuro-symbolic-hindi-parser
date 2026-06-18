"""
Analyze remaining dev errors after Correction Layer v2.1.

Evaluation uses corrected_candidates from results/stanza_dev_corrected_v2_all.csv.
"""

from collections import Counter
from pathlib import Path

from evaluate_pipeline_against_gold import (
    DEV_SPLIT,
    GOLD_PATH,
    build_pipeline_index,
    dev_gold_rows,
    load_csv,
    normalize_token,
    parse_candidates,
    prediction_label,
    write_csv,
)


PIPELINE_PATH = Path("results/stanza_dev_corrected_v2_all.csv")
SUMMARY_PATH = Path("output/remaining_error_summary_v2.csv")
EXAMPLES_PATH = Path("output/remaining_error_examples_v2.csv")
EXAMPLES_PER_KARAKA = 50

ERROR_FIELDS = [
    "sent_id",
    "sentence_text",
    "token_form",
    "gold_karaka",
    "corrected_candidates",
    "deprel",
    "case_marker",
]

SUMMARY_FIELDS = [
    "summary_type",
    "label",
    "count",
]


def find_remaining_errors(gold_rows, pipeline_rows):
    """Return rows where corrected_candidates misses the gold Karaka."""
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
            parse_candidates(pipeline_row["corrected_candidates"])
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
            "corrected_candidates": (
                pipeline_row["corrected_candidates"] if pipeline_row else ""
            ),
            "deprel": pipeline_row["deprel"] if pipeline_row else "",
            "case_marker": pipeline_row["case_marker"] if pipeline_row else "",
        })

    return errors


def add_counter_rows(summary_rows, summary_type, counts):
    """Append sorted Counter rows to the summary table."""
    for label, count in counts.most_common():
        summary_rows.append({
            "summary_type": summary_type,
            "label": label if label else "(blank)",
            "count": count,
        })


def build_summary_rows(errors):
    """Build aggregate remaining-error summaries."""
    confusion_pairs = Counter(
        (
            row["gold_karaka"],
            prediction_label(parse_candidates(row["corrected_candidates"])),
        )
        for row in errors
    )
    pattern_counts = Counter(
        (
            row["gold_karaka"],
            row["deprel"],
            row["case_marker"] if row["case_marker"] else "(blank)",
            prediction_label(parse_candidates(row["corrected_candidates"])),
        )
        for row in errors
    )

    summary_rows = []
    add_counter_rows(
        summary_rows,
        "errors_by_gold_karaka",
        Counter(row["gold_karaka"] for row in errors),
    )
    add_counter_rows(
        summary_rows,
        "errors_by_deprel",
        Counter(row["deprel"] for row in errors),
    )
    add_counter_rows(
        summary_rows,
        "errors_by_case_marker",
        Counter(row["case_marker"] for row in errors),
    )
    add_counter_rows(
        summary_rows,
        "confusion_patterns",
        Counter({
            f"{gold} -> {predicted}": count
            for (gold, predicted), count in confusion_pairs.items()
        }),
    )
    add_counter_rows(
        summary_rows,
        "top_remaining_error_patterns",
        Counter({
            f"{gold} | {deprel} | {case_marker} | {predicted}": count
            for (gold, deprel, case_marker, predicted), count in pattern_counts.items()
        }),
    )
    return summary_rows


def representative_examples(errors):
    """Save up to 50 examples for each major remaining gold Karaka category."""
    examples = []
    grouped = {}

    for row in errors:
        grouped.setdefault(row["gold_karaka"], []).append(row)

    for gold_karaka, rows in sorted(grouped.items()):
        examples.extend(rows[:EXAMPLES_PER_KARAKA])

    return examples


def print_top_patterns(summary_rows):
    """Print the top 10 remaining error patterns after H1."""
    print("Top 10 remaining error patterns after H1")
    print("=" * 41)
    shown = 0
    for row in summary_rows:
        if row["summary_type"] != "top_remaining_error_patterns":
            continue
        print(f"{row['count']:>5}  {row['label']}")
        shown += 1
        if shown >= 10:
            break


def print_target_hint(summary_rows):
    """Print which gold Karaka classes dominate remaining errors."""
    print()
    print("Remaining errors by gold_karaka")
    print("=" * 33)
    for row in summary_rows:
        if row["summary_type"] == "errors_by_gold_karaka":
            print(f"{row['label']}: {row['count']}")


def main():
    gold_rows = dev_gold_rows(load_csv(GOLD_PATH))
    pipeline_rows = load_csv(PIPELINE_PATH)

    errors = find_remaining_errors(gold_rows, pipeline_rows)
    summary_rows = build_summary_rows(errors)
    examples = representative_examples(errors)

    write_csv(SUMMARY_PATH, summary_rows, SUMMARY_FIELDS)
    write_csv(EXAMPLES_PATH, examples, ERROR_FIELDS)

    print(f"Total remaining errors after H1: {len(errors)}")
    print()
    print_top_patterns(summary_rows)
    print_target_hint(summary_rows)
    print()
    print(f"Saved remaining error summary to: {SUMMARY_PATH}")
    print(f"Saved remaining error examples to: {EXAMPLES_PATH}")


if __name__ == "__main__":
    main()
