"""
Run the v1 mapper and verifier together on gold UD sentences.

Loads the first 50 sentences from Hindi-HDTB train CONLL-U, maps each token
with map_ud_to_karaka(), verifies with verify_token(), and writes combined CSVs.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SRC_ROOT))
sys.path.insert(0, str(SRC_ROOT / "mapper"))
sys.path.insert(0, str(SRC_ROOT / "verifier"))

from paths import STANZA_GOLD_UD

from simple_mapper import map_ud_to_karaka
from simple_verifier import verify_token


CSV_FIELDS = [
    "sent_id",
    "sentence_text",
    "token_form",
    "deprel",
    "case_marker",
    "mapper_candidates",
    "mapper_confidence",
    "mapper_status",
    "verifier_candidates",
    "verifier_decision",
    "verifier_confidence",
    "verifier_rule_id",
    "final_candidates",
    "final_decision",
    "final_reason",
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


def join_candidates(candidates):
    """Join Karaka candidates with a pipe for CSV output."""
    return "|".join(candidates)


def combine_results(mapper_result, verifier_result):
    """
    Merge mapper and verifier outputs into final v1 fields.

    Priority:
      confirmed / ambiguous  -> verifier wins
      no_decision + mapper candidates -> mapping_hypothesis
      otherwise -> no_decision
    """
    mapper_candidates = mapper_result["karaka_candidates"]
    verifier_candidates = verifier_result["karaka_candidates"]
    verifier_decision = verifier_result["decision_type"]

    if verifier_decision == "confirmed":
        return {
            "final_candidates": join_candidates(verifier_candidates),
            "final_decision": "confirmed",
            "final_reason": verifier_result["reason"],
        }

    if verifier_decision == "ambiguous":
        return {
            "final_candidates": join_candidates(verifier_candidates),
            "final_decision": "ambiguous",
            "final_reason": verifier_result["reason"],
        }

    if mapper_candidates:
        return {
            "final_candidates": join_candidates(mapper_candidates),
            "final_decision": "mapping_hypothesis",
            "final_reason": mapper_result["reason"],
        }

    return {
        "final_candidates": "",
        "final_decision": "no_decision",
        "final_reason": (
            "Verifier returned no_decision and mapper provided no Karaka candidates."
        ),
    }


def process_sentence(sentence):
    """Run mapper and verifier on every token in one sentence."""
    tokens = sentence["tokens"]

    for token in tokens:
        case_marker = find_case_marker(token["id"], tokens)
        mapper_result = map_ud_to_karaka(token["deprel"])
        verifier_result = verify_token(token["deprel"], case_marker)
        final = combine_results(mapper_result, verifier_result)

        yield {
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
        }


def process_batch(sentences):
    """Run the pipeline on all sentences and return a list of row dicts."""
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
    """Print pipeline summary counts."""
    final_counts = Counter(row["final_decision"] for row in rows)
    rule_counts = Counter(
        row["verifier_rule_id"] for row in rows if row["verifier_rule_id"]
    )
    mapper_status_counts = Counter(row["mapper_status"] for row in rows)

    meaningful_count = sum(
        1 for row in rows if row["final_decision"] != "no_decision"
    )

    print("Gold UD pipeline summary")
    print("-" * 40)
    print(f"Total tokens processed: {len(rows)}")
    print(f"Meaningful (final_decision != no_decision): {meaningful_count}")
    print()
    print("Final decision counts (mapping_hypothesis = unverified mapper guess):")
    for decision, count in sorted(final_counts.items()):
        print(f"  {decision}: {count}")
    print()
    print("Verifier rule counts:")
    if rule_counts:
        for rule_id, count in sorted(rule_counts.items()):
            print(f"  {rule_id}: {count}")
    else:
        print("  (none)")
    print()
    print("Mapper status counts:")
    for status, count in sorted(mapper_status_counts.items()):
        print(f"  {status}: {count}")


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    data_path = project_root / "data" / "raw" / "hi_hdtb-ud-train.conllu"

    sentences = load_conllu(data_path, max_sentences=MAX_SENTENCES)
    print(f"Loaded {len(sentences)} sentences from {data_path.name}")

    all_rows = process_batch(sentences)
    meaningful_rows = [
        row for row in all_rows if row["final_decision"] != "no_decision"
    ]

    all_csv = STANZA_GOLD_UD / "gold_ud_pipeline_all.csv"
    meaningful_csv = STANZA_GOLD_UD / "gold_ud_pipeline_meaningful.csv"

    write_csv(all_rows, all_csv)
    write_csv(meaningful_rows, meaningful_csv)

    print(f"Saved all rows:        {all_csv}")
    print(f"Saved meaningful rows: {meaningful_csv}")
    print()
    print_summary(all_rows)


if __name__ == "__main__":
    setup_utf8_output()
    main()
