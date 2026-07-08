"""
Build accepted UD to HDTB sentence alignments.

The script uses the same normalization policy as alignment_audit_v2.py. Exact
normalized matches are accepted first. Remaining sentences use the best
SequenceMatcher candidate from the corresponding HDTB split and accept only
scores of 0.98 or higher.
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
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


UD_PATH = OUTPUTS_GOLD / 'ud_sentences.csv'
HDTB_PATH = OUTPUTS_GOLD / 'hdtb_sentences.csv'
ALIGNED_PATH = OUTPUTS_ALIGNMENT / 'aligned_ud_hdtb_sentences.csv'
UNMATCHED_PATH = OUTPUTS_ALIGNMENT / 'aligned_ud_hdtb_unmatched.csv'

SPLIT_MAP = {
    "train": "Training",
    "dev": "Development",
    "test": "Testing",
}

ALIGNED_FIELDS = [
    "ud_split",
    "ud_sent_id",
    "ud_text",
    "hdtb_split",
    "hdtb_file",
    "hdtb_sentence_index",
    "hdtb_text",
    "match_type",
    "similarity_score",
]

UNMATCHED_FIELDS = [
    "ud_split",
    "ud_sent_id",
    "ud_text",
    "best_hdtb_split",
    "best_hdtb_file",
    "best_hdtb_sentence_index",
    "best_hdtb_text",
    "best_similarity_score",
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


def build_hdtb_indexes(hdtb_rows):
    """Build split indexes with normalized text cached."""
    by_split = defaultdict(list)
    exact_index = defaultdict(lambda: defaultdict(list))

    for row in hdtb_rows:
        normalized = normalize_sentence(row["sentence_text"])
        indexed = {
            **row,
            "normalized_text": normalized,
            "normalized_length": len(normalized),
        }
        by_split[row["split"]].append(indexed)
        exact_index[row["split"]][normalized].append(indexed)

    return by_split, exact_index


def make_aligned_row(ud_row, hdtb_row, match_type, score):
    """Create one accepted alignment row."""
    return {
        "ud_split": ud_row["split"],
        "ud_sent_id": ud_row["sent_id"],
        "ud_text": ud_row["text"],
        "hdtb_split": hdtb_row["split"],
        "hdtb_file": hdtb_row["file_name"],
        "hdtb_sentence_index": hdtb_row["sentence_index"],
        "hdtb_text": hdtb_row["sentence_text"],
        "match_type": match_type,
        "similarity_score": f"{score:.4f}",
    }


def make_unmatched_row(ud_row, best_row, best_score):
    """Create one unmatched row with the best rejected candidate."""
    return {
        "ud_split": ud_row["split"],
        "ud_sent_id": ud_row["sent_id"],
        "ud_text": ud_row["text"],
        "best_hdtb_split": best_row.get("split", ""),
        "best_hdtb_file": best_row.get("file_name", ""),
        "best_hdtb_sentence_index": best_row.get("sentence_index", ""),
        "best_hdtb_text": best_row.get("sentence_text", ""),
        "best_similarity_score": f"{best_score:.4f}",
    }


def best_fuzzy_match(ud_text, hdtb_rows):
    """Return the best fuzzy candidate and score for one normalized sentence."""
    ud_length = len(ud_text)
    min_length = max(0, int(ud_length * 0.5))
    max_length = int(ud_length * 1.5) + 20
    shortlist = []

    for row in hdtb_rows:
        if not min_length <= row["normalized_length"] <= max_length:
            continue
        matcher = difflib.SequenceMatcher(None, ud_text, row["normalized_text"])
        if matcher.real_quick_ratio() >= 0.95:
            shortlist.append((matcher.quick_ratio(), row))

    shortlist.sort(key=lambda item: item[0], reverse=True)
    best_score = 0.0
    best_row = {}

    for _, row in shortlist[:50]:
        score = difflib.SequenceMatcher(
            None,
            ud_text,
            row["normalized_text"],
        ).ratio()
        if score > best_score:
            best_score = score
            best_row = row
        if best_score >= 0.98:
            break

    return best_row, best_score


def main():
    ud_rows = load_csv(UD_PATH)
    hdtb_rows = load_csv(HDTB_PATH)
    hdtb_by_split, hdtb_exact_index = build_hdtb_indexes(hdtb_rows)

    aligned = []
    unmatched = []
    summary = {}

    for ud_split, hdtb_split in SPLIT_MAP.items():
        split_ud_rows = [row for row in ud_rows if row["split"] == ud_split]
        counts = {
            "ud_sentences": len(split_ud_rows),
            "aligned": 0,
            "unmatched": 0,
            "exact": 0,
            "fuzzy": 0,
        }

        for ud_row in split_ud_rows:
            normalized = normalize_sentence(ud_row["text"])
            exact_candidates = hdtb_exact_index[hdtb_split].get(normalized, [])

            if exact_candidates:
                aligned.append(make_aligned_row(
                    ud_row,
                    exact_candidates[0],
                    "exact_normalized_match",
                    1.0,
                ))
                counts["aligned"] += 1
                counts["exact"] += 1
                continue

            best_row, best_score = best_fuzzy_match(
                normalized,
                hdtb_by_split[hdtb_split],
            )

            if best_score >= 0.98:
                aligned.append(make_aligned_row(
                    ud_row,
                    best_row,
                    "fuzzy_match_98",
                    best_score,
                ))
                counts["aligned"] += 1
                counts["fuzzy"] += 1
            else:
                unmatched.append(make_unmatched_row(ud_row, best_row, best_score))
                counts["unmatched"] += 1

        summary[ud_split] = counts

    write_csv(ALIGNED_PATH, aligned, ALIGNED_FIELDS)
    write_csv(UNMATCHED_PATH, unmatched, UNMATCHED_FIELDS)

    print("Aligned UD-HDTB sentence summary")
    print("=" * 78)
    print(
        f"{'split':<8} {'ud_sentences':>12} {'aligned':>9} "
        f"{'unmatched':>10} {'exact':>8} {'fuzzy':>8}"
    )
    for ud_split in SPLIT_MAP:
        row = summary[ud_split]
        print(
            f"{ud_split:<8} {row['ud_sentences']:>12} {row['aligned']:>9} "
            f"{row['unmatched']:>10} {row['exact']:>8} {row['fuzzy']:>8}"
        )


if __name__ == "__main__":
    main()
