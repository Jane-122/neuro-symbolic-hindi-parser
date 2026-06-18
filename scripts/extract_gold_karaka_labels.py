"""
Extract gold karaka labels from aligned HDTB sentences.

The aligned corpus points each UD sentence to its matching raw HDTB sentence.
This script reads those raw sentences and keeps core Paninian karaka labels.
"""

import csv
from collections import Counter
from pathlib import Path


ALIGNED_PATH = Path("output/aligned_ud_hdtb_sentences.csv")
RAW_HDTB_ROOT = Path("data/raw/news_articles_and_heritage")
OUTPUT_PATH = Path("output/gold_karaka_labels.csv")

TOKEN_ID_COLUMN = 0
TOKEN_COLUMN = 1
HEAD_COLUMN = 6
RELATION_COLUMN = 7

KARAKA_MAP = {
    "k1": "Karta",
    "k2": "Karma",
    "k3": "Karana",
    "k4": "Sampradana",
    "k5": "Apadana",
    "k7": "Adhikarana",
    "k7p": "Adhikarana",
}

OUTPUT_COLUMNS = [
    "split",
    "ud_sent_id",
    "hdtb_file",
    "hdtb_sentence_index",
    "token_id",
    "token",
    "head",
    "paninian_label",
    "gold_karaka",
]


def load_csv(filepath):
    """Load a UTF-8 CSV file as a list of dictionaries."""
    with open(filepath, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_sentences(filepath):
    """Read one HDTB .dat file as blank-line-separated token rows."""
    sentences = []
    current = []

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip("\n")
            if not stripped.strip():
                if current:
                    sentences.append(current)
                    current = []
                continue
            current.append(stripped.split("\t"))

    if current:
        sentences.append(current)

    return sentences


def sentence_cache_key(aligned_row):
    """Return the raw HDTB sentence identity for one aligned row."""
    return (
        aligned_row["hdtb_split"],
        aligned_row["hdtb_file"],
        int(aligned_row["hdtb_sentence_index"]),
    )


def get_sentence(aligned_row, sentence_cache):
    """Read and cache a raw HDTB sentence referenced by an aligned row."""
    hdtb_split, hdtb_file, sentence_index = sentence_cache_key(aligned_row)
    key = (hdtb_split, hdtb_file)

    if key not in sentence_cache:
        filepath = RAW_HDTB_ROOT / hdtb_split / hdtb_file
        sentence_cache[key] = read_sentences(filepath)

    return sentence_cache[key][sentence_index - 1]


def extract_gold_labels(aligned_rows):
    """Extract filtered karaka labels from all aligned HDTB sentences."""
    sentence_cache = {}
    extracted_rows = []

    for aligned_row in aligned_rows:
        sentence = get_sentence(aligned_row, sentence_cache)

        for columns in sentence:
            if len(columns) <= RELATION_COLUMN:
                continue

            relation = columns[RELATION_COLUMN]
            if relation not in KARAKA_MAP:
                continue

            extracted_rows.append({
                "split": aligned_row["ud_split"],
                "ud_sent_id": aligned_row["ud_sent_id"],
                "hdtb_file": aligned_row["hdtb_file"],
                "hdtb_sentence_index": aligned_row["hdtb_sentence_index"],
                "token_id": columns[TOKEN_ID_COLUMN],
                "token": columns[TOKEN_COLUMN],
                "head": columns[HEAD_COLUMN],
                "paninian_label": relation,
                "gold_karaka": KARAKA_MAP[relation],
            })

    return extracted_rows


def write_gold_labels(filepath, rows):
    """Write extracted gold karaka labels to CSV."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def print_counter(title, counts):
    """Print one count table sorted by descending frequency."""
    print(title)
    print("=" * len(title))
    print(f"{'label':<20} {'count':>10}")
    for label, count in counts.most_common():
        print(f"{label:<20} {count:>10}")
    print()


def print_report(rows):
    """Print requested aggregate counts."""
    paninian_counts = Counter(row["paninian_label"] for row in rows)
    karaka_counts = Counter(row["gold_karaka"] for row in rows)
    split_counts = Counter(row["split"] for row in rows)

    print_counter("Counts by paninian_label", paninian_counts)
    print_counter("Counts by gold_karaka", karaka_counts)
    print_counter("Counts by split", split_counts)


def main():
    aligned_rows = load_csv(ALIGNED_PATH)
    extracted_rows = extract_gold_labels(aligned_rows)
    write_gold_labels(OUTPUT_PATH, extracted_rows)
    print_report(extracted_rows)
    print(f"Saved gold karaka labels to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
