"""
Audit sentence alignment with improved normalization and fuzzy thresholds.

This script compares UD-HDTB sentences against original HDTB sentence exports
within the corresponding split. It writes a compact summary with exact match
counts and high-confidence SequenceMatcher match counts.
"""

import csv
import difflib
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


UD_PATH = Path("output/ud_sentences.csv")
HDTB_PATH = Path("output/hdtb_sentences.csv")
SUMMARY_PATH = Path("output/alignment_summary_v2.csv")

SPLIT_MAP = {
    "train": "Training",
    "dev": "Development",
    "test": "Testing",
}

SUMMARY_FIELDS = [
    "ud_split",
    "hdtb_split",
    "ud_sentences",
    "hdtb_sentences",
    "exact_match",
    "high_confidence_match_95",
    "high_confidence_match_98",
]

NUKTA_NORMALIZATION = str.maketrans({
    "\u0958": "\u0915\u093c",  # qa
    "\u0959": "\u0916\u093c",  # khha
    "\u095a": "\u0917\u093c",  # ghha
    "\u095b": "\u091c\u093c",  # za
    "\u095c": "\u0921\u093c",  # dddha
    "\u095d": "\u0922\u093c",  # rha
    "\u095e": "\u092b\u093c",  # fa
    "\u095f": "\u092f\u093c",  # yya
})


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


def normalize_nukta(text):
    """Normalize precomposed Devanagari nukta letters to explicit nukta forms."""
    return text.translate(NUKTA_NORMALIZATION)


def normalize_sentence(text):
    """Normalize Hindi sentence text for alignment comparisons."""
    text = unicodedata.normalize("NFC", text)
    text = normalize_nukta(text)
    text = re.sub(r"\bNULL\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    text = re.sub(r"\s*([,\.\u0964;:\?!])\s*", r"\1", text)
    text = re.sub(r"\(\s*", "(", text)
    text = re.sub(r"\s*\)", ")", text)
    text = re.sub(r"\[\s*", "[", text)
    text = re.sub(r"\s*\]", "]", text)
    text = re.sub(r"'\s+", "'", text)
    text = re.sub(r"\s+'", "'", text)
    text = re.sub(r'"\s+', '"', text)
    text = re.sub(r'\s+"', '"', text)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_split_rows(rows, split_field, text_field):
    """Group rows by split with cached normalized text and length."""
    grouped = defaultdict(list)
    for row in rows:
        normalized = normalize_sentence(row[text_field])
        grouped[row[split_field]].append({
            "text": normalized,
            "length": len(normalized),
        })
    return grouped


def build_exact_index(rows):
    """Build a set of normalized HDTB texts for each split."""
    index = defaultdict(set)
    for split, split_rows in rows.items():
        for row in split_rows:
            index[split].add(row["text"])
    return index


def max_similarity(ud_text, hdtb_rows):
    """Find the best SequenceMatcher score for one UD sentence."""
    ud_length = len(ud_text)
    min_length = max(0, int(ud_length * 0.5))
    max_length = int(ud_length * 1.5) + 20
    shortlist = []

    for row in hdtb_rows:
        if not min_length <= row["length"] <= max_length:
            continue
        matcher = difflib.SequenceMatcher(None, ud_text, row["text"])
        if matcher.real_quick_ratio() >= 0.95:
            shortlist.append((matcher.quick_ratio(), row["text"]))

    shortlist.sort(key=lambda item: item[0], reverse=True)
    best = 0.0

    for _, hdtb_text in shortlist[:50]:
        score = difflib.SequenceMatcher(None, ud_text, hdtb_text).ratio()
        if score > best:
            best = score
        if best >= 0.98:
            break

    return best


def main():
    ud_rows = load_csv(UD_PATH)
    hdtb_rows = load_csv(HDTB_PATH)

    ud_by_split = build_split_rows(ud_rows, "split", "text")
    hdtb_by_split = build_split_rows(hdtb_rows, "split", "sentence_text")
    hdtb_exact_index = build_exact_index(hdtb_by_split)

    summary = []

    for ud_split, hdtb_split in SPLIT_MAP.items():
        exact_match = 0
        high_confidence_95 = 0
        high_confidence_98 = 0

        for ud_row in ud_by_split[ud_split]:
            ud_text = ud_row["text"]

            if ud_text in hdtb_exact_index[hdtb_split]:
                exact_match += 1
                high_confidence_95 += 1
                high_confidence_98 += 1
                continue

            best_score = max_similarity(ud_text, hdtb_by_split[hdtb_split])
            if best_score >= 0.95:
                high_confidence_95 += 1
            if best_score >= 0.98:
                high_confidence_98 += 1

        summary.append({
            "ud_split": ud_split,
            "hdtb_split": hdtb_split,
            "ud_sentences": len(ud_by_split[ud_split]),
            "hdtb_sentences": len(hdtb_by_split[hdtb_split]),
            "exact_match": exact_match,
            "high_confidence_match_95": high_confidence_95,
            "high_confidence_match_98": high_confidence_98,
        })

    write_csv(SUMMARY_PATH, summary, SUMMARY_FIELDS)

    print("Alignment summary v2")
    print("=" * 100)
    print(
        f"{'ud_split':<8} {'hdtb_split':<12} {'ud':>8} {'hdtb':>8} "
        f"{'exact':>8} {'>=0.95':>8} {'>=0.98':>8}"
    )
    for row in summary:
        print(
            f"{row['ud_split']:<8} {row['hdtb_split']:<12} "
            f"{row['ud_sentences']:>8} {row['hdtb_sentences']:>8} "
            f"{row['exact_match']:>8} "
            f"{row['high_confidence_match_95']:>8} "
            f"{row['high_confidence_match_98']:>8}"
        )


if __name__ == "__main__":
    main()
