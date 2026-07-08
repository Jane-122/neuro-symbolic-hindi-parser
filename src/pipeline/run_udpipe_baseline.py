"""
Run Pipeline v1 on a selected UD split parsed by UDPipe.

Mirrors run_stanza_baseline.py for parser robustness experiments.
Does not change mapper or verifier logic.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = SRC_ROOT / "pipeline"

sys.path.insert(0, str(SRC_ROOT))
sys.path.insert(0, str(SRC_ROOT / "mapper"))
sys.path.insert(0, str(SRC_ROOT / "verifier"))
sys.path.insert(0, str(SRC_ROOT / "parser"))
sys.path.insert(0, str(PIPELINE_DIR))

from paths import udpipe_baseline_all, udpipe_baseline_meaningful, ud_conllu

from run_gold_ud_pipeline import (
    combine_results,
    find_case_marker,
    join_candidates,
    setup_utf8_output,
    write_csv,
)
from simple_mapper import map_ud_to_karaka
from simple_verifier import verify_token
from udpipe_parser import parse_sentence_with_udpipe


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


def parser_rows_to_sentence(sentence_text: str, parser_rows: list[dict]) -> dict:
    """Convert UDPipe token rows into the gold pipeline sentence format."""
    tokens = []
    for row in parser_rows:
        tokens.append({
            "id": row["token_id"],
            "form": row["text"],
            "head": row["head"],
            "deprel": row["deprel"],
        })
    return {
        "sent_id": parser_rows[0]["sent_id"] if parser_rows else "",
        "text": sentence_text,
        "tokens": tokens,
    }


def process_udpipe_sentence(sentence_text: str, sent_id: str) -> list[dict]:
    """Parse with UDPipe, then run mapper and verifier on each token."""
    parser_rows = parse_sentence_with_udpipe(sentence_text, sent_id=sent_id)
    sentence = parser_rows_to_sentence(sentence_text, parser_rows)
    tokens = sentence["tokens"]
    output_rows = []

    for token in tokens:
        case_marker = find_case_marker(token["id"], tokens)
        mapper_result = map_ud_to_karaka(token["deprel"])
        verifier_result = verify_token(token["deprel"], case_marker)
        final = combine_results(mapper_result, verifier_result)

        output_rows.append({
            "sent_id": sentence["sent_id"],
            "sentence_text": sentence["text"],
            "token_form": token["form"],
            "deprel": token["deprel"],
            "case_marker": case_marker or "",
            "mapper_candidates": join_candidates(mapper_result["karaka_candidates"]),
            "mapper_confidence": mapper_result["confidence"],
            "mapper_status": mapper_result["mapping_status"],
            "verifier_candidates": join_candidates(verifier_result["karaka_candidates"]),
            "verifier_decision": verifier_result["decision_type"],
            "verifier_confidence": verifier_result["confidence"],
            "verifier_rule_id": verifier_result["rule_id"] or "",
            "final_candidates": final["final_candidates"],
            "final_decision": final["final_decision"],
            "final_reason": final["final_reason"],
        })

    return output_rows


def print_summary(split, rows, total_sentences):
    """Print summary counts for a UDPipe baseline run."""
    final_counts = Counter(row["final_decision"] for row in rows)
    rule_counts = Counter(
        row["verifier_rule_id"] for row in rows if row["verifier_rule_id"]
    )
    meaningful_count = sum(
        1 for row in rows if row["final_decision"] != "no_decision"
    )

    print(f"UDPipe {split} baseline summary")
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
        description="Run UDPipe baseline for one split.",
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
    data_path = ud_conllu(split)

    sentence_items = load_conllu_sentence_texts(data_path)
    print(f"Loaded {len(sentence_items)} {split} sentences from {data_path.name}")
    print()

    all_rows = []
    for index, (sent_id, sentence_text) in enumerate(sentence_items, start=1):
        print(f"Parsing {index}/{len(sentence_items)}: {sent_id}")
        all_rows.extend(process_udpipe_sentence(sentence_text, sent_id))

    meaningful_rows = [
        row for row in all_rows if row["final_decision"] != "no_decision"
    ]

    all_csv = udpipe_baseline_all(split)
    meaningful_csv = udpipe_baseline_meaningful(split)

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
