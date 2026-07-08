"""
Inspect unmatched UD sentences against nearby HDTB candidates.

For each split, this script prints the first 30 unmatched UD sentences and
their top 3 closest HDTB sentence candidates by SequenceMatcher similarity.
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
import difflib
from collections import defaultdict
from pathlib import Path


UNMATCHED_PATH = OUTPUTS_ALIGNMENT / 'alignment_unmatched_ud.csv'
HDTB_PATH = OUTPUTS_GOLD / 'hdtb_sentences.csv'
OUTPUT_PATH = OUTPUTS_ALIGNMENT / 'unmatched_nearest_candidates.csv'

SPLIT_MAP = {
    "train": "Training",
    "dev": "Development",
    "test": "Testing",
}

OUTPUT_FIELDS = [
    "ud_split",
    "ud_sent_id",
    "ud_text",
    "hdtb_split",
    "hdtb_file",
    "hdtb_sentence_index",
    "hdtb_text",
    "similarity_score",
]


def load_csv(filepath):
    """Load a UTF-8 CSV file as a list of dictionaries."""
    with open(filepath, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(filepath, rows, fieldnames):
    """Write rows to a UTF-8 CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def similarity(left, right):
    """Return SequenceMatcher similarity ratio."""
    return difflib.SequenceMatcher(None, left, right).ratio()


def top_candidates(ud_text, hdtb_rows, limit=3):
    """Find the top matching HDTB sentences for one UD sentence."""
    ud_length = len(ud_text)
    min_length = max(0, int(ud_length * 0.5))
    max_length = int(ud_length * 1.5) + 20
    length_filtered = [
        row for row in hdtb_rows
        if min_length <= len(row["sentence_text"]) <= max_length
    ]

    quick_scored = []
    for row in length_filtered:
        matcher = difflib.SequenceMatcher(None, ud_text, row["sentence_text"])
        quick_scored.append((matcher.quick_ratio(), row))
    quick_scored.sort(key=lambda item: item[0], reverse=True)

    shortlist = [row for _, row in quick_scored[:50]]
    scored = []
    for row in shortlist:
        score = similarity(ud_text, row["sentence_text"])
        scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:limit]


def main():
    unmatched_rows = load_csv(UNMATCHED_PATH)
    hdtb_rows = load_csv(HDTB_PATH)

    unmatched_by_split = defaultdict(list)
    hdtb_by_split = defaultdict(list)

    for row in unmatched_rows:
        unmatched_by_split[row["ud_split"]].append(row)

    for row in hdtb_rows:
        hdtb_by_split[row["split"]].append(row)

    output_rows = []

    for ud_split in ["train", "dev", "test"]:
        hdtb_split = SPLIT_MAP[ud_split]
        selected_unmatched = unmatched_by_split[ud_split][:30]
        hdtb_candidates = hdtb_by_split[hdtb_split]

        print(f"{ud_split} unmatched UD sentences")
        print("=" * 80)
        print(f"HDTB candidate split: {hdtb_split}")
        print(f"Unmatched shown: {len(selected_unmatched)}")
        print()

        for index, ud_row in enumerate(selected_unmatched, start=1):
            candidates = top_candidates(
                ud_row["ud_text"],
                hdtb_candidates,
                limit=3,
            )

            print(f"{index}. {ud_row['ud_sent_id']}")
            print(f"UD: {ud_row['ud_text']}")

            for rank, (score, hdtb_row) in enumerate(candidates, start=1):
                print(
                    f"  Candidate {rank}: score={score:.4f}, "
                    f"file={hdtb_row['file_name']}, "
                    f"sentence_index={hdtb_row['sentence_index']}"
                )
                print(f"  HDTB: {hdtb_row['sentence_text']}")

                output_rows.append({
                    "ud_split": ud_row["ud_split"],
                    "ud_sent_id": ud_row["ud_sent_id"],
                    "ud_text": ud_row["ud_text"],
                    "hdtb_split": hdtb_row["split"],
                    "hdtb_file": hdtb_row["file_name"],
                    "hdtb_sentence_index": hdtb_row["sentence_index"],
                    "hdtb_text": hdtb_row["sentence_text"],
                    "similarity_score": f"{score:.4f}",
                })

            print()

    write_csv(OUTPUT_PATH, output_rows, OUTPUT_FIELDS)
    print(f"Saved nearest candidates to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
