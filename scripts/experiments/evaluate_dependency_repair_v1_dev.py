"""
Evaluate dependency-label repair v1 on dev.

This evaluates only dependency relation label accuracy. It does not evaluate
heads and does not compute UAS or LAS.
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


from collections import Counter, defaultdict, deque
from pathlib import Path

from evaluate_pipeline_against_gold import (
    DEV_SPLIT,
    load_csv,
    normalize_token,
    write_csv,
)


GOLD_CONLLU_PATH = Path("data/raw/hi_hdtb-ud-dev.conllu")
REPAIRED_PATH = REJECTED_DR1 / 'stanza_dev_dependency_repaired_v1_all.csv'
EVAL_PATH = OUTPUTS_REJECTED_DR1 / 'dependency_repair_v1_dev_eval.csv'
DR1_CASES_PATH = OUTPUTS_REJECTED_DR1 / 'dependency_repair_v1_dev_dr1_cases.csv'

EVAL_FIELDS = [
    "matched_tokens",
    "unmatched_gold_tokens",
    "original_correct",
    "repaired_correct",
    "original_deprel_accuracy",
    "repaired_deprel_accuracy",
    "dr1_repairs",
    "dr1_improved",
    "dr1_worsened",
    "dr1_unchanged_correct",
    "dr1_unchanged_wrong",
]

DR1_FIELDS = [
    "sent_id",
    "sentence_text",
    "token_form",
    "gold_deprel",
    "original_deprel",
    "corrected_deprel",
    "case_marker",
    "dependency_repair_rule_id",
    "effect",
]


def read_gold_tokens(filepath):
    """Read gold UD tokens from a CoNLL-U file."""
    rows = []
    current_sent_id = ""

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            if line.startswith("# sent_id = "):
                current_sent_id = line[len("# sent_id = "):]
                continue

            if not line or line.startswith("#"):
                continue

            columns = line.split("\t")
            if len(columns) < 8 or "-" in columns[0] or "." in columns[0]:
                continue

            rows.append({
                "sent_id": current_sent_id,
                "token_form": columns[1],
                "gold_deprel": columns[7],
            })

    return rows


def build_pipeline_index(rows):
    """Index pipeline rows by sent_id, normalized token text, and occurrence."""
    index = defaultdict(deque)
    for row in rows:
        key = (
            DEV_SPLIT,
            row["sent_id"],
            normalize_token(row["token_form"]),
        )
        index[key].append(row)
    return index


def repair_effect(gold_deprel, original_deprel, corrected_deprel):
    """Classify the effect of one dependency repair."""
    original_correct = original_deprel == gold_deprel
    repaired_correct = corrected_deprel == gold_deprel

    if not original_correct and repaired_correct:
        return "improved"
    if original_correct and not repaired_correct:
        return "worsened"
    if original_correct and repaired_correct:
        return "unchanged_correct"
    return "unchanged_wrong"


def evaluate(gold_rows, pipeline_rows):
    """Evaluate original and repaired deprel accuracy."""
    pipeline_index = build_pipeline_index(pipeline_rows)
    matched_tokens = 0
    unmatched_gold_tokens = 0
    original_correct = 0
    repaired_correct = 0
    dr1_cases = []
    dr1_effect_counts = Counter()

    for gold_row in gold_rows:
        key = (
            DEV_SPLIT,
            gold_row["sent_id"],
            normalize_token(gold_row["token_form"]),
        )
        pipeline_row = pipeline_index[key].popleft() if pipeline_index[key] else None

        if not pipeline_row:
            unmatched_gold_tokens += 1
            continue

        matched_tokens += 1
        gold_deprel = gold_row["gold_deprel"]
        original_deprel = pipeline_row["deprel"]
        corrected_deprel = pipeline_row["corrected_deprel"]

        if original_deprel == gold_deprel:
            original_correct += 1
        if corrected_deprel == gold_deprel:
            repaired_correct += 1

        if pipeline_row["dependency_repair_rule_id"] == "DR1_NMOD_LOCATIVE_TO_OBL":
            effect = repair_effect(gold_deprel, original_deprel, corrected_deprel)
            dr1_effect_counts[effect] += 1
            dr1_cases.append({
                "sent_id": pipeline_row["sent_id"],
                "sentence_text": pipeline_row["sentence_text"],
                "token_form": pipeline_row["token_form"],
                "gold_deprel": gold_deprel,
                "original_deprel": original_deprel,
                "corrected_deprel": corrected_deprel,
                "case_marker": pipeline_row["case_marker"],
                "dependency_repair_rule_id": pipeline_row["dependency_repair_rule_id"],
                "effect": effect,
            })

    eval_row = {
        "matched_tokens": matched_tokens,
        "unmatched_gold_tokens": unmatched_gold_tokens,
        "original_correct": original_correct,
        "repaired_correct": repaired_correct,
        "original_deprel_accuracy": round(original_correct / matched_tokens, 4),
        "repaired_deprel_accuracy": round(repaired_correct / matched_tokens, 4),
        "dr1_repairs": len(dr1_cases),
        "dr1_improved": dr1_effect_counts["improved"],
        "dr1_worsened": dr1_effect_counts["worsened"],
        "dr1_unchanged_correct": dr1_effect_counts["unchanged_correct"],
        "dr1_unchanged_wrong": dr1_effect_counts["unchanged_wrong"],
    }

    return eval_row, dr1_cases


def print_summary(eval_row):
    """Print compact dependency repair evaluation summary."""
    print("Dependency repair v1 dev evaluation")
    print("=" * 37)
    print(f"matched tokens: {eval_row['matched_tokens']}")
    print(f"unmatched gold tokens: {eval_row['unmatched_gold_tokens']}")
    print(f"original deprel accuracy: {eval_row['original_deprel_accuracy']}")
    print(f"repaired deprel accuracy: {eval_row['repaired_deprel_accuracy']}")
    print(f"DR1 repairs: {eval_row['dr1_repairs']}")
    print(f"DR1 improved: {eval_row['dr1_improved']}")
    print(f"DR1 worsened: {eval_row['dr1_worsened']}")
    print(f"DR1 unchanged_correct: {eval_row['dr1_unchanged_correct']}")
    print(f"DR1 unchanged_wrong: {eval_row['dr1_unchanged_wrong']}")


def main():
    gold_rows = read_gold_tokens(GOLD_CONLLU_PATH)
    pipeline_rows = load_csv(REPAIRED_PATH)
    eval_row, dr1_cases = evaluate(gold_rows, pipeline_rows)

    write_csv(EVAL_PATH, [eval_row], EVAL_FIELDS)
    write_csv(DR1_CASES_PATH, dr1_cases, DR1_FIELDS)

    print_summary(eval_row)
    print()
    print(f"Saved dependency repair eval to: {EVAL_PATH}")
    print(f"Saved DR1 cases to: {DR1_CASES_PATH}")


if __name__ == "__main__":
    main()
