"""
Evaluate correction layer v2 against dev gold Karaka labels.

Compares:
- neural_only: mapper_candidates
- verifier_v1: final_candidates
- correction_v2: corrected_candidates
"""

from pathlib import Path

from evaluate_dev_metrics_strict_vs_candidate import (
    MODES,
    OUTPUT_FIELDS,
    compute_mode_metrics,
    evaluate_rows,
    print_compact_table,
)
from evaluate_pipeline_against_gold import (
    GOLD_PATH,
    dev_gold_rows,
    load_csv,
    write_csv,
)


BASELINE_PATH = Path("results/stanza_dev_baseline_all.csv")
CORRECTED_PATH = Path("results/stanza_dev_corrected_v2_all.csv")
OUTPUT_PATH = Path("output/dev_correction_v2_metrics.csv")

SYSTEMS = [
    ("neural_only", "mapper_candidates", BASELINE_PATH),
    ("verifier_v1", "final_candidates", BASELINE_PATH),
    ("correction_v2", "corrected_candidates", CORRECTED_PATH),
]


def main():
    gold_rows = dev_gold_rows(load_csv(GOLD_PATH))
    output_rows = []

    for system_name, candidate_column, input_path in SYSTEMS:
        pipeline_rows = load_csv(input_path)
        evaluated_rows = evaluate_rows(gold_rows, pipeline_rows, candidate_column)
        for mode in MODES:
            output_rows.extend(compute_mode_metrics(system_name, mode, evaluated_rows))

    write_csv(OUTPUT_PATH, output_rows, OUTPUT_FIELDS)
    print_compact_table(output_rows)
    print()
    print(f"Saved correction v2 metrics to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
