"""
Save example rows for top actionable neural-only error patterns.
"""

import csv
from pathlib import Path


INPUT_PATH = Path("output/dev_actionable_neural_errors.csv")
OUTPUT_PATH = Path("output/top_actionable_error_examples.csv")
EXAMPLES_PER_PATTERN = 20

PATTERNS = [
    {
        "pattern_id": "adhikarana_nmod_mein",
        "gold_karaka": "Adhikarana",
        "deprel": "nmod",
        "case_marker": "में",
    },
    {
        "pattern_id": "karta_obj_blank",
        "gold_karaka": "Karta",
        "deprel": "obj",
        "case_marker": "",
    },
    {
        "pattern_id": "karma_nsubj_blank",
        "gold_karaka": "Karma",
        "deprel": "nsubj",
        "case_marker": "",
    },
    {
        "pattern_id": "karma_obl_se",
        "gold_karaka": "Karma",
        "deprel": "obl",
        "case_marker": "से",
    },
]

OUTPUT_COLUMNS = [
    "pattern_id",
    "sent_id",
    "sentence_text",
    "token_form",
    "gold_karaka",
    "mapper_candidates",
    "deprel",
    "case_marker",
    "final_candidates",
    "verifier_rule_id",
]


def load_csv(filepath):
    """Load a UTF-8 CSV file as dictionaries."""
    with open(filepath, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(filepath, rows, fieldnames):
    """Write dictionaries to a UTF-8 CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def matches_pattern(row, pattern):
    """Return true when a row matches one configured pattern."""
    return (
        row["gold_karaka"] == pattern["gold_karaka"]
        and row["deprel"] == pattern["deprel"]
        and row["case_marker"] == pattern["case_marker"]
    )


def select_examples(rows):
    """Select up to 20 examples for each configured pattern."""
    examples = []

    for pattern in PATTERNS:
        matches = [
            row for row in rows
            if matches_pattern(row, pattern)
        ][:EXAMPLES_PER_PATTERN]

        for row in matches:
            examples.append({
                "pattern_id": pattern["pattern_id"],
                "sent_id": row["sent_id"],
                "sentence_text": row["sentence_text"],
                "token_form": row["token_form"],
                "gold_karaka": row["gold_karaka"],
                "mapper_candidates": row["mapper_candidates"],
                "deprel": row["deprel"],
                "case_marker": row["case_marker"],
                "final_candidates": row["final_candidates"],
                "verifier_rule_id": row["verifier_rule_id"],
            })

    return examples


def print_examples(examples):
    """Print a compact preview grouped by pattern."""
    for pattern in PATTERNS:
        pattern_examples = [
            row for row in examples
            if row["pattern_id"] == pattern["pattern_id"]
        ]
        print()
        print(f"{pattern['pattern_id']}: {len(pattern_examples)} examples")
        print("-" * 60)
        for row in pattern_examples:
            print(
                f"{row['sent_id']} | {row['token_form']} | "
                f"gold={row['gold_karaka']} mapper={row['mapper_candidates'] or '(blank)'}"
            )


def main():
    rows = load_csv(INPUT_PATH)
    examples = select_examples(rows)
    write_csv(OUTPUT_PATH, examples, OUTPUT_COLUMNS)

    print_examples(examples)
    print()
    print(f"Saved top actionable error examples to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
