# Recommended Figures and Tables

Planning document only. No images are generated here.

**Project framing:** Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses

---

## Figure 1: Pipeline Architecture

| Property | Detail |
|----------|--------|
| **Purpose** | Show the end-to-end neuro-symbolic pipeline and evaluation points. |
| **Data source** | `docs/archive/project_status_checkpoint_3.md`, `src/pipeline/`, pipeline CSV column definitions |
| **What to show** | Linear flow: Sentence -> Stanza -> UD dependencies (+ case markers) -> Mapper v1 -> Verifier v1 -> Correction v2.1 -> Karaka prediction. Annotate three evaluation stages: neural only, verifier v1, correction v2.1. Mark H1 as the only accepted correction rule. |
| **Priority** | **Essential** |

Suggested layout: horizontal block diagram with boxed stages and arrow labels for `mapper_candidates`, `final_candidates`, `corrected_candidates`.

---

## Figure 2: Dataset Alignment Flow

| Property | Detail |
|----------|--------|
| **Purpose** | Explain how gold Karaka labels are obtained from two corpora. |
| **Data source** | `docs/archive/project_status_checkpoint_3.md`, `outputs/alignment/aligned_ud_hdtb_sentences.csv`, `outputs/gold/gold_karaka_labels.csv` |
| **What to show** | UD Hindi-HDTB + Original HDTB -> normalization -> sentence alignment -> gold Karaka extraction -> token-level evaluation join. Include alignment statistics table inset or callout (train/dev/test exact match counts). |
| **Priority** | **Essential** |

Suggested layout: two-column input (UD CoNLL-U, HDTB `.dat`) merging into aligned sentence pairs, then token-level Karaka labels.

---

## Figure 3: Strict Accuracy Comparison Across Splits

| Property | Detail |
|----------|--------|
| **Purpose** | Present the primary result: strict Karaka accuracy improvement across pipeline stages and splits. |
| **Data source** | `docs/paper/paper_assets/final_results_tables.md` (Table 4) |
| **What to show** | Grouped bar chart: x-axis = split (train, dev, test); grouped bars = Neural Only, Verifier v1, Correction v2.1; y-axis = strict accuracy. Values: Train (0.5310, 0.6259, 0.6400); Dev (0.4909, 0.5947, 0.6118); Test (0.4850, 0.5785, 0.5980). |
| **Priority** | **Essential** |

Optional variant: line chart with three series across splits to emphasize consistent gains.

---

## Figure 4: Adhikarana F1 Improvement (Verifier v1 vs Correction v2.1)

| Property | Detail |
|----------|--------|
| **Purpose** | Show localized effect of H1 on the target Karaka class across splits. |
| **Data source** | `docs/final/final_train_dev_results.md`, `docs/final/final_test_results.md`, `docs/paper/paper_assets/final_results_tables.md` (Table 5) |
| **What to show** | Grouped bars or paired dot plot for Adhikarana F1: Verifier v1 vs Correction v2.1 on train, dev, test. Report both candidate F1 and strict F1 in separate panels or dual y-axis subplots. Candidate F1: 0.9026/0.9325 (train), 0.8881/0.9241 (dev), 0.8815/0.9239 (test). Strict F1: 0.7890/0.8265 (train), 0.7897/0.8335 (dev), 0.7713/0.8237 (test). Annotate H1 fire counts: 830, 121, 130. |
| **Priority** | **Essential** |

---

## Figure 5: Negative Result (DR1 Dependency Repair)

| Property | Detail |
|----------|--------|
| **Purpose** | Demonstrate that Karaka-oriented correction does not imply UD deprel improvement. |
| **Data source** | `docs/final/correction_layer_log.md`, `docs/archive/project_status_checkpoint_3.md`, `outputs/rejected_experiments/dependency_repair_v1/dependency_repair_v1_dev_eval.csv` |
| **What to show** | Before/after deprel accuracy on dev: 95.16% (original Stanza) vs 94.85% (after DR1). Bar or table inset with repair outcome counts: 121 repairs, 5 improved, 113 worsened, 3 unchanged wrong. Contrast with H1 Karaka gain on Adhikarana. |
| **Priority** | **Essential** for honest framing; prevents misclassification as dependency parsing work |

Caption note: DR1 rule was `nmod + में/पर -> obl`. Accepted system uses Karaka correction only, not deprel repair.

---

## Optional Figures

### Figure 6: Strict Macro F1 Across Splits

| Property | Detail |
|----------|--------|
| **Purpose** | Supplement strict accuracy with class-balanced summary metric. |
| **Data source** | Table 4 in `final_results_tables.md` |
| **What to show** | Same layout as Figure 3 but for strict macro F1. |
| **Priority** | Optional |

### Figure 7: Per-Karaka Strict F1 Heatmap (Test)

| Property | Detail |
|----------|--------|
| **Purpose** | Visualize class-wise strengths and persistent failures on held-out test. |
| **Data source** | `docs/final/final_test_results.md`, Table 7 in `final_results_tables.md` |
| **What to show** | Heatmap: rows = Karakas, columns = Neural Only / Verifier v1 / Correction v2.1, values = strict F1. Highlights zero strict F1 for Karana and Apadana. |
| **Priority** | Optional |

### Figure 8: Error Pattern Motivating H1

| Property | Detail |
|----------|--------|
| **Purpose** | Connect rule design to error analysis. |
| **Data source** | `docs/final/correction_layer_log.md`, dev actionable error summaries |
| **What to show** | Count or bar for pattern `Adhikarana | nmod | में` (80 dev errors) vs post-H1 reduction. |
| **Priority** | Optional (methods/error analysis support) |

### Figure 9: Passive Diagnostic Investigation (Not Accepted)

| Property | Detail |
|----------|--------|
| **Purpose** | Document investigated but rejected correction directions. |
| **Data source** | `docs/experiments/passive_example_manual_summary.md`, `outputs/error_analysis/passive_diagnostic_summary.csv` |
| **What to show** | Flag counts for `possible_passive_karta` and `possible_passive_karma` with conclusion labels (NEEDS REFINEMENT / FALSE LEAD). No correction applied. |
| **Priority** | Optional (limitations / negative results section) |

---

## Suggested Table List for the Paper

| Table | Content | Source | Priority |
|-------|---------|--------|----------|
| **T1: Dataset statistics** | UD sentences per split, HDTB sentences, gold Karaka row counts | `docs/archive/project_status_checkpoint_3.md` | Essential |
| **T2: Alignment statistics** | Exact match and high-confidence match rates by split | `docs/archive/project_status_checkpoint_3.md`, `outputs/alignment/aligned_ud_hdtb_sentences.csv` | Essential |
| **T3: Overall results** | Train/dev/test accuracy and macro F1 for all three systems | `docs/paper/paper_assets/final_results_tables.md` Tables 1-3 | Essential |
| **T4: Strict accuracy progression** | Neural Only -> Verifier v1 -> Correction v2.1 by split | `final_results_tables.md` Table 4 | Essential |
| **T5: Per-Karaka F1** | Candidate and strict F1 by Karaka (test primary; dev/train supplementary) | `docs/final/final_test_results.md`, train/dev docs | Essential |
| **T6: H1 Adhikarana impact** | F1 gains and fire counts across splits | `final_results_tables.md` Table 5 | Essential |
| **T7: Token matching audit** | Matched/unmatched gold rows, match percentage | `docs/final/final_test_results.md` | Essential |
| **T8: Negative result (DR1)** | Deprel accuracy before/after DR1, repair outcome breakdown | `docs/final/correction_layer_log.md`, `outputs/rejected_experiments/dependency_repair_v1/dependency_repair_v1_dev_eval.csv` | Essential |
| **T9: Absolute improvements (test)** | Verifier and correction gains on held-out test | `docs/final/final_test_results.md` | Recommended |
| **T10: Gold label mapping** | HDTB Paninian label to Karaka mapping | `docs/archive/project_status_checkpoint_3.md` | Optional |
| **T11: Verifier rule summary** | Postposition rules in Verifier v1 | `src/verifier/simple_verifier.py`, handover docs | Optional |

---

## Figure and Table Placement Guide

| Paper section | Recommended visuals |
|---------------|-------------------|
| Introduction | Figure 1 (pipeline overview) |
| Dataset and Alignment | Figure 2, T1, T2, T10 |
| Methodology | Figure 1 (detailed), T11 |
| Experimental Setup | T7 (matching), scoring mode box |
| Results | Figure 3, Figure 4, T3, T4, T5, T6, T9 |
| Error Analysis and Negative Results | Figure 5, Figure 8, Figure 9, T8 |
| Limitations | Figure 7 (optional) |
| Conclusion | Figure 3 inset or T4 summary row for test |

---

## Design Notes

- Use consistent colors for the three systems across all figures.
- Label the project as **Karaka extraction over neural parses**, not UD parsing improvement.
- Mark test results as **held-out, single-run, frozen system**.
- Keep candidate-set figures/tables in appendix or supplementary material if space is limited.
- For Figure 5, place near Results or Negative Results to avoid misinterpretation of project scope.
