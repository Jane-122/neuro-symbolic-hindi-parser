"""
Evaluate pipeline karaka candidates against extracted gold HDTB karaka labels.

For this first pass, evaluation is limited to the dev split because the
available pipeline result files are dev-only.
"""

import csv
from collections import Counter, defaultdict, deque
from pathlib import Path

from alignment_audit_v2 import normalize_sentence


GOLD_PATH = Path("output/gold_karaka_labels.csv")
GOLD_UD_PIPELINE_PATH = Path("results/dev_baseline_all.csv")
STANZA_PIPELINE_PATH = Path("results/stanza_dev_baseline_all.csv")

GOLD_UD_EVAL_PATH = Path("output/gold_ud_vs_gold_karaka_eval.csv")
STANZA_EVAL_PATH = Path("output/stanza_vs_gold_karaka_eval.csv")
GOLD_UD_CONFUSION_PATH = Path("output/karaka_confusion_matrix_gold_ud.csv")
STANZA_CONFUSION_PATH = Path("output/karaka_confusion_matrix_stanza.csv")

DEV_SPLIT = "dev"
NO_PREDICTION = "NO_PREDICTION"

KARAKAS = [
    "Karta",
    "Karma",
    "Karana",
    "Sampradana",
    "Apadana",
    "Adhikarana",
]

LABEL_NORMALIZATION = {
    "Kartā": "Karta",
    "Karta": "Karta",
    "Karma": "Karma",
    "Karaṇa": "Karana",
    "Karana": "Karana",
    "Sampradāna": "Sampradana",
    "Sampradana": "Sampradana",
    "Apādāna": "Apadana",
    "Apadana": "Apadana",
    "Adhikaraṇa": "Adhikarana",
    "Adhikarana": "Adhikarana",
}

EVAL_FIELDS = [
    "system",
    "metric_scope",
    "karaka",
    "support",
    "tp",
    "fp",
    "fn",
    "precision",
    "recall",
    "f1",
    "accuracy",
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


def normalize_token(token):
    """Normalize token text with the alignment normalization."""
    return normalize_sentence(token)


def normalize_karaka(label):
    """Normalize pipeline karaka spellings to the gold label space."""
    return LABEL_NORMALIZATION.get(label.strip(), label.strip())


def parse_candidates(candidate_text):
    """Parse and normalize a pipe-separated final_candidates cell."""
    if not candidate_text:
        return set()

    candidates = set()
    for label in candidate_text.split("|"):
        normalized = normalize_karaka(label)
        if normalized in KARAKAS:
            candidates.add(normalized)
    return candidates


def prediction_label(candidates):
    """Return one confusion-matrix column label for a candidate set."""
    if not candidates:
        return NO_PREDICTION
    return "|".join(sorted(candidates))


def build_pipeline_index(rows):
    """Index pipeline rows by split, sentence id, and normalized token."""
    index = defaultdict(deque)
    for row in rows:
        key = (
            DEV_SPLIT,
            row["sent_id"],
            normalize_token(row["token_form"]),
        )
        index[key].append(row)
    return index


def dev_gold_rows(rows):
    """Keep dev rows where a gold karaka label exists."""
    return [
        row for row in rows
        if row["split"] == DEV_SPLIT and row["gold_karaka"]
    ]


def evaluate_rows(gold_rows, pipeline_rows):
    """Join gold and pipeline rows, then compute row-level predictions."""
    pipeline_index = build_pipeline_index(pipeline_rows)
    evaluated = []

    for gold_row in gold_rows:
        key = (
            gold_row["split"],
            gold_row["ud_sent_id"],
            normalize_token(gold_row["token"]),
        )
        pipeline_row = pipeline_index[key].popleft() if pipeline_index[key] else None
        candidates = parse_candidates(pipeline_row["final_candidates"]) if pipeline_row else set()

        evaluated.append({
            "gold": gold_row["gold_karaka"],
            "predicted": candidates,
            "prediction_label": prediction_label(candidates),
            "matched_pipeline_row": pipeline_row is not None,
        })

    return evaluated


def safe_divide(numerator, denominator):
    """Return a rounded metric value with zero for empty denominators."""
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


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


def compute_confusion_rows(evaluated_rows):
    """Build a gold-by-prediction confusion matrix."""
    prediction_labels = sorted({
        row["prediction_label"] for row in evaluated_rows
    })
    if NO_PREDICTION in prediction_labels:
        prediction_labels.remove(NO_PREDICTION)
        prediction_labels.append(NO_PREDICTION)

    counts = Counter(
        (row["gold"], row["prediction_label"])
        for row in evaluated_rows
    )
    fieldnames = ["gold_karaka"] + prediction_labels
    rows = []

    for gold in KARAKAS:
        matrix_row = {"gold_karaka": gold}
        for predicted in prediction_labels:
            matrix_row[predicted] = counts[(gold, predicted)]
        rows.append(matrix_row)

    return rows, fieldnames


def run_system(system_name, pipeline_path, eval_path, confusion_path, gold_rows):
    """Evaluate one pipeline output file and write both output CSVs."""
    pipeline_rows = load_csv(pipeline_path)
    evaluated_rows = evaluate_rows(gold_rows, pipeline_rows)

    eval_rows = compute_eval_summary(system_name, evaluated_rows)
    confusion_rows, confusion_fields = compute_confusion_rows(evaluated_rows)

    write_csv(eval_path, eval_rows, EVAL_FIELDS)
    write_csv(confusion_path, confusion_rows, confusion_fields)

    return eval_rows, evaluated_rows


def print_compact_summary(system_name, eval_rows, evaluated_rows):
    """Print compact overall and per-label metrics."""
    overall = eval_rows[0]
    unmatched = sum(1 for row in evaluated_rows if not row["matched_pipeline_row"])

    print(system_name)
    print("=" * len(system_name))
    print(f"evaluated_rows: {overall['support']}")
    print(f"accuracy: {overall['accuracy']}")
    print(f"unmatched_gold_rows: {unmatched}")
    print(f"{'karaka':<15} {'support':>8} {'precision':>10} {'recall':>8} {'f1':>8}")
    for row in eval_rows[1:]:
        print(
            f"{row['karaka']:<15} {row['support']:>8} "
            f"{row['precision']:>10} {row['recall']:>8} {row['f1']:>8}"
        )
    print()


def main():
    gold_rows = dev_gold_rows(load_csv(GOLD_PATH))

    gold_ud_eval_rows, gold_ud_evaluated = run_system(
        "gold_ud_pipeline",
        GOLD_UD_PIPELINE_PATH,
        GOLD_UD_EVAL_PATH,
        GOLD_UD_CONFUSION_PATH,
        gold_rows,
    )
    stanza_eval_rows, stanza_evaluated = run_system(
        "stanza_pipeline",
        STANZA_PIPELINE_PATH,
        STANZA_EVAL_PATH,
        STANZA_CONFUSION_PATH,
        gold_rows,
    )

    print_compact_summary("Gold UD pipeline vs gold Karaka", gold_ud_eval_rows, gold_ud_evaluated)
    print_compact_summary("Stanza pipeline vs gold Karaka", stanza_eval_rows, stanza_evaluated)
    print(f"Saved eval CSVs to: {GOLD_UD_EVAL_PATH}, {STANZA_EVAL_PATH}")
    print(f"Saved confusion matrices to: {GOLD_UD_CONFUSION_PATH}, {STANZA_CONFUSION_PATH}")


if __name__ == "__main__":
    main()
