# Final Project Reference

**Project title (final):** Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses

**Document purpose:** Definitive implementation handbook for the completed research project. This document is written for a future return to the repository after several months. It explains what was built, how the work evolved, where important files live, which experiments were run, and how all components connect.

**This is not:** a paper outline, a README, or a handover note for a new collaborator starting mid-project.

**Primary companion documents:**

| Document | Role |
|----------|------|
| `docs/final_train_dev_results.md` | Final train/dev metrics |
| `docs/final_test_results.md` | Final held-out test metrics |
| `docs/correction_layer_log.md` | Correction and DR1 decisions |
| `docs/project_status_checkpoint_3.md` | Comprehensive status snapshot before test |
| `docs/paper_assets/` | Paper planning tables and figure specs |

---

## How to Read This Document

The project evolved in phases. Each phase below includes:

- **Objective**
- **Implementation**
- **Important files**
- **Outputs**
- **Lessons learned**
- **Link to next phase**

Two architecture flows appear repeatedly:

**Karaka prediction pipeline:**

```text
Sentence
  -> Stanza parser
  -> UD token rows + case markers
  -> Mapper v1 (mapper_candidates)
  -> Verifier v1 (final_candidates)
  -> Correction Layer v2.1 (corrected_candidates)
  -> Karaka prediction / evaluation
```

**Evaluation dataset construction:**

```text
UD Hindi-HDTB + Original HDTB .dat files
  -> normalization
  -> sentence alignment
  -> gold Karaka extraction
  -> token matching to pipeline output
  -> evaluation against gold Karaka labels
```

---

## Chronological Narrative: Project Evolution

### Starting Framing (Week 1)

The internship began with a neuro-symbolic NLP goal: combine neural dependency parsing with Paninian grammar for Hindi. Early documents (`docs/project_context.md`, `docs/project_scope.md`) framed the work as building a **verifier and corrector over UD parses**, not merely a lookup table from UD labels to Karakas.

**Original emphasis:**

- UD-to-Karaka mapping is a **starting hypothesis**, not the research output.
- The verifier is the main symbolic contribution.
- Decision types (`confirmed`, `corrected`, `ambiguous`, `no_decision`) must be explicit.
- Gold UD trees from Hindi-HDTB would be used first to isolate symbolic behavior from parser noise.

**Early limitation discovered:** Hindi-HDTB in UD format does not contain Paninian Karaka gold labels. The project could design and inspect rules, but could not yet **evaluate Karaka accuracy** against a gold standard. This limitation later drove the HDTB alignment pivot.

---

## Phase 1: Dataset Exploration and Rule Design

**Objective:** Understand Hindi-HDTB structure, dependency label distribution, and postposition patterns that could support Paninian verifier rules.

**Implementation:**

- Loaded train split CoNLL-U files.
- Counted sentences, tokens, and dependency relations.
- Identified `case` nodes as postposition evidence attached to parents.
- Analyzed co-occurrence of postposition forms (`ने`, `को`, `से`, `में`, `पर`) with parent `deprel` labels.

**Important files:**

| Type | Path |
|------|------|
| Notebook | `notebooks/01_dataset_exploration.ipynb` |
| Notebook | `notebooks/02_postposition_analysis.ipynb` |
| Notebook | `notebooks/03_dev_postposition_comparison.ipynb` |
| Doc | `docs/project_context.md` |
| Doc | `docs/ud_to_karaka_mapping_v1.md` |
| Doc | `docs/rule_specification_v1.md` |
| Doc | `docs/rule_specification_audit.md` |
| Data | `data/raw/hi_hdtb-ud-train.conllu` |
| Data | `data/raw/hi_hdtb-ud-dev.conllu` |

**Outputs:**

- Statistical evidence for rules R1 to R5 (e.g. `ने` on `nsubj`, `में`/`पर` on `obl`, ambiguous `से` and `को` patterns).
- Confirmation that train and dev postposition patterns are stable enough for rule design.

**Lessons learned:**

- Postpositions are the strongest symbolic evidence available in UD trees.
- `obl` is inherently context-dependent; deprel alone is insufficient for Karaka assignment.
- `से` and `को` require ambiguity-preserving rules, not forced single-label outputs.

**Led to:** Phase 2 (Mapper v1) and Phase 3 (Verifier v1), because mapping hypotheses and postposition rules needed separate implementations.

---

## Phase 2: Mapper v1

**Objective:** Implement a conservative, deprel-only UD-to-Karaka mapping layer as the neural-only baseline input to the verifier.

**Implementation:**

- `map_ud_to_karaka(deprel)` returns candidate Karakas, confidence, mapping status, and reason.
- Supports `nsubj`, `obj`, `iobj`, `obl`, `root`, `case`; all other deprels are `unsupported`.
- Does not use postpositions. Does not call the verifier.

**Important files:**

| Type | Path |
|------|------|
| Code | `src/mapper/simple_mapper.py` |
| Doc | `docs/ud_to_karaka_mapping_v1.md` |

**Outputs:**

- Mapper behavior documented in mapping spec.
- `mapper_candidates` column in all later pipeline CSVs.

**Lessons learned:**

- Mapper alone produces useful but shallow hypotheses (`nsubj -> Kartā`, `obj -> Karma`).
- `obl` mapping must remain multi-candidate and low confidence.
- Mapper output alone is the **neural-only** baseline in final evaluation (`mapper_candidates`).

**Led to:** Phase 3, because mapper hypotheses required symbolic verification.

---

## Phase 3: Verifier v1

**Objective:** Implement postposition-based Paninian verifier rules R1 to R5 with explicit decision types.

**Implementation:**

- `verify_token(deprel, case_marker)` applies rules only when a case marker is present.
- **R1:** `nsubj + ने` -> confirmed Kartā
- **R2:** `obl + में` -> confirmed Adhikaraṇa
- **R3:** `obl + पर` -> confirmed Adhikaraṇa
- **R4:** `obl + से` -> ambiguous Karaṇa|Apādāna
- **R5:** `obj/iobj + को` -> ambiguous Karma|Sampradāna
- Deliberately excludes `nmod + में/पर` (important later for H1).
- Pipeline merge logic in `run_gold_ud_pipeline.py`: verifier `confirmed`/`ambiguous` overrides mapper; otherwise mapper hypothesis is kept.

**Important files:**

| Type | Path |
|------|------|
| Code | `src/verifier/simple_verifier.py` |
| Code | `src/verifier/run_on_sentence.py` |
| Code | `src/verifier/run_verifier_batch.py` |
| Code | `src/pipeline/run_gold_ud_pipeline.py` |
| Doc | `docs/rule_specification_v1.md` |
| Doc | `docs/verifier_output_observations_v1.md` |
| Doc | `docs/verifier_failure_analysis_v1.md` |
| Notebook | `notebooks/05_verifier_output_analysis.ipynb` |
| Notebook | `notebooks/06_verifier_failure_analysis.ipynb` |
| Notebook | `notebooks/07_pipeline_analysis.ipynb` |
| Output | `results/verifier_batch_all.csv` |
| Output | `results/verifier_batch_meaningful.csv` |
| Output | `results/gold_ud_pipeline_all.csv` |

**Outputs:**

- 50-sentence train pilot with verifier-only and full pipeline CSVs.
- Qualitative failure analysis: strong confirmations, unresolved ambiguities, mapping-only hypotheses.

**Lessons learned:**

- Verifier v1 works best when postposition evidence aligns with expected parent deprel (`obl + में/पर`).
- Many tokens remain `no_decision` or `mapping_hypothesis` because v1 requires case markers.
- Strict disambiguation gain would later come mainly from turning mapper guesses into verifier-confirmed single labels.

**Led to:** Phase 4 (Stanza integration) to test the pipeline on realistic parser output.

---

## Phase 4: Stanza Integration

**Objective:** Replace gold UD input with neural parser output while keeping Mapper v1 and Verifier v1 frozen.

**Implementation:**

- `src/parser/stanza_parser.py` wraps Stanza Hindi pipeline (`tokenize,pos,lemma,depparse`).
- `run_stanza_pipeline_sample.py` parses fixed sample sentences end-to-end.
- `run_stanza_dev_baseline.py` and `run_stanza_train_baseline.py` run full splits.
- `run_stanza_baseline.py` generalizes to `--split train|dev|test`.
- Case marker extraction reuses gold pipeline logic: find child `case` token attached to parent.

**Important files:**

| Type | Path |
|------|------|
| Code | `src/parser/stanza_parser.py` |
| Code | `src/pipeline/run_stanza_pipeline_sample.py` |
| Code | `src/pipeline/run_stanza_dev_baseline.py` |
| Code | `src/pipeline/run_stanza_train_baseline.py` |
| Code | `src/pipeline/run_stanza_baseline.py` |
| Output | `results/stanza_pipeline_sample_all.csv` |
| Output | `results/stanza_dev_baseline_all.csv` |
| Output | `results/stanza_train_baseline_all.csv` |
| Output | `results/stanza_test_baseline_all.csv` |

**Outputs:**

- Full Stanza baselines for dev, train, and test with same CSV schema as gold UD baseline.
- Evidence that Stanza introduces label and attachment differences vs gold UD.

**Lessons learned:**

- Parser noise changes which verifier rules fire.
- Stanza often uses `nmod` where gold UD uses `obl` for locative dependents. This pattern became central to H1.
- Neural parser integration is necessary for realistic Karaka extraction evaluation.

**Led to:** Phase 5 (Gold vs Stanza comparison).

---

## Phase 5: Gold vs Stanza Comparison

**Objective:** Quantify how Stanza parser output differs from gold UD and how those differences affect pipeline decisions.

**Implementation:**

- Ran full gold UD dev baseline (`run_dev_baseline.py`) and Stanza dev baseline.
- Notebook 10 matched token rows between gold and Stanza pipeline outputs.
- Compared `deprel`, `case_marker`, verifier rule IDs, and final decisions.

**Important files:**

| Type | Path |
|------|------|
| Code | `src/pipeline/run_dev_baseline.py` |
| Notebook | `notebooks/09_dev_baseline_analysis.ipynb` |
| Notebook | `notebooks/10_stanza_vs_gold_analysis.ipynb` |
| Doc | `docs/verifier_v1_dev_baseline.md` |
| Output | `results/dev_baseline_all.csv` |
| Output | `results/stanza_dev_baseline_all.csv` |
| Output | `results/stanza_vs_gold_matched.csv` |
| Output | `results/stanza_vs_gold_deprel_disagreements.csv` |
| Output | `results/stanza_vs_gold_case_marker_disagreements.csv` |
| Output | `results/stanza_vs_gold_final_decision_disagreements.csv` |

**Outputs:**

- Large deprel disagreement count (~1,705 on dev matched tokens).
- Case marker attachment disagreements (~216).
- Stanza deprel accuracy ~95.16% on dev (used later in DR1 evaluation).

**Lessons learned:**

- Gold UD experiments isolate symbolic logic; Stanza experiments reflect deployable conditions.
- Parser label choice (`nmod` vs `obl`) directly gates verifier rules R2/R3.
- Final evaluation must use Stanza output, not gold UD, for realistic claims.

**Led to:** Phase 6 (rule disagreement analysis).

---

## Phase 6: Rule Disagreement Analysis

**Objective:** Determine which verifier rules are gained or lost when moving from gold UD to Stanza parses.

**Implementation:**

- Notebook 11 analyzed `stanza_vs_gold_rule_disagreements.csv`.
- Counted per-rule gains and losses (R1 to R5).
- Inspected examples where Stanza triggered R4 (`obl + से`) but gold did not.

**Important files:**

| Type | Path |
|------|------|
| Notebook | `notebooks/11_rule_disagreement_analysis.ipynb` |
| Output | `results/stanza_vs_gold_rule_disagreements.csv` |
| Output | `results/rule_disagreement_summary.csv` |

**Outputs:**

- R4 (`obl + से`) had the largest disagreement footprint.
- Many disagreements stem from deprel or case attachment changes, not verifier logic bugs.

**Lessons learned:**

- Symbolic rules are sensitive to parser structure, not just token text.
- Error analysis must separate **rule design limits** from **parser errors**.
- `nmod + locative` cases missed by R2/R3 would become a major correction opportunity.

**Led to:** Phase 7 (original HDTB discovery), because quantitative Karaka evaluation still required gold semantic labels not present in UD alone.

---

## Phase 7: Original HDTB Discovery

**Objective:** Find original HDTB annotation files that contain Paninian relation labels (`k1`, `k2`, `k7`, etc.).

**Implementation:**

- Discovered raw HDTB `.dat` files under `data/raw/news_articles_and_heritage/`.
- Inspected file structure with `scripts/inspect_hdtb_structure.py`.
- Confirmed columns include token, head, and Paninian relation label.
- Counted relation frequencies with `scripts/count_hdtb_relations.py`.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/inspect_hdtb_structure.py` |
| Script | `scripts/count_hdtb_relations.py` |
| Data | `data/raw/news_articles_and_heritage/` |
| Output | `output/hdtb_relation_counts.csv` |

**Outputs:**

- Verified that original HDTB contains rich Paninian labels beyond the small evaluation subset.
- Confirmed label inventory includes `k1`, `k2`, `k3`, `k4`, `k5`, `k7`, `k7p` and many variants not used in evaluation.

**Lessons learned:**

- UD Hindi-HDTB and original HDTB are related but not directly joinable without sentence alignment.
- Evaluation scope must explicitly restrict which Paninian labels map to Karaka classes.
- This discovery transformed the project from rule prototyping into measurable Karaka extraction research.

**Led to:** Phase 8 (sentence alignment).

---

## Phase 8: Sentence Alignment

**Objective:** Align UD sentences to HDTB sentences so gold Karaka labels can be assigned to UD token positions.

**Implementation:**

- Built alignment pipeline with Unicode NFC normalization, nukta variants, punctuation cleanup, `NULL` token removal.
- Exact normalized match first; fuzzy `SequenceMatcher` fallback for high-confidence cases.
- Iterated through alignment audits (v1 and v2) fixing quote-spacing normalization bugs.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/alignment_audit.py` |
| Script | `scripts/alignment_audit_v2.py` |
| Script | `scripts/build_aligned_hdtb_ud.py` |
| Script | `scripts/inspect_unmatched_alignment.py` |
| Output | `output/aligned_ud_hdtb_sentences.csv` |
| Output | `output/unmatched_nearest_candidates.csv` |

**Alignment results (final v2):**

| Split | UD sentences | Exact match | Notes |
|-------|-------------:|------------:|-------|
| train | 13,306 | 13,302 | 4 unmatched UD sentences |
| dev | 1,659 | 1,659 | full alignment |
| test | 1,684 | 1,684 | full alignment |

**Lessons learned:**

- Text normalization details matter; one quote-spacing bug blocked an otherwise exact match.
- Train has a small number of genuine segmentation or text mismatches, not a systemic alignment failure.
- Sentence alignment is a prerequisite artifact; token matching is a separate later step.

**Led to:** Phase 9 (gold Karaka recovery).

---

## Phase 9: Gold Karaka Recovery

**Objective:** Extract token-level gold Karaka labels from aligned HDTB `.dat` files.

**Implementation:**

- For each aligned sentence, read HDTB sentence by index from corresponding `.dat` file.
- Extract token, head, Paninian relation.
- Map restricted label set to normalized Karaka names.

**Label mapping (evaluation subset):**

| HDTB label | Gold Karaka |
|------------|-------------|
| k1 | Karta |
| k2 | Karma |
| k3 | Karana |
| k4 | Sampradana |
| k5 | Apadana |
| k7, k7p | Adhikarana |

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/extract_gold_karaka_labels.py` |
| Output | `output/gold_karaka_labels.csv` |

**Gold row counts:**

| Split | Gold Karaka rows |
|-------|-----------------:|
| train | 47,378 |
| dev | 5,902 |
| test | 5,946 |

**Lessons learned:**

- Gold evaluation covers a **subset** of HDTB semantics; many Paninian labels remain unmapped.
- Gold labels attach to HDTB token strings; UD/Stanza tokenization requires normalized token matching.
- Evaluation rows are sparse: only tokens with mapped gold Karaka labels are scored.

**Led to:** Phase 10 (token matching audit).

---

## Phase 10: Token Matching Audit

**Objective:** Verify that gold Karaka rows align reliably to Stanza pipeline token rows.

**Implementation:**

- Matching key: `split + sent_id + normalized_token + occurrence_order`.
- Normalization follows `alignment_audit_v2.py` token normalization.
- Audited dev split unmatched and extra pipeline rows.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/audit_dev_token_matching.py` |
| Script | `scripts/evaluate_pipeline_against_gold.py` (shared matching utilities) |
| Output | `output/dev_token_matching_audit.csv` |

**Dev audit results:**

| Metric | Count |
|--------|------:|
| Total gold rows | 5,902 |
| Matched | 5,880 |
| Unmatched | 22 |
| Match rate | 99.63% |
| Extra pipeline rows with meaningful candidates | 2,393 |

**Test audit results (final evaluation):**

| Metric | Count |
|--------|------:|
| Total gold rows | 5,946 |
| Matched | 5,924 |
| Unmatched | 22 |
| Match rate | 99.63% |

**Lessons learned:**

- Token matching is stable enough for evaluation but not perfect.
- Many Stanza predictions exist on tokens outside the restricted gold Karaka set; precision interpretation requires care.
- Unmatched gold rows count as incorrect under strict scoring because predictions are empty.

**Led to:** Phase 11 (first gold Karaka evaluation).

---

## Phase 11: First Gold Karaka Evaluation

**Objective:** Compare pipeline Karaka predictions against extracted gold labels for the first time.

**Implementation:**

- `evaluate_pipeline_against_gold.py` joins gold rows to pipeline rows.
- Initial evaluation compared gold UD pipeline vs Stanza pipeline on dev.
- Produced accuracy, per-Karaka P/R/F1, confusion matrices.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/evaluate_pipeline_against_gold.py` |
| Script | `scripts/evaluate_neural_vs_neurosymbolic.py` |
| Output | `output/gold_ud_vs_gold_karaka_eval.csv` |
| Output | `output/stanza_vs_gold_karaka_eval.csv` |
| Output | `output/karaka_confusion_matrix_stanza.csv` |
| Output | `output/neural_only_eval.csv` |
| Output | `output/neurosymbolic_eval.csv` |

**Lessons learned:**

- Gold UD upper bounds symbolic behavior; Stanza is the realistic evaluation target.
- Verifier v1 helps, but not uniformly across Karakas.
- Multi-candidate outputs require careful metric definition.

**Led to:** Phase 12 (candidate vs strict metrics).

---

## Phase 12: Candidate vs Strict Metrics

**Objective:** Separate generous ambiguity-aware scoring from strict single-label scoring.

**Implementation:**

- **Candidate-set:** gold Karaka anywhere in predicted set counts as correct.
- **Strict:** exactly one predicted label must match gold; empty or multi-label predictions are incorrect.
- `evaluate_dev_metrics_strict_vs_candidate.py` formalized both modes.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/evaluate_dev_metrics_strict_vs_candidate.py` |
| Output | `output/dev_metrics_strict_vs_candidate.csv` |

**Lessons learned:**

- Candidate-set scores overstate disambiguation success when mapper returns broad hypotheses.
- Strict scoring shows Verifier v1's main value: converting hypotheses to single confirmed labels.
- Both metrics should be reported; **strict is primary** for final claims.

**Led to:** Phase 13 (error analysis).

---

## Phase 13: Error Analysis

**Objective:** Characterize neural-only (`mapper_candidates`) errors against gold Karaka on dev.

**Implementation:**

- `analyze_dev_neural_errors.py` listed all incorrect neural-only predictions.
- Summarized errors by gold Karaka, deprel, case marker, confusion pairs.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/analyze_dev_neural_errors.py` |
| Output | `output/dev_neural_only_errors.csv` |
| Output | `output/dev_neural_error_summary.csv` |

**Lessons learned:**

- Errors cluster by syntactic pattern, not randomly.
- Locative, passive-like, and `से`-marked patterns dominate actionable errors.
- Error summaries must feed rule design, not just reporting.

**Led to:** Phase 14 (actionable error mining).

---

## Phase 14: Actionable Error Mining

**Objective:** Filter errors to patterns where symbolic rules could plausibly help.

**Implementation:**

- Filtered to rows with `deprel in {nsubj, obj, iobj, obl, nmod}` or salient case markers.
- Pattern summaries and top example extraction for manual inspection.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/analyze_dev_actionable_errors.py` |
| Script | `scripts/inspect_top_actionable_error_examples.py` |
| Output | `output/dev_actionable_neural_errors.csv` |
| Output | `output/dev_actionable_error_summary.csv` |
| Output | `output/top_actionable_error_examples.csv` |

**Top actionable pattern:**

- `Adhikarana | nmod | में` = **80 errors** on dev.

**Lessons learned:**

- Verifier v1 already handles `obl + में/पर`; Stanza's `nmod + में/पर` is the gap.
- Passive-like `obj`/`nsubj` patterns are frequent but not automatically safe to correct.
- Actionable mining must precede any correction rule acceptance.

**Led to:** Phase 15 (H1 discovery).

---

## Phase 15: H1 Discovery

**Objective:** Formulate a conservative correction rule for locative `nmod` cases missed by Verifier v1.

**Implementation:**

- Hypothesis: extend locative postposition evidence from `obl` to a narrow `nmod` context.
- Proposed rule H1: `nmod + में/पर -> Adhikarana`.
- Implemented in `correction_layer_v2.py` as safe override after verifier v1.
- Diagnostic flags added in same module but kept non-correcting.

**Important files:**

| Type | Path |
|------|------|
| Code | `src/pipeline/correction_layer_v2.py` |
| Doc | `docs/correction_layer_log.md` |

**Lessons learned:**

- H1 is linguistically parallel to R2/R3 but applied at Karaka layer, not deprel layer.
- Correction must be scoped narrowly to avoid broad `nmod` remapping.
- Diagnostics (`possible_passive_karta`, etc.) should remain separate from accepted rules.

**Led to:** Phase 16 (Correction Layer v2.1).

---

## Phase 16: Correction Layer v2.1

**Objective:** Integrate H1 as the only accepted automatic correction rule and produce corrected pipeline outputs.

**Implementation:**

- `apply_correction(row)` copies row and sets `corrected_candidates`.
- Only H1 changes `corrected_candidates` relative to `final_candidates`.
- Applied via split-aware `scripts/apply_correction_v2.py` (and split-specific dev/train scripts).

**Important files:**

| Type | Path |
|------|------|
| Code | `src/pipeline/correction_layer_v2.py` |
| Script | `scripts/apply_correction_v2.py` |
| Script | `scripts/apply_correction_v2_dev.py` |
| Script | `scripts/apply_correction_v2_train.py` |
| Output | `results/stanza_dev_corrected_v2_all.csv` |
| Output | `results/stanza_train_corrected_v2_all.csv` |
| Output | `results/stanza_test_corrected_v2_all.csv` |

**H1 firing counts:**

| Split | H1 fires |
|-------|--------:|
| train | 830 |
| dev | 121 |
| test | 130 |

**Lessons learned:**

- Correction layer belongs **after** verifier v1, not inside mapper or verifier.
- A single conservative rule can improve metrics without touching unrelated Karakas.
- `correction_v2.1` column (`corrected_candidates`) is the third evaluation stage.

**Led to:** Phase 17 (train/dev validation).

---

## Phase 17: Train/Dev Validation

**Objective:** Validate Correction v2.1 on train and dev before any test evaluation.

**Implementation:**

- `evaluate_correction_v2.py` compares neural_only, verifier_v1, correction_v2.1.
- `compare_correction_v2_per_karaka.py` reports per-Karaka F1 deltas.
- Test split explicitly excluded until freeze.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/evaluate_correction_v2.py` |
| Script | `scripts/evaluate_correction_v2_dev.py` |
| Script | `scripts/evaluate_correction_v2_train.py` |
| Script | `scripts/compare_correction_v2_per_karaka.py` |
| Doc | `docs/final_train_dev_results.md` |
| Output | `output/dev_correction_v2_metrics.csv` |
| Output | `output/train_correction_v2_metrics.csv` |
| Output | `output/dev_correction_v2_per_karaka_comparison.csv` |

**Lessons learned:**

- H1 improves both candidate-set and strict metrics on train and dev.
- Effect is localized to Adhikarana; other Karakas unchanged.
- Train/dev gains justify a single held-out test run, not further rule tuning.

**Led to:** Phase 18 (passive investigation).

---

## Phase 18: Passive Investigation

**Objective:** Evaluate whether passive-voice diagnostics could become safe correction rules.

**Implementation:**

- Diagnostic flags in correction layer:
  - `possible_passive_karta`: `obj` without Karta in final candidates
  - `possible_passive_karma`: `nsubj` without Karma in final candidates
- `analyze_passive_diagnostics.py` computed distributions and estimated conversion impact.
- Manual review of 50 examples per flag in `docs/passive_example_manual_summary.md`.

**Important files:**

| Type | Path |
|------|------|
| Script | `scripts/analyze_passive_diagnostics.py` |
| Doc | `docs/passive_example_manual_summary.md` |
| Output | `output/passive_diagnostic_summary.csv` |
| Output | `output/passive_diagnostic_examples.csv` |

**Findings:**

- `possible_passive_karta`: **NEEDS REFINEMENT** (some true passives, many ordinary `obj -> Karma` cases).
- `possible_passive_karma`: **FALSE LEAD** (mostly correct `nsubj -> Karta` cases).

**Lessons learned:**

- Syntactic configuration alone is insufficient for passive correction.
- Future passive rules would need explicit passive morphology and predicate context.
- Diagnostics remain in code but **no passive correction rule was accepted**.

**Led to:** Phase 19 (dependency repair experiment).

---

## Phase 19: Dependency Repair Experiment (DR1)

**Objective:** Test whether changing Stanza deprel labels (`nmod -> obl`) improves alignment with gold UD and helps Karaka extraction.

**Implementation:**

- `dependency_repair_v1.py` implements DR1: `nmod + में/पर -> obl` on a copy column `corrected_deprel`.
- Original `deprel` preserved; heads unchanged.
- Evaluated deprel accuracy against gold UD dev (`evaluate_dependency_repair_v1_dev.py`).

**Important files:**

| Type | Path |
|------|------|
| Code | `src/pipeline/dependency_repair_v1.py` |
| Script | `scripts/apply_dependency_repair_v1_dev.py` |
| Script | `scripts/evaluate_dependency_repair_v1_dev.py` |
| Output | `output/dependency_repair_v1_dev_eval.csv` |
| Output | `output/dependency_repair_v1_dev_dr1_cases.csv` |
| Output | `results/stanza_dev_dependency_repaired_v1_all.csv` |

**DR1 results (dev):**

| Metric | Value |
|--------|------:|
| Original deprel accuracy | 95.16% |
| After DR1 | 94.85% |
| Repairs | 121 |
| Improved | 5 |
| Worsened | 113 |

**Lessons learned:**

- Karaka-oriented label repair can conflict with UD gold structure.
- DR1 is a **negative result** and was rejected.
- H1 at Karaka layer achieves locative gains without claiming UD parsing improvement.

**Led to:** Phase 20 (project reframing).

---

## Phase 20: Project Reframing

**Objective:** Align all documentation with what the evidence actually supports.

**Pivot:**

| Earlier implicit framing | Final framing |
|--------------------------|---------------|
| Neuro-symbolic dependency parsing improvement | Neuro-symbolic **Karaka extraction** over neural parses |
| UD label repair as possible path | UD label repair rejected (DR1) |
| Broad correction layer | Single accepted rule H1 in Correction v2.1 |

**Evidence causing pivot:**

- DR1 harmed UD deprel accuracy while H1 helped Karaka F1.
- Evaluation target is HDTB-derived Karaka labels, not UAS/LAS.
- Verifier and correction layers improve semantic interpretation, not treebank dependency repair.

**Important files updated:**

| Path |
|------|
| `README.md` |
| `docs/project_context.md` |
| `docs/project_handover_v1.md` |
| `docs/project_handover_v2.md` |
| `docs/project_status_checkpoint_3.md` |
| `docs/correction_layer_log.md` |
| `docs/final_train_dev_results.md` |
| `docs/paper_assets/` |

**Lessons learned:**

- Negative results must be documented with equal clarity to positive results.
- Test split must remain frozen until reframing and rule freeze are complete.
- README and handover docs are historical layers; `final_project_reference.md` and `final_*_results.md` are the completion record.

**Led to:** Phase 21 (final test evaluation).

---

## Phase 21: Final Test Evaluation

**Objective:** Run exactly one held-out test evaluation of the frozen system after all rule decisions were finalized.

**Frozen system:**

- Stanza parser
- Mapper v1 (frozen)
- Verifier v1 (frozen)
- Correction Layer v2.1 with H1 only

**Commands run (once):**

```bash
python src/pipeline/run_stanza_baseline.py --split test
python scripts/apply_correction_v2.py --split test
python scripts/evaluate_correction_v2.py --split test
python scripts/compare_correction_v2_per_karaka.py --split test
```

**Important files:**

| Type | Path |
|------|------|
| Script | `src/pipeline/run_stanza_baseline.py` |
| Script | `scripts/apply_correction_v2.py` |
| Script | `scripts/evaluate_correction_v2.py` |
| Script | `scripts/compare_correction_v2_per_karaka.py` |
| Doc | `docs/final_test_results.md` |
| Output | `output/test_correction_v2_metrics.csv` |
| Output | `output/test_correction_v2_per_karaka_comparison.csv` |
| Output | `results/stanza_test_baseline_all.csv` |
| Output | `results/stanza_test_corrected_v2_all.csv` |

**Lessons learned:**

- Test trends match train/dev: Verifier v1 provides largest strict gain; H1 adds localized Adhikarana improvement.
- Strict test accuracy: 0.4850 (neural) to 0.5980 (correction v2.1).
- No further test reruns are methodologically valid without a new research phase.

---

## Final Frozen System Specification

### End-to-End Pipeline

```text
Input: Hindi sentence text (from UD CoNLL-U # text field at runtime)

1. Stanza parse
   Module: src/parser/stanza_parser.py
   Output per token: token_id, text, head, deprel, POS fields

2. Case marker extraction
   Module: src/pipeline/run_gold_ud_pipeline.py (find_case_marker)
   Output: case_marker string from child case node, or blank

3. Mapper v1
   Module: src/mapper/simple_mapper.py
   Function: map_ud_to_karaka(deprel)
   Output column: mapper_candidates

4. Verifier v1
   Module: src/verifier/simple_verifier.py
   Function: verify_token(deprel, case_marker)
   Output columns: verifier_candidates, verifier_rule_id, verifier_decision

5. Merge mapper + verifier
   Module: src/pipeline/run_gold_ud_pipeline.py (combine_results)
   Output column: final_candidates, final_decision

6. Correction Layer v2.1
   Module: src/pipeline/correction_layer_v2.py
   Function: apply_correction(row)
   Output column: corrected_candidates
```

### Mapper v1 (Frozen)

| deprel | karaka_candidates | confidence | status |
|--------|-------------------|------------|--------|
| nsubj | Kartā | low-medium | mapped |
| obj | Karma | medium | mapped |
| iobj | Sampradāna | medium | mapped |
| obl | Adhikaraṇa, Apādāna, Karaṇa | low | context_dependent |
| root | (none) | high | no_karaka |
| case | (none) | high | evidence_only |
| other | (none) | none | unsupported |

### Verifier v1 Rules (Frozen)

| Rule | Condition | Output | decision_type |
|------|-----------|--------|---------------|
| R1 | nsubj + ने | Kartā | confirmed |
| R2 | obl + में | Adhikaraṇa | confirmed |
| R3 | obl + पर | Adhikaraṇa | confirmed |
| R4 | obl + से | Karaṇa, Apādāna | ambiguous |
| R5 | obj/iobj + को | Karma, Sampradāna | ambiguous |

No rule fires without a case marker. No rule handles `nmod + में/पर`.

### Correction Layer v2.1 (Frozen)

**Accepted correction rule:**

| Rule ID | Condition | Action | Type |
|---------|-----------|--------|------|
| H1_NMOD_LOCATIVE_ADHIKARANA | deprel == nmod AND case_marker in {में, पर} | corrected_candidates = Adhikarana | safe_override |

**Diagnostic flags only (do not change corrected_candidates):**

| Flag | Condition |
|------|-----------|
| possible_passive_karta | deprel == obj AND final_candidates lacks Karta |
| possible_passive_karma | deprel == nsubj AND final_candidates lacks Karma |
| se_ambiguous_requires_verb_context | deprel == obl AND case_marker == से |

### Evaluation Systems

| System name | CSV column | Description |
|-------------|------------|-------------|
| neural_only | mapper_candidates | Mapper output only |
| verifier_v1 | final_candidates | After verifier merge |
| correction_v2.1 | corrected_candidates | After H1 correction |

### Evaluation Protocol (Frozen)

- Gold labels: `output/gold_karaka_labels.csv`
- Token match key: split + sent_id + normalized token + occurrence order
- Primary metric: **strict accuracy** (exactly one correct label)
- Secondary metric: candidate-set accuracy
- Splits: train and dev used for development; test used once after freeze

---

## Rejected Ideas

### Passive Correction Rules

**Why investigated:**

- Dev errors included `Karta | obj` and `Karma | nsubj` patterns suggestive of passive voice.
- Diagnostic flags surfaced many rows where deprel and expected Karaka appeared mismatched.
- Automated estimates suggested large potential gains if flags were converted to corrections.

**Why rejected:**

- Manual review showed flags are too broad.
- `possible_passive_karma` mostly flags correct Karta subjects (FALSE LEAD).
- `possible_passive_karta` mixes genuine passives with ordinary objects (NEEDS REFINEMENT).
- Safe passive correction requires verb voice context and passive morphology, not deprel alone.

**Status:** Diagnostics remain in `correction_layer_v2.py`; no passive rule in frozen system.

### Dependency Repair DR1

**Why investigated:**

- Same locative pattern as H1: Stanza marks many locative dependents as `nmod` instead of `obl`.
- Hypothesis: relabeling `nmod + में/पर` to `obl` would unlock Verifier R2/R3 instead of needing Karaka-layer H1.

**Why rejected:**

- Dev gold UD deprel accuracy dropped from **95.16%** to **94.85%**.
- 121 repairs: 5 improved, 113 worsened vs gold UD.
- Gold UD annotators often retain `nmod` where Karaka is still Adhikarana.
- Karaka correction and UD deprel accuracy are different objectives.

**Status:** Code exists in `src/pipeline/dependency_repair_v1.py` as experimental artifact; **not used** in final system or test evaluation.

---

## Final Train / Dev / Test Metrics

### Overall Results

**Train** (47,378 gold rows):

| System | Cand. Acc | Cand. Macro F1 | Strict Acc | Strict Macro F1 |
|--------|----------:|---------------:|-----------:|----------------:|
| Neural Only | 0.7865 | 0.6023 | 0.5310 | 0.4234 |
| Verifier v1 | 0.7864 | 0.6023 | 0.6259 | 0.4451 |
| Correction v2.1 | 0.8004 | 0.6073 | 0.6400 | 0.4513 |

**Dev** (5,902 gold rows):

| System | Cand. Acc | Cand. Macro F1 | Strict Acc | Strict Macro F1 |
|--------|----------:|---------------:|-----------:|----------------:|
| Neural Only | 0.7369 | 0.5599 | 0.4909 | 0.3877 |
| Verifier v1 | 0.7403 | 0.5724 | 0.5947 | 0.4153 |
| Correction v2.1 | 0.7574 | 0.5784 | 0.6118 | 0.4226 |

**Test** (5,946 gold rows, held-out):

| System | Cand. Acc | Cand. Macro F1 | Strict Acc | Strict Macro F1 |
|--------|----------:|---------------:|-----------:|----------------:|
| Neural Only | 0.7356 | 0.5621 | 0.4850 | 0.3876 |
| Verifier v1 | 0.7373 | 0.5716 | 0.5785 | 0.4220 |
| Correction v2.1 | 0.7568 | 0.5786 | 0.5980 | 0.4308 |

### Strict Accuracy Progression (Primary Metric)

| Split | Neural Only | Verifier v1 | Correction v2.1 |
|-------|------------:|------------:|----------------:|
| Train | 0.5310 | 0.6259 | 0.6400 |
| Dev | 0.4909 | 0.5947 | 0.6118 |
| Test | 0.4850 | 0.5785 | 0.5980 |

### H1 Adhikarana Impact

| Split | H1 fires | Verifier v1 Cand. F1 | Corr. v2.1 Cand. F1 | Verifier v1 Strict F1 | Corr. v2.1 Strict F1 |
|-------|--------:|---------------------:|--------------------:|----------------------:|---------------------:|
| Train | 830 | 0.9026 | 0.9325 | 0.7890 | 0.8265 |
| Dev | 121 | 0.8881 | 0.9241 | 0.7897 | 0.8335 |
| Test | 130 | 0.8815 | 0.9239 | 0.7713 | 0.8237 |

### Test Absolute Improvements (Correction v2.1 vs Neural Only)

| Metric | Gain |
|--------|-----:|
| Candidate accuracy | +0.0212 |
| Candidate macro F1 | +0.0165 |
| Strict accuracy | +0.1130 |
| Strict macro F1 | +0.0432 |

---

## Repository Map (Evolution-Critical Files Only)

```text
data/raw/
  hi_hdtb-ud-{train,dev,test}.conllu     # UD treebank splits
  news_articles_and_heritage/            # Original HDTB .dat files

src/
  mapper/simple_mapper.py                # Mapper v1
  verifier/simple_verifier.py            # Verifier v1
  parser/stanza_parser.py                # Stanza wrapper
  pipeline/
    run_gold_ud_pipeline.py              # Core pipeline + case marker + merge
    run_stanza_baseline.py               # Split-aware Stanza baseline runner
    correction_layer_v2.py               # Correction v2.1 + diagnostics
    dependency_repair_v1.py              # DR1 experiment (rejected)

scripts/
  build_aligned_hdtb_ud.py               # Sentence alignment
  extract_gold_karaka_labels.py          # Gold label extraction
  evaluate_pipeline_against_gold.py      # Core evaluation utilities
  evaluate_correction_v2.py              # Split-aware final metrics
  apply_correction_v2.py                 # Split-aware correction application
  analyze_dev_neural_errors.py           # Error analysis chain
  analyze_passive_diagnostics.py         # Passive investigation
  evaluate_dependency_repair_v1_dev.py   # DR1 evaluation

output/
  aligned_ud_hdtb_sentences.csv          # Sentence alignment artifact
  gold_karaka_labels.csv                 # Gold evaluation labels
  {train,dev,test}_correction_v2_metrics.csv
  test_correction_v2_per_karaka_comparison.csv

results/
  stanza_{split}_baseline_all.csv        # Stanza pipeline outputs (large; gitignored)
  stanza_{split}_corrected_v2_all.csv    # Corrected outputs (large; gitignored)
  dev_baseline_all.csv                   # Gold UD dev baseline
  stanza_vs_gold_*.csv                   # Gold vs Stanza comparison artifacts

docs/
  final_project_reference.md             # This document
  final_train_dev_results.md             # Train/dev metrics
  final_test_results.md                  # Test metrics
  correction_layer_log.md                # H1 and DR1 decisions
  project_status_checkpoint_3.md           # Pre-test comprehensive status
  paper_assets/                          # Paper planning artifacts

notebooks/
  01-03                                  # Dataset and postposition analysis
  05-07                                  # Verifier and pipeline pilots
  09-11                                  # Dev baseline, Stanza comparison, rule disagreements
```

**Gitignore note:** Large generated CSVs (`results/*_all.csv`), `.venv/`, and `data/raw/news_articles_and_heritage/` are excluded from version control. Local copies remain on disk for reproduction.

---

## Final Lessons Learned

1. **Gold semantic labels require a bridge corpus.** UD Hindi-HDTB alone cannot evaluate Karaka extraction; original HDTB alignment was the enabling engineering step.

2. **Separate mapper, verifier, and correction stages.** Each stage maps to a distinct evaluation column and makes ablation interpretable.

3. **Strict metrics reveal verifier value.** Candidate-set scores hide ambiguity; strict scoring shows Verifier v1's disambiguation contribution.

4. **Parser label choice gates symbolic rules.** Stanza `nmod` vs `obl` differences explain why R2/R3 miss locative cases and why H1 was needed at the Karaka layer.

5. **Conservative rules generalize better.** H1 affects only Adhikarana and improved train, dev, and test without side effects on other Karakas.

6. **Not every plausible pattern should become a rule.** Passive diagnostics and DR1 looked promising in aggregate statistics but failed manual or gold-UD validation.

7. **Karaka correction is not deprel repair.** DR1 proved that improving Karaka interpretation can worsen UD label accuracy; the project framing must keep these tasks separate.

8. **Freeze test before claiming generalization.** Train/dev error mining motivated H1; test confirmed the trend once, without iterative tuning.

9. **Token matching is good but not perfect.** 99.63% match rate on dev and test leaves 22 unmatched gold rows per split; evaluation protocol treats unmatched rows as incorrect predictions.

10. **Document negative results explicitly.** DR1 and passive rejection are part of the scientific record, not footnotes.

---

## What Actually Became the Contribution of This Project

The completed project is **not** a Hindi dependency parser and **not** a demonstration that UD dependency accuracy improves through symbolic post-processing.

The actual contribution is a **reproducible neuro-symbolic Karaka extraction pipeline** that:

1. Takes **Stanza neural dependency parses** as input evidence.
2. Applies **frozen Paninian-inspired symbolic rules** (Mapper v1 and Verifier v1) to produce interpretable Karaka candidates with explicit decision types.
3. Adds one **validated correction rule** (H1) that fixes a recurring Stanza locative pattern (`nmod + में/पर`) at the **Karaka interpretation layer**.
4. Evaluates against **HDTB-derived gold Karaka labels** obtained through a documented UD-to-HDTB alignment and extraction pipeline.
5. Reports both generous and strict metrics, with strict accuracy showing **0.4850 to 0.5980** improvement on held-out test from neural-only mapping to the full frozen system.
6. Includes **negative results** that bound the claims: DR1 dependency repair harms UD deprel accuracy; passive diagnostics were not promoted to rules.

**Why the final framing is Karaka extraction, not dependency parsing improvement:**

- The evaluation target is Paninian Karaka labels from HDTB, not UAS/LAS or deprel accuracy on the final system claim.
- The largest reliable gains come from interpreting neural parses semantically (verifier disambiguation and H1 locative correction), not from relabeling edges to match gold UD.
- DR1 explicitly showed that forcing `nmod -> obl` hurts UD accuracy even when motivated by similar locative intuition as H1.
- The symbolic layer's value is **transparent, rule-governed semantic role extraction** over imperfect neural syntactic analyses.

In short: the project delivers a **small, frozen, auditable neuro-symbolic layer for Hindi Karaka extraction from Stanza parses**, with train/dev development, one held-out test confirmation, and clearly documented limits on scope, label coverage, and rejected extensions.
