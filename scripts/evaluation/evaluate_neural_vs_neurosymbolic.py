"""
Compare neural-only mapper candidates against neuro-symbolic final candidates.

Evaluation uses dev gold karaka labels and the same token matching /
normalization helpers as evaluate_pipeline_against_gold.py.
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


from evaluate_pipeline_against_gold import (
    DEV_SPLIT,
    EVAL_FIELDS,
    GOLD_PATH,
    KARAKAS,
    STANZA_PIPELINE_PATH,
    build_pipeline_index,
    dev_gold_rows,
    load_csv,
    normalize_token,
    parse_candidates,
    safe_divide,
    write_csv,
)
from pathlib import Path


NEURAL_ONLY_EVAL_PATH = OUTPUTS_METRICS / 'neural_only_eval.csv'
NEUROSYMBOLIC_EVAL_PATH = OUTPUTS_METRICS / 'neurosymbolic_eval.csv'


def evaluate_rows(gold_rows, pipeline_rows, candidate_column):
    """Join gold and pipeline rows, then evaluate one candidate source."""
    pipeline_index = build_pipeline_index(pipeline_rows)
    evaluated = []

    for gold_row in gold_rows:
        key = (
            DEV_SPLIT,
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )
        pipeline_row = (
            pipeline_index[key].popleft()
            if pipeline_index[key]
            else None
        )
        candidates = (
            parse_candidates(pipeline_row[candidate_column])
            if pipeline_row
            else set()
        )

        evaluated.append({
            "gold": gold_row["gold_karaka"],
            "predicted": candidates,
        })

    return evaluated


def compute_eval_summary(system_name, evaluated_rows):
    """Compute overall accuracy and per-karaka precision/recall/F1."""
    total = len(evaluated_rows)
    correct = sum(1 for row in evaluated_rows if row["gold"] in row["predicted"])
    accuracy = safe_divide(correct, total)

    rows = [{
        "system": system_name,
        "metric_scope": "overall",
        "karaka": "ALL",
        "support": total,
        "tp": correct,
        "fp": "",
        "fn": "",
        "precision": "",
        "recall": "",
        "f1": "",
        "accuracy": accuracy,
    }]

    for karaka in KARAKAS:
        tp = sum(
            1 for row in evaluated_rows
            if row["gold"] == karaka and karaka in row["predicted"]
        )
        fp = sum(
            1 for row in evaluated_rows
            if row["gold"] != karaka and karaka in row["predicted"]
        )
        fn = sum(
            1 for row in evaluated_rows
            if row["gold"] == karaka and karaka not in row["predicted"]
        )
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        f1 = safe_divide(2 * precision * recall, precision + recall)

        rows.append({
            "system": system_name,
            "metric_scope": "per_karaka",
            "karaka": karaka,
            "support": tp + fn,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "accuracy": "",
        })

    return rows


def run_eval(system_name, pipeline_rows, candidate_column, output_path, gold_rows):
    """Evaluate one candidate column and write its metrics CSV."""
    evaluated_rows = evaluate_rows(gold_rows, pipeline_rows, candidate_column)
    eval_rows = compute_eval_summary(system_name, evaluated_rows)
    write_csv(output_path, eval_rows, EVAL_FIELDS)
    return eval_rows[0]["accuracy"]


def main():
    gold_rows = dev_gold_rows(load_csv(GOLD_PATH))
    pipeline_rows = load_csv(STANZA_PIPELINE_PATH)

    neural_accuracy = run_eval(
        "neural_only",
        pipeline_rows,
        "mapper_candidates",
        NEURAL_ONLY_EVAL_PATH,
        gold_rows,
    )
    neurosymbolic_accuracy = run_eval(
        "neurosymbolic",
        pipeline_rows,
        "final_candidates",
        NEUROSYMBOLIC_EVAL_PATH,
        gold_rows,
    )

    absolute_improvement = round(neurosymbolic_accuracy - neural_accuracy, 4)
    relative_improvement = safe_divide(absolute_improvement, neural_accuracy)

    print(f"Neural Only Accuracy: {neural_accuracy}")
    print(f"Neuro-Symbolic Accuracy: {neurosymbolic_accuracy}")
    print(f"Absolute Improvement: {absolute_improvement}")
    print(f"Relative Improvement (%): {round(relative_improvement * 100, 2)}")
    print(f"Saved neural-only eval to: {NEURAL_ONLY_EVAL_PATH}")
    print(f"Saved neuro-symbolic eval to: {NEUROSYMBOLIC_EVAL_PATH}")


if __name__ == "__main__":
    main()
