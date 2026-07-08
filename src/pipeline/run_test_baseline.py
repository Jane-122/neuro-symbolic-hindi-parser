"""
Run Pipeline v1 on the full Hindi-HDTB test split and save baseline CSV outputs.

Reuses processing logic from run_gold_ud_pipeline.py.
No mapper, verifier, or rule changes.
"""

import sys
from collections import Counter
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent
SRC_ROOT = PIPELINE_DIR.parent
sys.path.insert(0, str(SRC_ROOT))
sys.path.insert(0, str(PIPELINE_DIR))

from paths import STANZA_GOLD_UD

from run_gold_ud_pipeline import (
    load_conllu,
    process_batch,
    setup_utf8_output,
    write_csv,
)


def print_test_summary(rows, num_sentences):
    """Print baseline statistics for the test split."""
    final_counts = Counter(row["final_decision"] for row in rows)
    rule_counts = Counter(
        row["verifier_rule_id"] for row in rows if row["verifier_rule_id"]
    )
    mapper_status_counts = Counter(row["mapper_status"] for row in rows)
    deprel_counts = Counter(row["deprel"] for row in rows)

    meaningful_count = sum(
        1 for row in rows if row["final_decision"] != "no_decision"
    )

    print("Test baseline summary (Pipeline v1)")
    print("-" * 40)
    print(f"Total sentences: {num_sentences}")
    print(f"Total tokens:    {len(rows)}")
    print(f"Meaningful (final_decision != no_decision): {meaningful_count}")
    print()
    print("Final decision counts:")
    for decision, count in sorted(final_counts.items()):
        print(f"  {decision}: {count}")
    print()
    print("Mapper status counts:")
    for status, count in sorted(mapper_status_counts.items()):
        print(f"  {status}: {count}")
    print()
    print("Verifier rule counts:")
    if rule_counts:
        for rule_id, count in sorted(rule_counts.items()):
            print(f"  {rule_id}: {count}")
    else:
        print("  (none)")
    print()
    print("Deprel counts (top 15):")
    for deprel, count in deprel_counts.most_common(15):
        print(f"  {deprel}: {count}")


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    data_path = project_root / "data" / "raw" / "hi_hdtb-ud-test.conllu"

    sentences = load_conllu(data_path)
    print(f"Loaded {len(sentences)} sentences from {data_path.name}")

    all_rows = process_batch(sentences)
    meaningful_rows = [
        row for row in all_rows if row["final_decision"] != "no_decision"
    ]

    all_csv = STANZA_GOLD_UD / "test_baseline_all.csv"
    meaningful_csv = STANZA_GOLD_UD / "test_baseline_meaningful.csv"

    write_csv(all_rows, all_csv)
    write_csv(meaningful_rows, meaningful_csv)

    print(f"Saved all rows:        {all_csv}")
    print(f"Saved meaningful rows: {meaningful_csv}")
    print()
    print_test_summary(all_rows, len(sentences))


if __name__ == "__main__":
    setup_utf8_output()
    main()
