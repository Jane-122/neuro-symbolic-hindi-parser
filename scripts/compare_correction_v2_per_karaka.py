"""
Compare per-karaka F1 across neural-only, verifier v1, and correction v2.
"""

import csv
from pathlib import Path


INPUT_PATH = Path("output/dev_correction_v2_metrics.csv")
OUTPUT_PATH = Path("output/dev_correction_v2_per_karaka_comparison.csv")

SYSTEMS = [
    "neural_only",
    "verifier_v1",
    "correction_v2",
]

MODES = [
    "candidate_set",
    "strict",
]

OUTPUT_FIELDS = [
    "mode",
    "karaka",
    "support",
    "neural_only_f1",
    "verifier_v1_f1",
    "correction_v2_f1",
    "delta_correction_v2_minus_verifier_v1",
    "delta_correction_v2_minus_neural_only",
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


def to_float(value):
    """Convert metric strings to floats."""
    return float(value) if value else 0.0


def build_metric_index(rows):
    """Index per-karaka metric rows by mode, karaka, and system."""
    index = {}
    for row in rows:
        if row["metric_scope"] != "per_karaka":
            continue
        key = (row["mode"], row["karaka"], row["system"])
        index[key] = row
    return index


def build_comparison_rows(rows):
    """Build one comparison row per mode and karaka."""
    index = build_metric_index(rows)
    karakas = sorted({
        row["karaka"]
        for row in rows
        if row["metric_scope"] == "per_karaka"
    })
    comparison_rows = []

    for mode in MODES:
        for karaka in karakas:
            neural = index[(mode, karaka, "neural_only")]
            verifier = index[(mode, karaka, "verifier_v1")]
            correction = index[(mode, karaka, "correction_v2")]

            neural_f1 = to_float(neural["f1"])
            verifier_f1 = to_float(verifier["f1"])
            correction_f1 = to_float(correction["f1"])

            comparison_rows.append({
                "mode": mode,
                "karaka": karaka,
                "support": correction["support"],
                "neural_only_f1": neural_f1,
                "verifier_v1_f1": verifier_f1,
                "correction_v2_f1": correction_f1,
                "delta_correction_v2_minus_verifier_v1": round(
                    correction_f1 - verifier_f1,
                    4,
                ),
                "delta_correction_v2_minus_neural_only": round(
                    correction_f1 - neural_f1,
                    4,
                ),
            })

    return comparison_rows


def print_table(rows):
    """Print per-karaka F1 comparison tables by mode."""
    for mode in MODES:
        print()
        print(mode)
        print("=" * len(mode))
        print(
            f"{'karaka':<15} {'support':>8} {'neural':>10} "
            f"{'verifier':>10} {'corr_v2':>10} "
            f"{'delta_v1':>10} {'delta_neural':>13}"
        )
        for row in rows:
            if row["mode"] != mode:
                continue
            print(
                f"{row['karaka']:<15} {row['support']:>8} "
                f"{row['neural_only_f1']:>10.4f} "
                f"{row['verifier_v1_f1']:>10.4f} "
                f"{row['correction_v2_f1']:>10.4f} "
                f"{row['delta_correction_v2_minus_verifier_v1']:>10.4f} "
                f"{row['delta_correction_v2_minus_neural_only']:>13.4f}"
            )


def main():
    rows = load_csv(INPUT_PATH)
    comparison_rows = build_comparison_rows(rows)
    write_csv(OUTPUT_PATH, comparison_rows, OUTPUT_FIELDS)
    print_table(comparison_rows)
    print()
    print(f"Saved per-karaka comparison to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
