"""
Run Pipeline v1 on a selected UD split parsed by Stanza.

This is a split-aware replacement for the train/dev Stanza baseline runners.
It does not change mapper or verifier logic.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = SRC_ROOT / "pipeline"

sys.path.insert(0, str(PIPELINE_DIR))

from run_gold_ud_pipeline import setup_utf8_output, write_csv
from run_stanza_pipeline_sample import process_stanza_sentence


SPLITS = {"train", "dev", "test"}


def load_conllu_sentence_texts(filepath):
    """Read sentence ids and raw sentence text from a CoNLL-U file."""
    sentences = []
    current_id = ""
    current_text = ""

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            if line.startswith("# sent_id = "):
                current_id = line[len("# sent_id = "):]
                continue

            if line.startswith("# text = "):
                current_text = line[len("# text = "):]
                continue

            if not line:
                if current_id and current_text:
                    sentences.append((current_id, current_text))
                current_id = ""
                current_text = ""

    if current_id and current_text:
        sentences.append((current_id, current_text))

    return sentences


def print_summary(split, rows, total_sentences):
    """Print summary counts for a Stanza baseline run."""
    final_counts = Counter(row["final_decision"] for row in rows)
    rule_counts = Counter(
        row["verifier_rule_id"] for row in rows if row["verifier_rule_id"]
    )
    meaningful_count = sum(
        1 for row in rows if row["final_decision"] != "no_decision"
    )

    print(f"Stanza {split} baseline summary")
    print("=" * 40)
    print(f"Total sentences processed: {total_sentences}")
    print(f"Total tokens processed:    {len(rows)}")
    print(f"Meaningful rows:           {meaningful_count}")
    print()
    print("Final decision counts:")
    for decision, count in sorted(final_counts.items()):
        print(f"  {decision}: {count}")
    print()
    print("Verifier rule counts:")
    if rule_counts:
        for rule_id, count in sorted(rule_counts.items()):
            print(f"  {rule_id}: {count}")
    else:
        print("  (none)")


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run Stanza baseline for one split.",
    )
    parser.add_argument(
        "--split",
        choices=sorted(SPLITS),
        required=True,
        help="Dataset split to process.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    split = args.split
    project_root = Path(__file__).resolve().parent.parent.parent
    data_path = project_root / "data" / "raw" / f"hi_hdtb-ud-{split}.conllu"
    results_dir = project_root / "results"

    sentence_items = load_conllu_sentence_texts(data_path)
    print(f"Loaded {len(sentence_items)} {split} sentences from {data_path.name}")
    print()

    all_rows = []
    for index, (sent_id, sentence_text) in enumerate(sentence_items, start=1):
        print(f"Parsing {index}/{len(sentence_items)}: {sent_id}")
        all_rows.extend(process_stanza_sentence(sentence_text, sent_id))

    meaningful_rows = [
        row for row in all_rows if row["final_decision"] != "no_decision"
    ]

    all_csv = results_dir / f"stanza_{split}_baseline_all.csv"
    meaningful_csv = results_dir / f"stanza_{split}_baseline_meaningful.csv"

    write_csv(all_rows, all_csv)
    write_csv(meaningful_rows, meaningful_csv)

    print()
    print(f"Saved all rows:        {all_csv}")
    print(f"Saved meaningful rows: {meaningful_csv}")
    print()
    print_summary(split, all_rows, len(sentence_items))


if __name__ == "__main__":
    setup_utf8_output()
    main()
