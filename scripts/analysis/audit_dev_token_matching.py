"""
Audit dev gold Karaka token matching against Stanza pipeline rows.

This reproduces the current matching key:
split, sent_id, normalized token text, occurrence order.
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


from collections import defaultdict, deque
from pathlib import Path

from evaluate_pipeline_against_gold import (
    DEV_SPLIT,
    GOLD_PATH,
    STANZA_PIPELINE_PATH,
    dev_gold_rows,
    load_csv,
    normalize_token,
    write_csv,
)


OUTPUT_PATH = OUTPUTS_ERROR_ANALYSIS / 'dev_token_matching_audit.csv'

OUTPUT_FIELDS = [
    "status",
    "sent_id",
    "gold_token",
    "pipeline_token",
    "gold_karaka",
    "deprel",
    "case_marker",
    "sentence_text",
]


def build_pipeline_index(rows, split):
    """Index pipeline rows by the current normalized token matching key."""
    index = defaultdict(deque)
    for row in rows:
        key = (
            split,
            row["sent_id"],
            normalize_token(row["token_form"]),
        )
        index[key].append(row)
    return index


def has_meaningful_candidates(row):
    """Return true if the pipeline row has any mapper or final candidates."""
    return bool(row["mapper_candidates"] or row["final_candidates"])


def matched_row(gold_row, pipeline_row):
    """Format one successfully matched audit row."""
    return {
        "status": "matched",
        "sent_id": gold_row["ud_sent_id"],
        "gold_token": gold_row["token"],
        "pipeline_token": pipeline_row["token_form"],
        "gold_karaka": gold_row["gold_karaka"],
        "deprel": pipeline_row["deprel"],
        "case_marker": pipeline_row["case_marker"],
        "sentence_text": pipeline_row["sentence_text"],
    }


def unmatched_gold_row(gold_row):
    """Format one gold row that could not be matched to a pipeline row."""
    return {
        "status": "unmatched_gold",
        "sent_id": gold_row["ud_sent_id"],
        "gold_token": gold_row["token"],
        "pipeline_token": "",
        "gold_karaka": gold_row["gold_karaka"],
        "deprel": "",
        "case_marker": "",
        "sentence_text": "",
    }


def extra_pipeline_row(pipeline_row):
    """Format one leftover meaningful pipeline candidate row."""
    return {
        "status": "extra_pipeline_candidate",
        "sent_id": pipeline_row["sent_id"],
        "gold_token": "",
        "pipeline_token": pipeline_row["token_form"],
        "gold_karaka": "",
        "deprel": pipeline_row["deprel"],
        "case_marker": pipeline_row["case_marker"],
        "sentence_text": pipeline_row["sentence_text"],
    }


def audit_matches(gold_rows, pipeline_rows, split):
    """Return audit rows and summary counts."""
    pipeline_index = build_pipeline_index(pipeline_rows, split)
    audit_rows = []
    matched_count = 0
    unmatched_count = 0

    for gold_row in gold_rows:
        key = (
            gold_row["split"],
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )

        if pipeline_index[key]:
            pipeline_row = pipeline_index[key].popleft()
            audit_rows.append(matched_row(gold_row, pipeline_row))
            matched_count += 1
        else:
            audit_rows.append(unmatched_gold_row(gold_row))
            unmatched_count += 1

    extra_count = 0
    for leftover_rows in pipeline_index.values():
        for pipeline_row in leftover_rows:
            if not has_meaningful_candidates(pipeline_row):
                continue
            audit_rows.append(extra_pipeline_row(pipeline_row))
            extra_count += 1

    return audit_rows, {
        "total_gold": len(gold_rows),
        "matched": matched_count,
        "unmatched": unmatched_count,
        "extra_pipeline_candidates": extra_count,
    }


def print_summary(counts):
    """Print the requested compact matching summary."""
    total_gold = counts["total_gold"]
    matched = counts["matched"]
    match_percentage = round((matched / total_gold) * 100, 2) if total_gold else 0.0

    print(f"total gold rows: {total_gold}")
    print(f"matched gold rows: {matched}")
    print(f"unmatched gold rows: {counts['unmatched']}")
    print(
        "extra pipeline rows with meaningful candidates: "
        f"{counts['extra_pipeline_candidates']}"
    )
    print(f"match percentage: {match_percentage}%")


def main():
    gold_rows = dev_gold_rows(load_csv(GOLD_PATH))
    pipeline_rows = load_csv(STANZA_PIPELINE_PATH)
    audit_rows, counts = audit_matches(gold_rows, pipeline_rows, DEV_SPLIT)

    write_csv(OUTPUT_PATH, audit_rows, OUTPUT_FIELDS)
    print_summary(counts)
    print()
    print(f"Saved dev token matching audit to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
