# Repository Reorganization Migration Log

**Date:** 2026-06-18  
**Purpose:** Prepare repo for UDPipe parser experiment without changing frozen Stanza scientific logic or overwriting existing results.

## Summary

- No files were deleted (empty `output/` and `results/` directories removed after all contents moved).
- Frozen logic unchanged: `src/mapper/simple_mapper.py`, `src/verifier/simple_verifier.py`, `src/pipeline/correction_layer_v2.py`, evaluation formulas in scripts.
- All existing Stanza CSV artifacts were **moved**, not regenerated.
- Central path constants added in `src/paths.py`.
- Script import bootstrap added in `scripts/_bootstrap.py`.

---

## Path replacement map (old → new)

### Top-level directories

| Old | New |
|-----|-----|
| `output/` | `outputs/` (with subfolders) |
| `results/` | `experiments/stanza/` (+ `experiments/rejected/`) |
| `scripts/*.py` (flat) | `scripts/{data_prep,evaluation,analysis,experiments,legacy}/` |
| `docs/*.md` (flat) | `docs/{final,paper,methodology,experiments,archive}/` |
| `notebooks/*.ipynb` (flat) | `notebooks/{exploration,analysis}/` |

### Scripts

| Old | New |
|-----|-----|
| `scripts/alignment_audit.py` | `scripts/data_prep/alignment_audit.py` |
| `scripts/alignment_audit_v2.py` | `scripts/data_prep/alignment_audit_v2.py` |
| `scripts/build_aligned_hdtb_ud.py` | `scripts/data_prep/build_aligned_hdtb_ud.py` |
| `scripts/extract_gold_karaka_labels.py` | `scripts/data_prep/extract_gold_karaka_labels.py` |
| `scripts/inspect_hdtb_structure.py` | `scripts/data_prep/inspect_hdtb_structure.py` |
| `scripts/inspect_sentences.py` | `scripts/data_prep/inspect_sentences.py` |
| `scripts/inspect_unmatched_alignment.py` | `scripts/data_prep/inspect_unmatched_alignment.py` |
| `scripts/count_hdtb_relations.py` | `scripts/data_prep/count_hdtb_relations.py` |
| `scripts/evaluate_pipeline_against_gold.py` | `scripts/evaluation/evaluate_pipeline_against_gold.py` |
| `scripts/evaluate_correction_v2.py` | `scripts/evaluation/evaluate_correction_v2.py` |
| `scripts/evaluate_dev_metrics_strict_vs_candidate.py` | `scripts/evaluation/evaluate_dev_metrics_strict_vs_candidate.py` |
| `scripts/evaluate_neural_vs_neurosymbolic.py` | `scripts/evaluation/evaluate_neural_vs_neurosymbolic.py` |
| `scripts/compare_correction_v2_per_karaka.py` | `scripts/evaluation/compare_correction_v2_per_karaka.py` |
| `scripts/apply_correction_v2.py` | `scripts/evaluation/apply_correction_v2.py` |
| `scripts/analyze_dev_neural_errors.py` | `scripts/analysis/analyze_dev_neural_errors.py` |
| `scripts/analyze_dev_actionable_errors.py` | `scripts/analysis/analyze_dev_actionable_errors.py` |
| `scripts/analyze_passive_diagnostics.py` | `scripts/analysis/analyze_passive_diagnostics.py` |
| `scripts/analyze_remaining_errors_v2.py` | `scripts/analysis/analyze_remaining_errors_v2.py` |
| `scripts/audit_dev_token_matching.py` | `scripts/analysis/audit_dev_token_matching.py` |
| `scripts/inspect_top_actionable_error_examples.py` | `scripts/analysis/inspect_top_actionable_error_examples.py` |
| `scripts/apply_dependency_repair_v1_dev.py` | `scripts/experiments/apply_dependency_repair_v1_dev.py` |
| `scripts/evaluate_dependency_repair_v1_dev.py` | `scripts/experiments/evaluate_dependency_repair_v1_dev.py` |
| `scripts/apply_correction_v2_dev.py` | `scripts/legacy/apply_correction_v2_dev.py` |
| `scripts/apply_correction_v2_train.py` | `scripts/legacy/apply_correction_v2_train.py` |
| `scripts/evaluate_correction_v2_dev.py` | `scripts/legacy/evaluate_correction_v2_dev.py` |
| `scripts/evaluate_correction_v2_train.py` | `scripts/legacy/evaluate_correction_v2_train.py` |

### Documentation

| Old | New |
|-----|-----|
| `docs/final_project_reference.md` | `docs/final/final_project_reference.md` |
| `docs/final_train_dev_results.md` | `docs/final/final_train_dev_results.md` |
| `docs/final_test_results.md` | `docs/final/final_test_results.md` |
| `docs/correction_layer_log.md` | `docs/final/correction_layer_log.md` |
| `docs/paper_assets/` | `docs/paper/paper_assets/` |
| `docs/paper_implementation_audit.md` | `docs/paper/paper_implementation_audit.md` |
| `docs/project_context.md` | `docs/methodology/project_context.md` |
| `docs/project_scope.md` | `docs/methodology/project_scope.md` |
| `docs/ud_to_karaka_mapping_v1.md` | `docs/methodology/ud_to_karaka_mapping_v1.md` |
| `docs/rule_specification_v1.md` | `docs/methodology/rule_specification_v1.md` |
| `docs/rule_specification_audit.md` | `docs/methodology/rule_specification_audit.md` |
| `docs/verifier_output_observations_v1.md` | `docs/experiments/verifier_output_observations_v1.md` |
| `docs/verifier_failure_analysis_v1.md` | `docs/experiments/verifier_failure_analysis_v1.md` |
| `docs/verifier_v1_dev_baseline.md` | `docs/experiments/verifier_v1_dev_baseline.md` |
| `docs/passive_example_manual_summary.md` | `docs/experiments/passive_example_manual_summary.md` |
| `docs/project_handover_v1.md` | `docs/archive/project_handover_v1.md` |
| `docs/project_handover_v2.md` | `docs/archive/project_handover_v2.md` |
| `docs/research_notes.md` | `docs/archive/research_notes.md` |
| `docs/ud_to_karaka_mapping.md` | `docs/archive/ud_to_karaka_mapping.md` |
| `docs/project_status_checkpoint_3.md` | `docs/archive/project_status_checkpoint_3.md` |

### Notebooks

| Old | New |
|-----|-----|
| `notebooks/01_dataset_exploration.ipynb` | `notebooks/exploration/01_dataset_exploration.ipynb` |
| `notebooks/02_postposition_analysis.ipynb` | `notebooks/exploration/02_postposition_analysis.ipynb` |
| `notebooks/03_dev_postposition_comparison.ipynb` | `notebooks/exploration/03_dev_postposition_comparison.ipynb` |
| `notebooks/05_verifier_output_analysis.ipynb` | `notebooks/analysis/05_verifier_output_analysis.ipynb` |
| `notebooks/06_verifier_failure_analysis.ipynb` | `notebooks/analysis/06_verifier_failure_analysis.ipynb` |
| `notebooks/07_pipeline_analysis.ipynb` | `notebooks/analysis/07_pipeline_analysis.ipynb` |
| `notebooks/09_dev_baseline_analysis.ipynb` | `notebooks/analysis/09_dev_baseline_analysis.ipynb` |
| `notebooks/10_stanza_vs_gold_analysis.ipynb` | `notebooks/analysis/10_stanza_vs_gold_analysis.ipynb` |
| `notebooks/11_rule_disagreement_analysis.ipynb` | `notebooks/analysis/11_rule_disagreement_analysis.ipynb` |

### Outputs (`output/` → `outputs/`)

| Old | New |
|-----|-----|
| `output/aligned_ud_hdtb_sentences.csv` | `outputs/alignment/aligned_ud_hdtb_sentences.csv` |
| `output/aligned_ud_hdtb_unmatched.csv` | `outputs/alignment/aligned_ud_hdtb_unmatched.csv` |
| `output/alignment_matches.csv` | `outputs/alignment/alignment_matches.csv` |
| `output/alignment_summary.csv` | `outputs/alignment/alignment_summary.csv` |
| `output/alignment_summary_v2.csv` | `outputs/alignment/alignment_summary_v2.csv` |
| `output/alignment_unmatched_ud.csv` | `outputs/alignment/alignment_unmatched_ud.csv` |
| `output/unmatched_nearest_candidates.csv` | `outputs/alignment/unmatched_nearest_candidates.csv` |
| `output/gold_karaka_labels.csv` | `outputs/gold/gold_karaka_labels.csv` |
| `output/hdtb_relation_counts.csv` | `outputs/gold/hdtb_relation_counts.csv` |
| `output/hdtb_sentences.csv` | `outputs/gold/hdtb_sentences.csv` |
| `output/ud_sentences.csv` | `outputs/gold/ud_sentences.csv` |
| `output/inspect_*.txt` | `outputs/gold/inspect_*.txt` |
| `output/*_correction_v2_metrics.csv` | `outputs/metrics/*_correction_v2_metrics.csv` |
| `output/*_correction_v2_per_karaka_comparison.csv` | `outputs/metrics/*_correction_v2_per_karaka_comparison.csv` |
| `output/dev_metrics_strict_vs_candidate.csv` | `outputs/metrics/dev_metrics_strict_vs_candidate.csv` |
| `output/gold_ud_vs_gold_karaka_eval.csv` | `outputs/metrics/gold_ud_vs_gold_karaka_eval.csv` |
| `output/stanza_vs_gold_karaka_eval.csv` | `outputs/metrics/stanza_vs_gold_karaka_eval.csv` |
| `output/karaka_confusion_matrix_*.csv` | `outputs/metrics/karaka_confusion_matrix_*.csv` |
| `output/neural_only_eval.csv` | `outputs/metrics/neural_only_eval.csv` |
| `output/neurosymbolic_eval.csv` | `outputs/metrics/neurosymbolic_eval.csv` |
| `output/dev_*errors*.csv`, `output/passive_*`, `output/remaining_*`, etc. | `outputs/error_analysis/` |
| `output/dependency_repair_v1_dev_*.csv` | `outputs/rejected_experiments/dependency_repair_v1/` |

### Experiments (`results/` → `experiments/`)

| Old | New |
|-----|-----|
| `results/stanza_*_baseline_all.csv` | `experiments/stanza/baseline/` |
| `results/stanza_*_baseline_meaningful.csv` | `experiments/stanza/baseline/` |
| `results/stanza_pipeline_sample_*.csv` | `experiments/stanza/baseline/` |
| `results/stanza_*_corrected_v2_all.csv` | `experiments/stanza/corrected/` |
| `results/stanza_vs_gold_*.csv` | `experiments/stanza/comparisons/` |
| `results/R*_gained_examples.csv`, `R*_lost_examples.csv` | `experiments/stanza/comparisons/` |
| `results/rule_disagreement_summary.csv` | `experiments/stanza/comparisons/` |
| `results/dev_baseline_*.csv`, `test_baseline_*.csv` | `experiments/stanza/gold_ud/` |
| `results/gold_ud_pipeline_*.csv` | `experiments/stanza/gold_ud/` |
| `results/verifier_batch_*.csv` | `experiments/stanza/gold_ud/` |
| `results/run_on_sentence_output.txt` | `experiments/stanza/gold_ud/` |
| `results/stanza_dev_dependency_repaired_v1_all.csv` | `experiments/rejected/dependency_repair_v1/` |

---

## New infrastructure files

| File | Purpose |
|------|---------|
| `src/paths.py` | Central path constants and helpers (`stanza_baseline_all`, `correction_metrics`, etc.) |
| `scripts/_bootstrap.py` | Adds script subdirs and `src/` to `sys.path` for cross-script imports |
| `experiments/udpipe/{baseline,corrected,comparisons}/.gitkeep` | Placeholders for UDPipe experiment |
| `logs/.gitkeep` | Placeholder for runtime logs |

---

## Code updated (path references only)

### `src/` pipeline and verifier runners

- `src/pipeline/run_stanza_baseline.py`
- `src/pipeline/run_stanza_dev_baseline.py`
- `src/pipeline/run_stanza_train_baseline.py`
- `src/pipeline/run_stanza_pipeline_sample.py`
- `src/pipeline/run_gold_ud_pipeline.py`
- `src/pipeline/run_dev_baseline.py`
- `src/pipeline/run_test_baseline.py`
- `src/verifier/run_verifier_batch.py`
- `src/verifier/run_on_sentence.py`

### All 26 moved scripts under `scripts/`

Each now imports `scripts/_bootstrap` and uses `src/paths.py` constants where applicable.

### Documentation

- `README.md` (rewritten structure + reproduction commands)
- 17 markdown files under `docs/` (path references bulk-updated)
- `.gitignore` (large CSV patterns moved to `experiments/stanza/`)

---

## Validation checks run

| Check | Result |
|-------|--------|
| `python -m compileall src scripts` | Pass |
| Import `mapper`, `verifier`, `correction_layer_v2` | Pass |
| Import `paths` helpers | Pass |
| Key files exist at new locations | Pass (test baseline, corrected, metrics, gold, docs) |
| `python scripts/evaluation/compare_correction_v2_per_karaka.py --split test` | Pass (reads existing metrics, writes comparison CSV) |

**Not run:** Stanza train parsing, full pipeline re-evaluation (per instructions).

---

## Updated reproduction commands

```bash
python src/pipeline/run_stanza_baseline.py --split test
python scripts/evaluation/apply_correction_v2.py --split test
python scripts/evaluation/evaluate_correction_v2.py --split test
python scripts/evaluation/compare_correction_v2_per_karaka.py --split test
```

---

## Known remaining issues

1. **Notebooks** may still contain hardcoded `results/` or `output/` paths in cell outputs or inline code — re-run or edit paths if you reopen them.
2. **Archive docs** (`docs/archive/project_handover_v*.md`) describe the old flat layout historically; they were path-updated but remain archival.
3. **Legacy split scripts** in `scripts/legacy/` still work via `_bootstrap` but are superseded by `--split` variants in `scripts/evaluation/`.
4. **No backward-compat symlinks** for `output/` or `results/` — use `src/paths.py` or this log.
5. **Script import style** uses flat cross-imports (`from evaluate_pipeline_against_gold import ...`) enabled by `_bootstrap`, not package-relative imports.

---

## Backward-compatible aliases in `src/paths.py`

```python
RESULTS = EXPERIMENTS  # deprecated name
OUTPUT = OUTPUTS       # deprecated name
```

Use the explicit constants (`STANZA_BASELINE`, `OUTPUTS_METRICS`, etc.) in new code.
