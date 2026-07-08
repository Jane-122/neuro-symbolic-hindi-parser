"""
Summarize final correction-layer error patterns for paper analysis.

Uses existing corrected pipeline outputs and gold Karaka labels.
Does not modify system logic or evaluation formulas.
"""

import argparse
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import _bootstrap  # noqa: F401

from correction_layer_v2 import CORRECTION_RULE_ID
from paths import (
    OUTPUTS_ERROR_ANALYSIS,
    stanza_corrected_all,
    udpipe_corrected_all,
)

from evaluate_pipeline_against_gold import (
    GOLD_PATH,
    NO_PREDICTION,
    load_csv,
    normalize_token,
    parse_candidates,
    write_csv,
)


SPLITS = {"dev", "test"}
PARSERS = {"stanza", "udpipe"}

KARMA_SAMPRADANA = {"Karma", "Sampradana"}
KARANA_APADANA = {"Karana", "Apadana"}

ROW_FIELDS = [
    "sent_id",
    "sentence_text",
    "gold_token",
    "gold_karaka",
    "pipeline_token",
    "deprel",
    "case_marker",
    "mapper_candidates",
    "final_candidates",
    "corrected_candidates",
    "correction_rule_id",
    "strict_prediction",
    "failure_type",
]

FAILURE_BY_KARAKA_FIELDS = [
    "gold_karaka",
    "failure_type",
    "count",
]

ERROR_PATTERN_FIELDS = [
    "gold_karaka",
    "deprel",
    "case_marker",
    "count",
]

CONFUSION_FIELDS = [
    "gold_karaka",
    "strict_prediction",
    "count",
]


def split_gold_rows(rows, split):
    """Keep rows for one split where a gold karaka label exists."""
    return [
        row for row in rows
        if row["split"] == split and row["gold_karaka"]
    ]


def resolve_corrected_path(parser, split):
    """Return corrected pipeline CSV path for one parser branch."""
    if parser == "stanza":
        return stanza_corrected_all(split)
    return udpipe_corrected_all(split)


def output_path(parser, split, suffix):
    """Build one error-analysis output path."""
    return OUTPUTS_ERROR_ANALYSIS / f"{parser}_{split}_{suffix}.csv"


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


def strict_prediction_label(candidates):
    """Return the strict single-label prediction, or blank if ambiguous/empty."""
    if len(candidates) == 1:
        return next(iter(candidates))
    return ""


def classify_failure_type(gold_karaka, candidates, matched):
    """Assign one failure category for a gold row."""
    if not matched:
        return "unmatched_gold"
    if not candidates:
        return "no_prediction"
    if gold_karaka in candidates and len(candidates) == 1:
        return "strict_correct"
    if gold_karaka in candidates:
        return "candidate_correct_strict_fail"
    return "candidate_wrong"


def clean(value):
    """Use a stable display value for blank CSV cells."""
    return value if value else "(blank)"


def analyze_rows(gold_rows, pipeline_rows, split):
    """Join gold and corrected pipeline rows and build per-row analysis."""
    pipeline_index = build_pipeline_index(pipeline_rows, split)
    rows = []

    for gold_row in gold_rows:
        key = (
            split,
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )
        pipeline_row = pipeline_index[key].popleft() if pipeline_index[key] else None
        candidates = (
            parse_candidates(pipeline_row["corrected_candidates"])
            if pipeline_row
            else set()
        )
        failure_type = classify_failure_type(
            gold_row["gold_karaka"],
            candidates,
            pipeline_row is not None,
        )

        rows.append({
            "sent_id": gold_row["ud_sent_id"],
            "sentence_text": pipeline_row["sentence_text"] if pipeline_row else "",
            "gold_token": gold_row["token"],
            "gold_karaka": gold_row["gold_karaka"],
            "pipeline_token": pipeline_row["token_form"] if pipeline_row else "",
            "deprel": pipeline_row["deprel"] if pipeline_row else "",
            "case_marker": pipeline_row["case_marker"] if pipeline_row else "",
            "mapper_candidates": pipeline_row["mapper_candidates"] if pipeline_row else "",
            "final_candidates": pipeline_row["final_candidates"] if pipeline_row else "",
            "corrected_candidates": pipeline_row["corrected_candidates"] if pipeline_row else "",
            "correction_rule_id": (
                pipeline_row.get("correction_rule_id", "") if pipeline_row else ""
            ),
            "strict_prediction": strict_prediction_label(candidates),
            "failure_type": failure_type,
        })

    return rows


def build_failure_by_karaka(rows):
    """Count rows by gold_karaka and failure_type."""
    counts = Counter((row["gold_karaka"], row["failure_type"]) for row in rows)
    return [
        {
            "gold_karaka": gold_karaka,
            "failure_type": failure_type,
            "count": count,
        }
        for (gold_karaka, failure_type), count in sorted(counts.items())
    ]


def build_error_patterns(rows):
    """Count error rows by gold_karaka, deprel, and case_marker."""
    error_rows = [
        row for row in rows if row["failure_type"] != "strict_correct"
    ]
    counts = Counter(
        (row["gold_karaka"], row["deprel"], row["case_marker"])
        for row in error_rows
    )
    return [
        {
            "gold_karaka": gold_karaka,
            "deprel": deprel,
            "case_marker": case_marker,
            "count": count,
        }
        for (gold_karaka, deprel, case_marker), count in counts.most_common()
    ]


def build_detailed_error_patterns(rows):
    """Count error rows with failure type and strict prediction for inspection."""
    error_rows = [
        row for row in rows if row["failure_type"] != "strict_correct"
    ]
    counts = Counter(
        (
            row["gold_karaka"],
            row["deprel"],
            row["case_marker"],
            row["failure_type"],
            row["strict_prediction"],
        )
        for row in error_rows
    )
    return [
        {
            "gold_karaka": gold_karaka,
            "deprel": deprel,
            "case_marker": case_marker,
            "failure_type": failure_type,
            "strict_prediction": strict_prediction,
            "count": count,
        }
        for (
            gold_karaka,
            deprel,
            case_marker,
            failure_type,
            strict_prediction,
        ), count in counts.most_common()
    ]


def build_confusion_summary(rows):
    """Count gold_karaka vs strict_prediction pairs."""
    counts = Counter(
        (row["gold_karaka"], row["strict_prediction"] or NO_PREDICTION)
        for row in rows
    )
    return [
        {
            "gold_karaka": gold_karaka,
            "strict_prediction": strict_prediction,
            "count": count,
        }
        for (gold_karaka, strict_prediction), count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0][0], item[0][1]),
        )
    ]


def filter_karaka_cases(rows, karaka_set):
    """Return focused rows for one Karaka subset."""
    return [row for row in rows if row["gold_karaka"] in karaka_set]


def build_h1_success_rows(rows):
    """Return rows where frozen H1 fired."""
    return [
        row for row in rows
        if row["correction_rule_id"] == CORRECTION_RULE_ID
    ]


def print_failure_summary(parser, split, rows):
    """Print compact failure-type counts."""
    counts = Counter(row["failure_type"] for row in rows)
    print(f"{parser} {split} failure summary")
    print("=" * (len(parser) + len(split) + 17))
    print(f"Total gold rows: {len(rows)}")
    for failure_type, count in sorted(counts.items()):
        print(f"  {failure_type}: {count}")
    print()


def print_top_patterns(parser, split, patterns, top_n=10):
    """Print top error patterns for terminal inspection."""
    print(f"Top {top_n} error patterns ({parser} {split})")
    print("-" * 40)
    for row in patterns[:top_n]:
        print(
            f"{row['count']:>5}  "
            f"{clean(row['gold_karaka'])} | "
            f"{clean(row['deprel'])} | "
            f"{clean(row['case_marker'])} | "
            f"{row['failure_type']} | "
            f"{clean(row['strict_prediction'])}"
        )
    print()


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze final correction-layer error patterns.",
    )
    parser.add_argument(
        "--split",
        choices=sorted(SPLITS),
        required=True,
        help="Dataset split to analyze.",
    )
    parser.add_argument(
        "--parser",
        choices=sorted(PARSERS),
        required=True,
        help="Parser branch to analyze.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    split = args.split
    parser_name = args.parser

    gold_rows = split_gold_rows(load_csv(GOLD_PATH), split)
    pipeline_path = resolve_corrected_path(parser_name, split)
    pipeline_rows = load_csv(pipeline_path)
    rows = analyze_rows(gold_rows, pipeline_rows, split)

    failure_by_karaka = build_failure_by_karaka(rows)
    error_patterns = build_error_patterns(rows)
    detailed_patterns = build_detailed_error_patterns(rows)
    confusion_summary = build_confusion_summary(rows)
    karma_sampradana = filter_karaka_cases(rows, KARMA_SAMPRADANA)
    karana_apadana = filter_karaka_cases(rows, KARANA_APADANA)
    h1_success_rows = build_h1_success_rows(rows)

    write_csv(output_path(parser_name, split, "final_error_rows"), rows, ROW_FIELDS)
    write_csv(
        output_path(parser_name, split, "failure_by_karaka"),
        failure_by_karaka,
        FAILURE_BY_KARAKA_FIELDS,
    )
    write_csv(
        output_path(parser_name, split, "error_patterns"),
        error_patterns,
        ERROR_PATTERN_FIELDS,
    )
    write_csv(
        output_path(parser_name, split, "confusion_summary"),
        confusion_summary,
        CONFUSION_FIELDS,
    )
    write_csv(
        output_path(parser_name, split, "karma_sampradana_cases"),
        karma_sampradana,
        ROW_FIELDS,
    )
    write_csv(
        output_path(parser_name, split, "karana_apadana_cases"),
        karana_apadana,
        ROW_FIELDS,
    )
    write_csv(
        output_path(parser_name, split, "h1_success_rows"),
        h1_success_rows,
        ROW_FIELDS,
    )

    print_failure_summary(parser_name, split, rows)
    print_top_patterns(parser_name, split, detailed_patterns)
    print(f"H1 success rows: {len(h1_success_rows)}")
    print(f"Loaded corrected pipeline: {pipeline_path}")
    print(f"Saved outputs under: {OUTPUTS_ERROR_ANALYSIS}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
