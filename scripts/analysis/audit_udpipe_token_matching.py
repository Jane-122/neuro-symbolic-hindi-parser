"""
Audit gold Karaka token matching against UDPipe pipeline rows.

Uses the same matching key as Stanza evaluation:
split, sent_id, normalized token text, occurrence order.
"""

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import _bootstrap  # noqa: F401

from paths import (
    OUTPUTS_GOLD,
    udpipe_baseline_all,
    udpipe_token_matching_audit,
)

from audit_dev_token_matching import (
    OUTPUT_FIELDS,
    audit_matches,
    print_summary,
)
from evaluate_pipeline_against_gold import GOLD_PATH, load_csv, write_csv


SPLITS = {"train", "dev", "test"}


def split_gold_rows(rows, split):
    """Keep rows for one split where a gold karaka label exists."""
    return [
        row for row in rows
        if row["split"] == split and row["gold_karaka"]
    ]


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Audit UDPipe token matching against gold Karaka labels.",
    )
    parser.add_argument(
        "--split",
        choices=sorted(SPLITS),
        default="dev",
        help="Dataset split to audit, default: dev.",
    )
    return parser.parse_args()


def print_unmatched_examples(audit_rows, limit=10):
    """Print sample unmatched gold rows when match rate is low."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    unmatched = [row for row in audit_rows if row["status"] == "unmatched_gold"]
    if not unmatched:
        return

    print()
    print(f"Sample unmatched gold rows (up to {limit}):")
    for row in unmatched[:limit]:
        print(
            f"  {row['sent_id']}\t{row['gold_token']}\t{row['gold_karaka']}"
        )


def main():
    args = parse_args()
    split = args.split

    gold_rows = split_gold_rows(load_csv(GOLD_PATH), split)
    pipeline_rows = load_csv(udpipe_baseline_all(split))
    audit_rows, counts = audit_matches(gold_rows, pipeline_rows, split)

    output_path = udpipe_token_matching_audit(split)
    write_csv(output_path, audit_rows, OUTPUT_FIELDS)
    print_summary(counts)

    total_gold = counts["total_gold"]
    matched = counts["matched"]
    match_rate = (matched / total_gold * 100) if total_gold else 0.0
    if match_rate < 98.0:
        print_unmatched_examples(audit_rows)

    print()
    print(f"Saved UDPipe token matching audit to: {output_path}")


if __name__ == "__main__":
    main()
