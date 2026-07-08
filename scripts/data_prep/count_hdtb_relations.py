"""
Count HDTB dependency relation labels in the aligned HDTB corpus.

The aligned corpus is defined by output/aligned_ud_hdtb_sentences.csv. Each
aligned row points to one sentence in the raw HDTB .dat files.
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
from collections import Counter, defaultdict
from pathlib import Path


ALIGNED_PATH = OUTPUTS_ALIGNMENT / 'aligned_ud_hdtb_sentences.csv'
RAW_HDTB_ROOT = Path("data/raw/news_articles_and_heritage")
OUTPUT_PATH = OUTPUTS_GOLD / 'hdtb_relation_counts.csv'

DEPREL_COLUMN = 7
SPECIFIC_RELATIONS = [
    "k1",
    "k2",
    "k3",
    "k4",
    "k5",
    "k7",
    "k7p",
    "k1s",
    "k2p",
    "k2s",
    "k4a",
]


def load_csv(filepath):
    """Load a UTF-8 CSV file as a list of dictionaries."""
    with open(filepath, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_counts(filepath, counts):
    """Write relation counts sorted by descending frequency."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["relation", "count"])
        writer.writeheader()
        for relation, count in counts.most_common():
            writer.writerow({
                "relation": relation,
                "count": count,
            })


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


def build_needed_sentences(aligned_rows):
    """Group aligned sentence indexes by HDTB split and filename."""
    needed = defaultdict(set)
    for row in aligned_rows:
        key = (row["hdtb_split"], row["hdtb_file"])
        needed[key].add(int(row["hdtb_sentence_index"]))
    return needed


def count_relations(aligned_rows):
    """Count dependency labels from aligned HDTB sentences."""
    needed = build_needed_sentences(aligned_rows)
    counts = Counter()

    for (hdtb_split, hdtb_file), sentence_indexes in sorted(needed.items()):
        filepath = RAW_HDTB_ROOT / hdtb_split / hdtb_file
        sentences = read_sentences(filepath)

        for sentence_index in sentence_indexes:
            sentence = sentences[sentence_index - 1]
            for columns in sentence:
                if len(columns) <= DEPREL_COLUMN:
                    continue
                counts[columns[DEPREL_COLUMN]] += 1

    return counts


def print_report(counts):
    """Print top relation counts and selected karaka-style labels."""
    print("Top 50 HDTB dependency relations")
    print("=" * 50)
    print(f"{'relation':<20} {'count':>10}")
    for relation, count in counts.most_common(50):
        print(f"{relation:<20} {count:>10}")

    print()
    print("Selected relation counts")
    print("=" * 50)
    print(f"{'relation':<20} {'count':>10}")
    for relation in SPECIFIC_RELATIONS:
        print(f"{relation:<20} {counts[relation]:>10}")


def main():
    aligned_rows = load_csv(ALIGNED_PATH)
    counts = count_relations(aligned_rows)
    write_counts(OUTPUT_PATH, counts)
    print_report(counts)
    print()
    print(f"Saved relation counts to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
