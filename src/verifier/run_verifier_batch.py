"""
Run the v1 verifier on a batch of Hindi-HDTB sentences and save CSV outputs.

Processes the first 50 sentences from the training CONLL-U file, applies
verify_token() to each token, and writes full + meaningful result tables.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simple_verifier import verify_token


# CSV column order
CSV_FIELDS = [
    "sent_id",
    "sentence_text",
    "token_form",
    "deprel",
    "case_marker",
    "rule_id",
    "decision_type",
    "confidence",
    "karaka_candidates",
    "reason",
]

MAX_SENTENCES = 50


def setup_utf8_output():
    """Configure UTF-8 terminal output on Windows."""
    import os

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    if sys.platform == "win32":
        try:
            os.system("chcp 65001 >nul")
        except Exception:
            pass


def load_conllu(filepath, max_sentences=None):
    """Read a CONLL-U file and return a list of sentence dictionaries."""
    sentences = []
    current = {"text": "", "sent_id": "", "tokens": []}

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            if not line:
                if current["tokens"]:
                    sentences.append(current)
                    if max_sentences and len(sentences) >= max_sentences:
                        break
                    current = {"text": "", "sent_id": "", "tokens": []}
                continue

            if line.startswith("#"):
                if line.startswith("# text = "):
                    current["text"] = line[len("# text = "):]
                elif line.startswith("# sent_id = "):
                    current["sent_id"] = line[len("# sent_id = "):]
                continue

            columns = line.split("\t")
            if len(columns) < 8 or "-" in columns[0]:
                continue

            current["tokens"].append({
                "id": columns[0],
                "form": columns[1],
                "head": columns[6],
                "deprel": columns[7],
            })

    if current["tokens"] and (not max_sentences or len(sentences) < max_sentences):
        sentences.append(current)

    return sentences


def find_case_marker(token_id, tokens):
    """Return the form of the first child case token, or None."""
    for token in tokens:
        if token["head"] == token_id and token["deprel"] == "case":
            return token["form"]
    return None


def process_sentence(sentence):
    """Run the verifier on every token in one sentence. Yield flat CSV rows."""
    tokens = sentence["tokens"]

    for token in tokens:
        case_marker = find_case_marker(token["id"], tokens)
        result = verify_token(token["deprel"], case_marker)
        karakas = "|".join(result["karaka_candidates"])

        yield {
            "sent_id": sentence["sent_id"],
            "sentence_text": sentence["text"],
            "token_form": token["form"],
            "deprel": token["deprel"],
            "case_marker": case_marker or "",
            "rule_id": result["rule_id"] or "",
            "decision_type": result["decision_type"],
            "confidence": result["confidence"],
            "karaka_candidates": karakas,
            "reason": result["reason"],
        }


def process_batch(sentences):
    """Run verifier on all sentences and return a list of row dicts."""
    rows = []
    for sentence in sentences:
        rows.extend(process_sentence(sentence))
    return rows


def write_csv(rows, filepath):
    """Write rows to a UTF-8 CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows):
    """Print verifier decision counts for the batch."""
    decision_counts = Counter(row["decision_type"] for row in rows)
    rule_counts = Counter(row["rule_id"] for row in rows if row["rule_id"])

    meaningful_count = sum(
        1 for row in rows if row["decision_type"] != "no_decision"
    )

    print("Verifier batch summary")
    print("-" * 40)
    print(f"Total tokens processed: {len(rows)}")
    print(f"Confirmed:              {decision_counts.get('confirmed', 0)}")
    print(f"Ambiguous:              {decision_counts.get('ambiguous', 0)}")
    print(f"No decision:            {decision_counts.get('no_decision', 0)}")
    print(f"Meaningful (not no_decision): {meaningful_count}")
    print()
    print("Count by rule_id:")
    if rule_counts:
        for rule_id, count in sorted(rule_counts.items()):
            print(f"  {rule_id}: {count}")
    else:
        print("  (none)")


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    data_path = project_root / "data" / "raw" / "hi_hdtb-ud-train.conllu"
    results_dir = project_root / "results"

    sentences = load_conllu(data_path, max_sentences=MAX_SENTENCES)
    print(f"Loaded {len(sentences)} sentences from {data_path.name}")

    all_rows = process_batch(sentences)
    meaningful_rows = [
        row for row in all_rows if row["decision_type"] != "no_decision"
    ]

    all_csv = results_dir / "verifier_batch_all.csv"
    meaningful_csv = results_dir / "verifier_batch_meaningful.csv"

    write_csv(all_rows, all_csv)
    write_csv(meaningful_rows, meaningful_csv)

    print(f"Saved all rows:        {all_csv}")
    print(f"Saved meaningful rows: {meaningful_csv}")
    print()
    print_summary(all_rows)


if __name__ == "__main__":
    setup_utf8_output()
    main()
