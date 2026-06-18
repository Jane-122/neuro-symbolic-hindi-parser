"""
Analyze passive diagnostic flags without implementing any correction rule.

Inputs:
- results/stanza_dev_corrected_v2_all.csv
- output/gold_karaka_labels.csv

Uses only dev split and the current normalized-token occurrence matching.
"""

import csv
from collections import Counter, defaultdict, deque
from pathlib import Path

from evaluate_pipeline_against_gold import (
    DEV_SPLIT,
    GOLD_PATH,
    dev_gold_rows,
    load_csv,
    normalize_token,
    write_csv,
)


PIPELINE_PATH = Path("results/stanza_dev_corrected_v2_all.csv")
SUMMARY_PATH = Path("output/passive_diagnostic_summary.csv")
EXAMPLES_PATH = Path("output/passive_diagnostic_examples.csv")

PASSIVE_FLAGS = [
    "possible_passive_karta",
    "possible_passive_karma",
]

PASSIVE_INDICATORS = [
    "गया",
    "गई",
    "गए",
    "जाता",
    "जाती",
    "जाते",
    "किया गया",
    "की गई",
    "किये गए",
]

SUMMARY_FIELDS = [
    "diagnostic_flag",
    "summary_type",
    "label",
    "count",
    "notes",
]

EXAMPLE_FIELDS = [
    "sent_id",
    "sentence_text",
    "token_form",
    "gold_karaka",
    "deprel",
    "case_marker",
    "final_candidates",
    "corrected_candidates",
    "diagnostic_flag",
]


def build_pipeline_index(rows):
    """Index pipeline rows by the current normalized token matching key."""
    index = defaultdict(deque)
    for row in rows:
        key = (
            DEV_SPLIT,
            row["sent_id"],
            normalize_token(row["token_form"]),
        )
        index[key].append(row)
    return index


def match_gold_to_pipeline(gold_rows, pipeline_rows):
    """Return a mapping from pipeline row object id to matched gold row."""
    pipeline_index = build_pipeline_index(pipeline_rows)
    matched = {}

    for gold_row in gold_rows:
        key = (
            gold_row["split"],
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )
        if pipeline_index[key]:
            pipeline_row = pipeline_index[key].popleft()
            matched[id(pipeline_row)] = gold_row

    return matched


def add_count_rows(summary_rows, diagnostic_flag, summary_type, counts):
    """Append Counter rows to the summary output."""
    for label, count in counts.most_common():
        summary_rows.append({
            "diagnostic_flag": diagnostic_flag,
            "summary_type": summary_type,
            "label": label if label else "(blank)",
            "count": count,
            "notes": "",
        })


def add_single_summary(summary_rows, diagnostic_flag, summary_type, label, count, notes=""):
    """Append one scalar summary row."""
    summary_rows.append({
        "diagnostic_flag": diagnostic_flag,
        "summary_type": summary_type,
        "label": label,
        "count": count,
        "notes": notes,
    })


def indicator_counts(rows):
    """Count sentence-level passive lexical indicators among flagged rows."""
    counts = Counter()
    for row in rows:
        sentence_text = row["sentence_text"]
        for indicator in PASSIVE_INDICATORS:
            if indicator in sentence_text:
                counts[indicator] += 1
    return counts


def estimate_opportunity(matched_gold_rows):
    """Estimate dominant-label correction opportunity for matched rows."""
    gold_counts = Counter(row["gold_karaka"] for row in matched_gold_rows)
    if not gold_counts:
        return "", 0, 0

    dominant_gold, correct_count = gold_counts.most_common(1)[0]
    incorrect_count = len(matched_gold_rows) - correct_count
    return dominant_gold, correct_count, incorrect_count


def conclusion_for_flag(matched_count, dominant_correct, dominant_incorrect):
    """Classify whether a passive correction looks supported."""
    if matched_count == 0:
        return "NOT SUPPORTED"

    precision_estimate = dominant_correct / matched_count
    if precision_estimate >= 0.9 and dominant_correct >= 50:
        return "SAFE"
    if precision_estimate >= 0.7 and dominant_correct >= 30:
        return "PROMISING"
    if precision_estimate >= 0.5:
        return "RISKY"
    return "NOT SUPPORTED"


def example_row(row, gold_row):
    """Format one representative diagnostic example."""
    return {
        "sent_id": row["sent_id"],
        "sentence_text": row["sentence_text"],
        "token_form": row["token_form"],
        "gold_karaka": gold_row["gold_karaka"] if gold_row else "",
        "deprel": row["deprel"],
        "case_marker": row["case_marker"],
        "final_candidates": row["final_candidates"],
        "corrected_candidates": row["corrected_candidates"],
        "diagnostic_flag": row["diagnostic_flag"],
    }


def analyze_flag(diagnostic_flag, pipeline_rows, matched_gold_by_pipeline_id):
    """Analyze one passive diagnostic flag."""
    flagged_rows = [
        row for row in pipeline_rows
        if row["diagnostic_flag"] == diagnostic_flag
    ]
    matched_pairs = [
        (row, matched_gold_by_pipeline_id[id(row)])
        for row in flagged_rows
        if id(row) in matched_gold_by_pipeline_id
    ]
    matched_gold_rows = [gold_row for _, gold_row in matched_pairs]

    summary_rows = []
    add_single_summary(
        summary_rows,
        diagnostic_flag,
        "totals",
        "total_flagged_rows",
        len(flagged_rows),
    )
    add_single_summary(
        summary_rows,
        diagnostic_flag,
        "totals",
        "matched_gold_rows",
        len(matched_pairs),
    )
    add_single_summary(
        summary_rows,
        diagnostic_flag,
        "totals",
        "unmatched_flagged_rows",
        len(flagged_rows) - len(matched_pairs),
    )

    add_count_rows(
        summary_rows,
        diagnostic_flag,
        "gold_karaka_distribution",
        Counter(row["gold_karaka"] for row in matched_gold_rows),
    )
    add_count_rows(
        summary_rows,
        diagnostic_flag,
        "deprel_distribution",
        Counter(row["deprel"] for row in flagged_rows),
    )
    add_count_rows(
        summary_rows,
        diagnostic_flag,
        "case_marker_distribution",
        Counter(row["case_marker"] for row in flagged_rows),
    )
    add_count_rows(
        summary_rows,
        diagnostic_flag,
        "final_candidates_distribution",
        Counter(row["final_candidates"] for row in flagged_rows),
    )
    add_count_rows(
        summary_rows,
        diagnostic_flag,
        "passive_lexical_indicator",
        indicator_counts(flagged_rows),
    )

    dominant_gold, correct_count, incorrect_count = estimate_opportunity(matched_gold_rows)
    conclusion = conclusion_for_flag(len(matched_gold_rows), correct_count, incorrect_count)
    add_single_summary(
        summary_rows,
        diagnostic_flag,
        "correction_opportunity_estimate",
        "dominant_gold_karaka",
        correct_count,
        notes=f"{dominant_gold}; incorrect_if_converted={incorrect_count}",
    )
    add_single_summary(
        summary_rows,
        diagnostic_flag,
        "conclusion",
        conclusion,
        len(matched_gold_rows),
        notes=(
            "Based on dominant-gold conversion estimate among matched gold rows. "
            "No rule implemented."
        ),
    )

    examples = [
        example_row(row, gold_row)
        for row, gold_row in matched_pairs[:50]
    ]

    return summary_rows, examples, conclusion


def print_flag_report(diagnostic_flag, summary_rows, conclusion):
    """Print a compact report for one diagnostic flag."""
    print(diagnostic_flag)
    print("=" * len(diagnostic_flag))
    for row in summary_rows:
        if row["summary_type"] != "totals":
            continue
        print(f"{row['label']}: {row['count']}")

    print("gold Karaka distribution:")
    for row in summary_rows:
        if row["summary_type"] == "gold_karaka_distribution":
            print(f"  {row['label']}: {row['count']}")

    for row in summary_rows:
        if row["summary_type"] == "correction_opportunity_estimate":
            print(
                "dominant conversion estimate: "
                f"{row['notes']} correct_if_converted={row['count']}"
            )
    print(f"conclusion: {conclusion}")
    print()


def main():
    pipeline_rows = load_csv(PIPELINE_PATH)
    gold_rows = dev_gold_rows(load_csv(GOLD_PATH))
    matched_gold_by_pipeline_id = match_gold_to_pipeline(gold_rows, pipeline_rows)

    all_summary_rows = []
    all_examples = []

    for diagnostic_flag in PASSIVE_FLAGS:
        summary_rows, examples, conclusion = analyze_flag(
            diagnostic_flag,
            pipeline_rows,
            matched_gold_by_pipeline_id,
        )
        all_summary_rows.extend(summary_rows)
        all_examples.extend(examples)
        print_flag_report(diagnostic_flag, summary_rows, conclusion)

    write_csv(SUMMARY_PATH, all_summary_rows, SUMMARY_FIELDS)
    write_csv(EXAMPLES_PATH, all_examples, EXAMPLE_FIELDS)
    print(f"Saved passive diagnostic summary to: {SUMMARY_PATH}")
    print(f"Saved passive diagnostic examples to: {EXAMPLES_PATH}")


if __name__ == "__main__":
    main()
