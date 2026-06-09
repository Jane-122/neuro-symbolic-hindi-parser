"""
Run the v1 token-level verifier on real CONLL-U sentences.

Loads a small sample from Hindi-HDTB, finds each token's deprel and
any child case marker, then calls verify_token() from simple_verifier.py.
"""

import sys
from pathlib import Path

# Import sibling module when run as a script from project root or this folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simple_verifier import verify_token


def load_conllu(filepath, max_sentences=None):
    """
    Read a CONLL-U file and return a list of sentence dictionaries.

    Each sentence has: text, sent_id, tokens (list of dicts with id, form, head, deprel).
    """
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
    """
    Return the form of the first child case token attached to this token.

    A case child is any token whose head points to token_id and deprel is 'case'.
    Returns None if no case child exists.
    """
    for token in tokens:
        if token["head"] == token_id and token["deprel"] == "case":
            return token["form"]
    return None


def run_verifier_on_sentence(sentence):
    """
    Run verify_token() on every token in one sentence.

    Yields one result dict per token with sentence and token context added.
    """
    tokens = sentence["tokens"]

    for token in tokens:
        case_marker = find_case_marker(token["id"], tokens)
        verifier_result = verify_token(token["deprel"], case_marker)

        yield {
            "sentence_text": sentence["text"],
            "sent_id": sentence["sent_id"],
            "token_form": token["form"],
            "deprel": token["deprel"],
            "case_marker": case_marker,
            "verifier_result": verifier_result,
        }


def setup_utf8_output():
    """Configure UTF-8 output so Hindi text displays correctly in the terminal."""
    import os

    # Help child processes and Python 3.7+ UTF-8 mode on Windows.
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    # On Windows, switch the console code page to UTF-8 (CP 65001).
    if sys.platform == "win32":
        try:
            os.system("chcp 65001 >nul")
        except Exception:
            pass
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:
            pass


def format_token_row(row):
    """Format one token result as a single readable block."""
    vr = row["verifier_result"]
    case_display = row["case_marker"] if row["case_marker"] else "-"
    rule_display = vr["rule_id"] if vr["rule_id"] else "-"
    karakas_display = vr["karaka_candidates"] if vr["karaka_candidates"] else "[]"

    lines = [
        f"  Token:      {row['token_form']}",
        f"  Deprel:     {row['deprel']}",
        f"  Case:       {case_display}",
        f"  Rule:       {rule_display}",
        f"  Decision:   {vr['decision_type']}",
        f"  Confidence: {vr['confidence']}",
        f"  Karakas:    {karakas_display}",
    ]
    return "\n".join(lines)


def print_sentence_results(sentence, rows):
    """Print one sentence header, then all token verifier results beneath it."""
    print(f"--- {sentence['sent_id']} ---")
    print(f"Sentence: {sentence['text']}")
    print()

    for row in rows:
        print(format_token_row(row))
        print()


def main():
    # Path to training file relative to this script (src/verifier/ -> data/raw/)
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "hi_hdtb-ud-train.conllu"

    sentences = load_conllu(data_path, max_sentences=5)
    print(f"Loaded {len(sentences)} sentences from {data_path.name}\n")
    print("=" * 60)

    output_lines = []
    output_lines.append(f"Loaded {len(sentences)} sentences from {data_path.name}")
    output_lines.append("=" * 60)

    for sentence in sentences:
        rows = list(run_verifier_on_sentence(sentence))
        print_sentence_results(sentence, rows)
        print("=" * 60)

        output_lines.append(f"--- {sentence['sent_id']} ---")
        output_lines.append(f"Sentence: {sentence['text']}")
        output_lines.append("")
        for row in rows:
            output_lines.append(format_token_row(row))
            output_lines.append("")
        output_lines.append("=" * 60)

    # Save UTF-8 copy for easy viewing/copy-paste if the terminal font struggles.
    output_path = Path(__file__).resolve().parent.parent.parent / "results" / "run_on_sentence_output.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    print(f"\nSaved UTF-8 output to: {output_path}")


if __name__ == "__main__":
    setup_utf8_output()
    main()
