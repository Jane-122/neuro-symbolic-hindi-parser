"""
Compare candidate-set and strict metrics on dev gold Karaka labels.

Systems:
- neural_only: mapper_candidates from the Stanza dev baseline
- neurosymbolic: final_candidates from the Stanza dev baseline
"""

from pathlib import Path

from evaluate_pipeline_against_gold import (
    DEV_SPLIT,
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


OUTPUT_PATH = Path("output/dev_metrics_strict_vs_candidate.csv")

SYSTEMS = [
    ("neural_only", "mapper_candidates"),
    ("neurosymbolic", "final_candidates"),
]

MODES = [
    "candidate_set",
    "strict",
]

OUTPUT_FIELDS = [
    "system",
    "mode",
    "metric_scope",
    "karaka",
    "support",
    "tp",
    "fp",
    "fn",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "macro_precision",
    "macro_recall",
    "macro_f1",
]


def get_predicted_labels(candidates, mode):
    """Return predicted labels for metric counting under one evaluation mode."""
    if mode == "candidate_set":
        return candidates
    if mode == "strict" and len(candidates) == 1:
        return candidates
    return set()


def is_correct(gold_label, candidates, mode):
    """Return whether a row is correct under the requested mode."""
    if mode == "candidate_set":
        return gold_label in candidates
    return len(candidates) == 1 and gold_label in candidates


def evaluate_rows(gold_rows, pipeline_rows, candidate_column):
    """Join dev gold rows to pipeline rows and parse candidate labels."""
    pipeline_index = build_pipeline_index(pipeline_rows)
    evaluated_rows = []

    for gold_row in gold_rows:
        key = (
            DEV_SPLIT,
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )
        pipeline_row = pipeline_index[key].popleft() if pipeline_index[key] else None
        candidates = (
            parse_candidates(pipeline_row[candidate_column])
            if pipeline_row
            else set()
        )

        evaluated_rows.append({
            "gold": gold_row["gold_karaka"],
            "candidates": candidates,
        })

    return evaluated_rows


def compute_mode_metrics(system_name, mode, evaluated_rows):
    """Compute overall, macro, and per-karaka metrics."""
    total = len(evaluated_rows)
    correct = sum(
        1 for row in evaluated_rows
        if is_correct(row["gold"], row["candidates"], mode)
    )
    accuracy = safe_divide(correct, total)

    per_karaka_rows = []
    precision_values = []
    recall_values = []
    f1_values = []

    for karaka in KARAKAS:
        tp = 0
        fp = 0
        fn = 0

        for row in evaluated_rows:
            predicted_labels = get_predicted_labels(row["candidates"], mode)
            gold_label = row["gold"]

            if gold_label == karaka and karaka in predicted_labels:
                tp += 1
            elif gold_label != karaka and karaka in predicted_labels:
                fp += 1
            elif gold_label == karaka and karaka not in predicted_labels:
                fn += 1

        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        f1 = safe_divide(2 * precision * recall, precision + recall)

        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)

        per_karaka_rows.append({
            "system": system_name,
            "mode": mode,
            "metric_scope": "per_karaka",
            "karaka": karaka,
            "support": tp + fn,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "accuracy": "",
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "macro_precision": "",
            "macro_recall": "",
            "macro_f1": "",
        })

    overall_row = {
        "system": system_name,
        "mode": mode,
        "metric_scope": "overall",
        "karaka": "ALL",
        "support": total,
        "tp": correct,
        "fp": "",
        "fn": "",
        "accuracy": accuracy,
        "precision": "",
        "recall": "",
        "f1": "",
        "macro_precision": safe_divide(sum(precision_values), len(precision_values)),
        "macro_recall": safe_divide(sum(recall_values), len(recall_values)),
        "macro_f1": safe_divide(sum(f1_values), len(f1_values)),
    }

    return [overall_row] + per_karaka_rows


def print_compact_table(rows):
    """Print system, mode, accuracy, and macro F1 for overall rows."""
    print(f"{'system':<16} {'mode':<15} {'accuracy':>10} {'macro_f1':>10}")
    print("-" * 55)
    for row in rows:
        if row["metric_scope"] != "overall":
            continue
        print(
            f"{row['system']:<16} {row['mode']:<15} "
            f"{row['accuracy']:>10} {row['macro_f1']:>10}"
        )


def main():
    gold_rows = dev_gold_rows(load_csv(GOLD_PATH))
    pipeline_rows = load_csv(STANZA_PIPELINE_PATH)
    output_rows = []

    for system_name, candidate_column in SYSTEMS:
        evaluated_rows = evaluate_rows(gold_rows, pipeline_rows, candidate_column)
        for mode in MODES:
            output_rows.extend(compute_mode_metrics(system_name, mode, evaluated_rows))

    write_csv(OUTPUT_PATH, output_rows, OUTPUT_FIELDS)
    print_compact_table(output_rows)
    print()
    print(f"Saved strict vs candidate metrics to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
