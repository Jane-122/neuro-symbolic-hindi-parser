"""
Audit sentence alignment between UD-HDTB and original HDTB sentence exports.

Alignment is based only on normalized sentence text within the corresponding
split. This script does not perform fuzzy matching.
"""

import csv
import re
from collections import defaultdict
from pathlib import Path


UD_PATH = Path("output/ud_sentences.csv")
HDTB_PATH = Path("output/hdtb_sentences.csv")

MATCHES_PATH = Path("output/alignment_matches.csv")
UNMATCHED_PATH = Path("output/alignment_unmatched_ud.csv")
SUMMARY_PATH = Path("output/alignment_summary.csv")

SPLIT_MAP = {
    "train": "Training",
    "dev": "Development",
    "test": "Testing",
}

MATCH_FIELDS = [
    "ud_split",
    "ud_sent_id",
    "ud_text",
    "hdtb_split",
    "hdtb_file",
    "hdtb_sentence_index",
    "hdtb_text",
    "match_type",
]

UNMATCHED_FIELDS = [
    "ud_split",
    "ud_sent_id",
    "ud_text",
    "normalized_text",
]

SUMMARY_FIELDS = [
    "ud_split",
    "hdtb_split",
    "ud_sentences",
    "hdtb_sentences",
    "matched",
    "duplicates",
    "unmatched",
    "match_percentage",
]


def load_csv(filepath):
    """Load a UTF-8 CSV file as a list of dictionaries."""
    with open(filepath, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(filepath, rows, fieldnames):
    """Write dictionaries to a UTF-8 CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_sentence(text):
    """Normalize sentence text for exact sentence matching."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    tokens = [token for token in text.split(" ") if token != "NULL"]
    text = " ".join(tokens)
    text = re.sub(r"\s+([,\.\u0964\?\!;:\)\]])", r"\1", text)
    text = re.sub(r"([\(\[])\s+", r"\1", text)
    text = text.replace(" - ", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_hdtb_index(hdtb_rows):
    """Build normalized text indexes for each HDTB split."""
    index = defaultdict(lambda: defaultdict(list))
    split_counts = defaultdict(int)

    for row in hdtb_rows:
        split = row["split"]
        normalized = normalize_sentence(row["sentence_text"])
        split_counts[split] += 1
        index[split][normalized].append(row)

    return index, split_counts


def make_match_row(ud_row, hdtb_row, match_type):
    """Create one row for alignment_matches.csv."""
    return {
        "ud_split": ud_row["split"],
        "ud_sent_id": ud_row["sent_id"],
        "ud_text": ud_row["text"],
        "hdtb_split": hdtb_row.get("split", ""),
        "hdtb_file": hdtb_row.get("file_name", ""),
        "hdtb_sentence_index": hdtb_row.get("sentence_index", ""),
        "hdtb_text": hdtb_row.get("sentence_text", ""),
        "match_type": match_type,
    }


def main():
    ud_rows = load_csv(UD_PATH)
    hdtb_rows = load_csv(HDTB_PATH)
    hdtb_index, hdtb_split_counts = build_hdtb_index(hdtb_rows)

    matches = []
    unmatched = []
    summary = []

    for ud_split, hdtb_split in SPLIT_MAP.items():
        split_ud_rows = [row for row in ud_rows if row["split"] == ud_split]
        matched_count = 0
        duplicate_count = 0
        unmatched_count = 0

        for ud_row in split_ud_rows:
            normalized = normalize_sentence(ud_row["text"])
            candidates = hdtb_index[hdtb_split].get(normalized, [])

            if len(candidates) == 1:
                matched_count += 1
                matches.append(make_match_row(
                    ud_row,
                    candidates[0],
                    "exact_normalized_match",
                ))
            elif len(candidates) > 1:
                duplicate_count += 1
                for candidate in candidates:
                    matches.append(make_match_row(
                        ud_row,
                        candidate,
                        "duplicate_match",
                    ))
            else:
                unmatched_count += 1
                unmatched.append({
                    "ud_split": ud_row["split"],
                    "ud_sent_id": ud_row["sent_id"],
                    "ud_text": ud_row["text"],
                    "normalized_text": normalized,
                })

        total_ud = len(split_ud_rows)
        match_percentage = 100 * matched_count / total_ud if total_ud else 0
        summary.append({
            "ud_split": ud_split,
            "hdtb_split": hdtb_split,
            "ud_sentences": total_ud,
            "hdtb_sentences": hdtb_split_counts[hdtb_split],
            "matched": matched_count,
            "duplicates": duplicate_count,
            "unmatched": unmatched_count,
            "match_percentage": f"{match_percentage:.2f}",
        })

    write_csv(MATCHES_PATH, matches, MATCH_FIELDS)
    write_csv(UNMATCHED_PATH, unmatched, UNMATCHED_FIELDS)
    write_csv(SUMMARY_PATH, summary, SUMMARY_FIELDS)

    print("Alignment summary")
    print("=" * 90)
    print(
        f"{'ud_split':<8} {'hdtb_split':<12} {'ud':>8} {'hdtb':>8} "
        f"{'matched':>8} {'dupes':>8} {'unmatched':>10} {'match_%':>8}"
    )
    for row in summary:
        print(
            f"{row['ud_split']:<8} {row['hdtb_split']:<12} "
            f"{row['ud_sentences']:>8} {row['hdtb_sentences']:>8} "
            f"{row['matched']:>8} {row['duplicates']:>8} "
            f"{row['unmatched']:>10} {row['match_percentage']:>8}"
        )


if __name__ == "__main__":
    main()
