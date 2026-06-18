"""
Sanity-check extracted UD and HDTB sentence CSV files.

This script prints sample sentences and simple token-length statistics.
It does not perform alignment.
"""

import csv
from collections import defaultdict
from pathlib import Path


UD_PATH = Path("output/ud_sentences.csv")
HDTB_PATH = Path("output/hdtb_sentences.csv")


def load_csv(filepath):
    """Load a UTF-8 CSV file as a list of dictionaries."""
    with open(filepath, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def token_count(sentence_text):
    """Count whitespace-separated tokens in a sentence."""
    return len(sentence_text.split())


def print_first_sentences(rows, title, text_key, split_key, split_value, limit=20):
    """Print the first sentences from a selected split."""
    print(title)
    print("=" * len(title))

    selected = [row for row in rows if row[split_key] == split_value]
    for index, row in enumerate(selected[:limit], start=1):
        print(f"{index:>2}. {row[text_key]}")
    print()


def summarize_lengths(rows, source_name, text_key, split_key):
    """Print average and longest sentence length by split."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[split_key]].append(row)

    print(f"{source_name}: average sentence length by split")
    print("=" * (len(source_name) + 34))
    for split in sorted(grouped):
        lengths = [token_count(row[text_key]) for row in grouped[split]]
        average = sum(lengths) / len(lengths) if lengths else 0
        print(f"{split}: {average:.2f} tokens")
    print()

    print(f"{source_name}: longest sentence by split")
    print("=" * (len(source_name) + 27))
    for split in sorted(grouped):
        longest = max(grouped[split], key=lambda row: token_count(row[text_key]))
        length = token_count(longest[text_key])
        print(f"{split}: {length} tokens")
        print(longest[text_key])
        print()


def main():
    ud_rows = load_csv(UD_PATH)
    hdtb_rows = load_csv(HDTB_PATH)

    print_first_sentences(
        ud_rows,
        title="First 20 UD dev sentences",
        text_key="text",
        split_key="split",
        split_value="dev",
    )

    print_first_sentences(
        hdtb_rows,
        title="First 20 HDTB Development sentences",
        text_key="sentence_text",
        split_key="split",
        split_value="Development",
    )

    summarize_lengths(
        ud_rows,
        source_name="UD",
        text_key="text",
        split_key="split",
    )

    summarize_lengths(
        hdtb_rows,
        source_name="HDTB",
        text_key="sentence_text",
        split_key="split",
    )


if __name__ == "__main__":
    main()
