"""
Run Pipeline v1 on fixed Hindi sample sentences parsed with Stanza.

Parser integration v1 only. Does not modify mapper, verifier, or gold baselines.
"""

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

from paths import STANZA_BASELINE

from run_gold_ud_pipeline import (
    combine_results,
    find_case_marker,
    join_candidates,
    setup_utf8_output,
    write_csv,
)
from simple_mapper import map_ud_to_karaka
from simple_verifier import verify_token
from stanza_parser import parse_sentence_with_stanza


SAMPLE_SENTENCES = [
    ("sample-s1", "राम ने आम खाया।"),
    ("sample-s2", "सीता कमरे में बैठी।"),
    ("sample-s3", "बच्चा मेज पर बैठा।"),
    ("sample-s4", "मोहन चाकू से फल काटता है।"),
    ("sample-s5", "राम ने सीता को किताब दी।"),
]


def stanza_rows_to_sentence(sentence_text: str, stanza_rows: list[dict]) -> dict:
    """Convert Stanza token rows into the gold pipeline sentence format."""
    tokens = []
    for row in stanza_rows:
        tokens.append({
            "id": row["token_id"],
            "form": row["text"],
            "head": row["head"],
            "deprel": row["deprel"],
        })
    return {
        "sent_id": stanza_rows[0]["sent_id"] if stanza_rows else "",
        "text": sentence_text,
        "tokens": tokens,
    }


def process_stanza_sentence(sentence_text: str, sent_id: str) -> list[dict]:
    """Parse with Stanza, then run mapper and verifier on each token."""
    stanza_rows = parse_sentence_with_stanza(sentence_text, sent_id=sent_id)
    sentence = stanza_rows_to_sentence(sentence_text, stanza_rows)
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


def print_summary(rows):
    """Print summary counts for the Stanza sample run."""
    final_counts = Counter(row["final_decision"] for row in rows)
    rule_counts = Counter(
        row["verifier_rule_id"] for row in rows if row["verifier_rule_id"]
    )
    meaningful_count = sum(
        1 for row in rows if row["final_decision"] != "no_decision"
    )

    print("Stanza pipeline sample summary")
    print("-" * 40)
    print(f"Total tokens processed: {len(rows)}")
    print(f"Meaningful (final_decision != no_decision): {meaningful_count}")
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


def main():
    all_rows = []
    for sent_id, sentence_text in SAMPLE_SENTENCES:
        print(f"Parsing {sent_id}: {sentence_text}")
        all_rows.extend(process_stanza_sentence(sentence_text, sent_id))

    meaningful_rows = [
        row for row in all_rows if row["final_decision"] != "no_decision"
    ]

    all_csv = STANZA_BASELINE / "stanza_pipeline_sample_all.csv"
    meaningful_csv = STANZA_BASELINE / "stanza_pipeline_sample_meaningful.csv"

    write_csv(all_rows, all_csv)
    write_csv(meaningful_rows, meaningful_csv)

    print()
    print(f"Saved all rows:        {all_csv}")
    print(f"Saved meaningful rows: {meaningful_csv}")
    print()
    print_summary(all_rows)


if __name__ == "__main__":
    setup_utf8_output()
    main()
