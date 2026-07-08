# Project Handover Document (Version 2)

This document is a historical implementation handover for the neuro-symbolic Hindi project. It is still useful for understanding mapper v1, verifier v1, and the Stanza baseline, but it has been superseded by later HDTB alignment, gold Karaka extraction, and correction-layer work.

For the current finalized framing, see `docs/archive/project_status_checkpoint_3.md` and `docs/final/correction_layer_log.md`.

Style note: This document avoids em dashes and double-hyphen stylistic breaks.

## 1. Current Project Objective

Project title:

Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses

Current objective:

The project builds a small, reproducible neuro-symbolic pipeline for Hindi. The pipeline takes neural UD-style dependency parses, maps selected dependency labels to conservative Paninian Karaka hypotheses, applies symbolic verifier rules using postposition evidence, and records explicit Karaka decisions.

The current project is not framed as direct improvement of UD dependency parsing. The symbolic layer improves Karaka extraction and interpretation over neural dependency parses.

The research question is:

Can Paninian Karaka-based symbolic rules improve Karaka extraction from neural Hindi dependency parses?

The current work includes mapper v1, verifier v1, Stanza baselines, HDTB-derived gold Karaka labels, train/dev evaluation, and Correction Layer v2.1.

The main contribution so far is not a broad UD-to-Karaka mapping and not direct UD dependency repair. The main contribution is a symbolic verifier and Karaka correction layer that examines neural dependency parses and postposition evidence, then returns transparent Karaka decisions.

Important scope decisions:

- Hindi-HDTB in UD format is the current data source.
- Gold UD trees are used first to establish an upper baseline for parser-independent symbolic behavior.
- Stanza parser output is now integrated as the neural parser baseline.
- Verifier v1 and mapper v1 are frozen.
- Correction Layer v2.1 is implemented and frozen with only `H1_NMOD_LOCATIVE_ADHIKARANA`.
- Verifier v2 has not been implemented.
- Gold Paninian Karaka labels are available through HDTB alignment and extraction in `outputs/gold/gold_karaka_labels.csv`.
- A dependency-label repair experiment, DR1 (`nmod + में/पर -> obl`), was tested and rejected because it reduced dev deprel accuracy from `95.16%` to `94.85%`.

## 2. Dataset Being Used

Primary dataset:

- `data/raw/hi_hdtb-ud-train.conllu`
- `data/raw/hi_hdtb-ud-dev.conllu`
- `data/raw/hi_hdtb-ud-test.conllu`

Dataset type:

Hindi-HDTB in Universal Dependencies CoNLL-U format.

Why this dataset is used:

- It provides gold UD dependency trees for Hindi.
- It includes `case` dependencies that represent postpositions.
- It supports reproducible train, dev, and test split analysis.
- It allows symbolic rule design before adding parser noise.

How each split has been used:

- Train split: dataset exploration, postposition analysis, rule design, 50-sentence pilot runs.
- Dev split: full gold UD baseline, full Stanza baseline, Gold vs Stanza comparison, rule disagreement analysis, Karaka evaluation, and correction-layer analysis.
- Test split: aligned and gold labels extracted, but intentionally frozen for final held-out evaluation.

Important limitation:

The project now derives core gold Karaka labels from aligned raw HDTB `.dat` files, but the mapped label set is partial. Current gold labels cover `k1`, `k2`, `k3`, `k4`, `k5`, `k7`, and `k7p`; other HDTB relation variants remain outside the main evaluation.

## 3. Current Repository Structure

Important folders:

`data/`

- Purpose: stores raw and processed datasets.
- Current status: raw Hindi-HDTB files are present. `data/processed/` exists but is not used.

`data/raw/`

- `data/raw/hi_hdtb-ud-train.conllu`: train split, used for exploration, rule design, and pilot runs.
- `data/raw/hi_hdtb-ud-dev.conllu`: dev split, used for gold baseline, Stanza baseline, and comparison analysis.
- `data/raw/hi_hdtb-ud-test.conllu`: test split, present but not yet evaluated.

`docs/`

- Purpose: project documentation, specifications, audits, baselines, and handover files.
- Current status: active project documentation lives here. Some older placeholder files remain.

`notebooks/`

- Purpose: analysis notebooks for dataset exploration, rule evidence, baseline analysis, and parser comparison.
- Current status: notebooks 01, 02, 03, 05, 06, 07, 09, 10, and 11 exist. Notebook 04 and notebook 08 do not exist.

`src/`

- Purpose: implementation code.
- Current status: mapper, verifier, parser, and pipeline modules are active.

`src/mapper/`

- Purpose: UD-to-Karaka mapping layer.
- Active file: `src/mapper/simple_mapper.py`

`src/verifier/`

- Purpose: Paninian symbolic verifier v1 and verifier-only runners.
- Active files: `src/verifier/simple_verifier.py`, `src/verifier/run_on_sentence.py`, `src/verifier/run_verifier_batch.py`

`src/parser/`

- Purpose: parser integration.
- Active file: `src/parser/stanza_parser.py`

`src/pipeline/`

- Purpose: combined mapper plus verifier pipeline runners.
- Active files: `src/pipeline/run_gold_ud_pipeline.py`, `src/pipeline/run_dev_baseline.py`, `src/pipeline/run_stanza_pipeline_sample.py`, `src/pipeline/run_stanza_dev_baseline.py`

`experiments/stanza/` (and subfolders)

- Purpose: generated outputs, baseline CSVs, comparison CSVs, and disagreement examples.
- Current status: contains gold baseline, Stanza baseline, comparison, and rule disagreement outputs.

`logs/`

- Purpose: reserved for logs.
- Current status: no meaningful project outputs here.

## 4. Documentation Files and Their Purpose

`docs/methodology/project_context.md`

- Purpose: primary project authority.
- Contains: project title, objective, scope, decision types, implementation principles, documentation style rules.
- Status: active.

`docs/archive/project_handover_v1.md`

- Purpose: earlier handover before the most recent Stanza comparison and rule disagreement work.
- Status: useful historical handover, but superseded by this v2 handover.

`docs/archive/project_handover_v2.md`

- Purpose: current complete handover document.
- Status: active.

`docs/methodology/ud_to_karaka_mapping_v1.md`

- Purpose: documents mapper v1 hypotheses.
- Covers: `root`, `nsubj`, `obj`, `iobj`, `obl`, `case`.
- Status: active.

`docs/archive/ud_to_karaka_mapping.md`

- Purpose: older non-versioned placeholder.
- Status: placeholder, superseded by `docs/methodology/ud_to_karaka_mapping_v1.md`.

`docs/methodology/rule_specification_v1.md`

- Purpose: formal verifier v1 rule specification.
- Covers: R1 to R5, decision type usage, exclusions, known limitations.
- Status: active, but its header still says initial hypothesis. The rules are now implemented in code.

`docs/methodology/rule_specification_audit.md`

- Purpose: audits the statistics cited in `docs/methodology/rule_specification_v1.md`.
- Evidence source: `notebooks/exploration/02_postposition_analysis.ipynb`.
- Status: active.

`docs/experiments/verifier_output_observations_v1.md`

- Purpose: manual inspection notes for verifier-only batch outputs.
- Input: `experiments/stanza/gold_ud/verifier_batch_meaningful.csv`.
- Status: active.

`docs/experiments/verifier_failure_analysis_v1.md`

- Purpose: failure-mode analysis for verifier-only meaningful outputs.
- Input: `notebooks/analysis/06_verifier_failure_analysis.ipynb`.
- Status: active.

`docs/experiments/verifier_v1_dev_baseline.md`

- Purpose: documents full gold UD dev baseline for Pipeline v1.
- Input outputs: `experiments/stanza/gold_ud/dev_baseline_all.csv`, `experiments/stanza/gold_ud/dev_baseline_meaningful.csv`.
- Status: active.

`docs/archive/research_notes.md`

- Purpose: general research notes.
- Current content: definitions for pipeline `final_decision` labels.
- Status: partial.

`docs/methodology/project_scope.md`

- Purpose: project scope placeholder.
- Status: placeholder, not filled.

## 5. Notebooks and Their Purpose

`notebooks/exploration/01_dataset_exploration.ipynb`

- Purpose: explores Hindi-HDTB train split.
- Key outputs: sentence count, deprel count, examples of key dependency labels.
- Status: complete.

`notebooks/exploration/02_postposition_analysis.ipynb`

- Purpose: analyzes postposition forms and parent dependency labels in train split.
- Key output: statistical evidence for rules R1 to R5.
- Status: complete.

`notebooks/exploration/03_dev_postposition_comparison.ipynb`

- Purpose: repeats postposition analysis on dev split and compares train vs dev.
- Key output: rule-critical postposition patterns are stable across train and dev.
- Status: complete.

`notebooks/analysis/05_verifier_output_analysis.ipynb`

- Purpose: analyzes verifier-only meaningful outputs from the 50-sentence train pilot.
- Input: `experiments/stanza/gold_ud/verifier_batch_meaningful.csv`.
- Status: complete.

`notebooks/analysis/06_verifier_failure_analysis.ipynb`

- Purpose: categorizes strong, weak, ambiguous, and potentially resolvable verifier outputs.
- Inputs: `experiments/stanza/gold_ud/verifier_batch_meaningful.csv`, `experiments/stanza/gold_ud/verifier_batch_all.csv`.
- Status: complete.

`notebooks/analysis/07_pipeline_analysis.ipynb`

- Purpose: analyzes combined mapper plus verifier pipeline on the 50-sentence train pilot.
- Input: `experiments/stanza/gold_ud/gold_ud_pipeline_meaningful.csv`.
- Status: complete.

`notebooks/analysis/09_dev_baseline_analysis.ipynb`

- Purpose: analyzes full gold UD dev baseline.
- Inputs: `experiments/stanza/gold_ud/dev_baseline_all.csv`, `experiments/stanza/gold_ud/dev_baseline_meaningful.csv`.
- Status: complete.

`notebooks/analysis/10_stanza_vs_gold_analysis.ipynb`

- Purpose: compares gold UD dev baseline with Stanza dev baseline.
- Inputs: `experiments/stanza/gold_ud/dev_baseline_all.csv`, `experiments/stanza/gold_ud/dev_baseline_meaningful.csv`, `experiments/stanza/baseline/stanza_dev_baseline_all.csv`, `experiments/stanza/baseline/stanza_dev_baseline_meaningful.csv`.
- Outputs: matched rows and disagreement CSV files.
- Status: complete.

`notebooks/analysis/11_rule_disagreement_analysis.ipynb`

- Purpose: detailed analysis of verifier rule trigger differences between gold UD and Stanza outputs.
- Inputs: `experiments/stanza/comparisons/stanza_vs_gold_rule_disagreements.csv`, `experiments/stanza/comparisons/stanza_vs_gold_matched.csv`.
- Outputs: rule disagreement summary and per-rule lost/gained example CSVs.
- Status: complete.

## 6. Source Scripts and Their Purpose

`src/mapper/simple_mapper.py`

- Purpose: implements mapper v1.
- Main function: `map_ud_to_karaka(deprel: str) -> dict`
- Status: active and frozen.

`src/verifier/simple_verifier.py`

- Purpose: implements verifier v1 rules R1 to R5.
- Main function: `verify_token(deprel: str, case_marker: Optional[str]) -> dict`
- Status: active and frozen.

`src/verifier/run_on_sentence.py`

- Purpose: runs verifier v1 on first 5 train sentences.
- Output: `experiments/stanza/gold_ud/run_on_sentence_output.txt`
- Status: helper and smoke test.

`src/verifier/run_verifier_batch.py`

- Purpose: runs verifier v1 on first 50 train sentences.
- Outputs: `experiments/stanza/gold_ud/verifier_batch_all.csv`, `experiments/stanza/gold_ud/verifier_batch_meaningful.csv`
- Status: active helper for verifier-only pilot.

`src/parser/stanza_parser.py`

- Purpose: Stanza Hindi parser wrapper.
- Main function: `parse_sentence_with_stanza(sentence: str, sent_id: str = "sample-s1") -> list[dict]`
- Processors: `tokenize`, `pos`, `lemma`, `depparse`
- Output token fields: `sent_id`, `token_id`, `text`, `lemma`, `upos`, `xpos`, `feats`, `head`, `deprel`
- Status: active.

`src/pipeline/run_gold_ud_pipeline.py`

- Purpose: combined mapper plus verifier pipeline on first 50 gold train sentences.
- Outputs: `experiments/stanza/gold_ud/gold_ud_pipeline_all.csv`, `experiments/stanza/gold_ud/gold_ud_pipeline_meaningful.csv`
- Status: active.

`src/pipeline/run_dev_baseline.py`

- Purpose: combined mapper plus verifier pipeline on full gold UD dev split.
- Outputs: `experiments/stanza/gold_ud/dev_baseline_all.csv`, `experiments/stanza/gold_ud/dev_baseline_meaningful.csv`
- Status: active.

`src/pipeline/run_stanza_pipeline_sample.py`

- Purpose: runs Stanza parser and Pipeline v1 on five fixed sample Hindi sentences.
- Outputs: `experiments/stanza/baseline/stanza_pipeline_sample_all.csv`, `experiments/stanza/baseline/stanza_pipeline_sample_meaningful.csv`
- Status: active.

`src/pipeline/run_stanza_dev_baseline.py`

- Purpose: runs Stanza parser and Pipeline v1 on full dev split sentence text.
- Safety option: `MAX_SENTENCES`, currently `None` for full dev processing.
- Outputs: `experiments/stanza/baseline/stanza_dev_baseline_all.csv`, `experiments/stanza/baseline/stanza_dev_baseline_meaningful.csv`
- Status: active.

## 7. Pipeline Architecture

Pipeline v1 has four conceptual stages:

1. Input token source
2. Mapper v1
3. Verifier v1
4. Final decision merge

Gold UD pipeline:

Input: CoNLL-U gold token rows from Hindi-HDTB.

Flow:

```text
CoNLL-U sentence
to token rows (id, form, head, deprel)
to case marker extraction
to map_ud_to_karaka(deprel)
to verify_token(deprel, case_marker)
to combine_results(mapper_result, verifier_result)
to CSV row
```

Stanza pipeline:

Input: raw sentence text from Hindi-HDTB dev split or fixed samples.

Flow:

```text
raw Hindi sentence
to Stanza parser
to token rows (token_id, text, head, deprel, lemma, POS fields)
to pipeline token shape (id, form, head, deprel)
to case marker extraction
to map_ud_to_karaka(deprel)
to verify_token(deprel, case_marker)
to combine_results(mapper_result, verifier_result)
to CSV row
```

Final decision merge logic:

- If verifier returns `confirmed`: final decision is `confirmed`, final candidates come from verifier.
- If verifier returns `ambiguous`: final decision is `ambiguous`, final candidates come from verifier.
- If verifier returns `no_decision` and mapper has candidates: final decision is `mapping_hypothesis`, final candidates come from mapper.
- If both verifier and mapper provide no usable candidates: final decision is `no_decision`.

Pipeline final decision labels:

- `confirmed`: verifier-backed single Karaka decision.
- `ambiguous`: verifier-backed multiple candidate decision.
- `mapping_hypothesis`: unverified mapper guess from UD label only.
- `no_decision`: neither mapper nor verifier produced a usable Karaka candidate.

## 8. Mapper v1 Logic

Mapper v1 is implemented in:

`src/mapper/simple_mapper.py`

Function:

```python
map_ud_to_karaka(deprel: str) -> dict
```

Return fields:

- `karaka_candidates`
- `confidence`
- `mapping_status`
- `reason`

Supported mappings:

- `nsubj`: candidate `Kartā`, confidence `low-medium`, status `mapped`
- `obj`: candidate `Karma`, confidence `medium`, status `mapped`
- `iobj`: candidate `Sampradāna`, confidence `medium`, status `mapped`
- `obl`: candidates `Adhikaraṇa`, `Apādāna`, `Karaṇa`, confidence `low`, status `context_dependent`
- `root`: no candidates, confidence `high`, status `no_karaka`
- `case`: no candidates, confidence `high`, status `evidence_only`
- unsupported labels: no candidates, confidence `none`, status `unsupported`

Important design decision:

Mapper v1 does not use postpositions. Postposition evidence belongs to the verifier. This keeps the mapping layer simple and prevents duplicated rule logic.

Known mapper limitations:

- Bare `nsubj` often maps to Kartā even when the token is not a semantic agent.
- `obl` receives a broad triple candidate set.
- Most UD labels are unsupported in v1.
- Mapper output is only a hypothesis unless verifier evidence supports it.

## 9. Verifier v1 Rules R1 to R5

Verifier v1 is implemented in:

`src/verifier/simple_verifier.py`

Function:

```python
verify_token(deprel: str, case_marker: Optional[str]) -> dict
```

Return fields:

- `karaka_candidates`
- `decision_type`
- `confidence`
- `rule_id`
- `reason`

Rule R1:

- Trigger: `deprel = nsubj` and child case marker `ने`
- Karaka: Kartā
- Decision: `confirmed`
- Confidence: high
- Rationale: `ने` strongly associates with `nsubj` in train and dev statistics.

Rule R2:

- Trigger: `deprel = obl` and child case marker `में`
- Karaka: Adhikaraṇa
- Decision: `confirmed`
- Confidence: medium-high
- Rationale: `में` often signals locative or locus-like readings, but can also mark time, extent, or manner.

Rule R3:

- Trigger: `deprel = obl` and child case marker `पर`
- Karaka: Adhikaraṇa
- Decision: `confirmed`
- Confidence: medium-high
- Rationale: `पर` often signals surface or location.

Rule R4:

- Trigger: `deprel = obl` and child case marker `से`
- Karaka candidates: Karaṇa, Apādāna
- Decision: `ambiguous`
- Confidence: low-medium
- Rationale: `से` can indicate instrument, source, separation, or manner.

Rule R5:

- Trigger: `deprel = obj` or `deprel = iobj`, and child case marker `को`
- Karaka candidates: Karma, Sampradāna
- Decision: `ambiguous`
- Confidence: low-medium
- Rationale: `को` can mark patient, recipient, experiencer-like, or dative-accusative roles.

Verifier v1 decision types:

- `confirmed`: symbolic evidence supports one Karaka candidate.
- `ambiguous`: symbolic evidence supports multiple possible Karakas.
- `no_decision`: v1 rule conditions are not met.

Documented but not implemented:

- `corrected`: reserved for a future correction layer. It is not emitted by verifier v1.

## 10. Gold Baseline Implementation and Outputs

Gold baseline means the pipeline uses gold UD trees from Hindi-HDTB rather than Stanza parser output.

50-sentence train pilot:

- Script: `src/pipeline/run_gold_ud_pipeline.py`
- Input: first 50 sentences from `data/raw/hi_hdtb-ud-train.conllu`
- Outputs: `experiments/stanza/gold_ud/gold_ud_pipeline_all.csv`, `experiments/stanza/gold_ud/gold_ud_pipeline_meaningful.csv`

50-sentence pilot counts:

- Total tokens: 779
- Meaningful rows: 117
- `confirmed`: 19
- `ambiguous`: 17
- `mapping_hypothesis`: 81
- `no_decision`: 662

Full gold UD dev baseline:

- Script: `src/pipeline/run_dev_baseline.py`
- Input: all sentences from `data/raw/hi_hdtb-ud-dev.conllu`
- Outputs: `experiments/stanza/gold_ud/dev_baseline_all.csv`, `experiments/stanza/gold_ud/dev_baseline_meaningful.csv`
- Report: `docs/experiments/verifier_v1_dev_baseline.md`
- Notebook: `notebooks/analysis/09_dev_baseline_analysis.ipynb`

Gold dev counts:

- Total sentences: 1,659
- Total tokens: 35,217
- Meaningful rows: 7,019
- `confirmed`: 1,715
- `ambiguous`: 840
- `mapping_hypothesis`: 4,464
- `no_decision`: 28,198

Gold dev verifier rule counts:

- R1: 556
- R2: 847
- R3: 312
- R4: 341
- R5: 499

Interpretation:

The high `no_decision` count is expected because verifier v1 is intentionally narrow. Most UD tokens are not candidate Karaka-bearing dependents, and the verifier only fires on five postposition patterns.

## 11. Stanza Integration Implementation and Outputs

Stanza parser wrapper:

`src/parser/stanza_parser.py`

Details:

- Loads Hindi Stanza pipeline.
- Uses processors `tokenize`, `pos`, `lemma`, `depparse`.
- Tries local cached model first.
- Downloads the Hindi model only if resources are missing.
- Returns token rows with parser features and dependency structure.

Sample Stanza pipeline:

- Script: `src/pipeline/run_stanza_pipeline_sample.py`
- Input: five fixed Hindi sample sentences.
- Outputs: `experiments/stanza/baseline/stanza_pipeline_sample_all.csv`, `experiments/stanza/baseline/stanza_pipeline_sample_meaningful.csv`

Sample sentence list:

- `राम ने आम खाया।`
- `सीता कमरे में बैठी।`
- `बच्चा मेज पर बैठा।`
- `मोहन चाकू से फल काटता है।`
- `राम ने सीता को किताब दी।`

Sample output counts:

- Total tokens: 29
- Meaningful rows: 11
- `confirmed`: 4
- `ambiguous`: 2
- `mapping_hypothesis`: 5
- `no_decision`: 18

Sample verifier rule counts:

- R1: 2
- R2: 1
- R3: 1
- R4: 1
- R5: 1

Full Stanza dev baseline:

- Script: `src/pipeline/run_stanza_dev_baseline.py`
- Input: raw sentence text from `data/raw/hi_hdtb-ud-dev.conllu`
- Outputs: `experiments/stanza/baseline/stanza_dev_baseline_all.csv`, `experiments/stanza/baseline/stanza_dev_baseline_meaningful.csv`

Full Stanza dev counts:

- Total sentences: 1,659
- Total tokens: 35,217
- Meaningful rows: 7,009
- `confirmed`: 1,741
- `ambiguous`: 864
- `mapping_hypothesis`: 4,404
- `no_decision`: 28,208

Full Stanza dev verifier rule counts:

- R1: 560
- R2: 864
- R3: 317
- R4: 360
- R5: 504

Important note:

Stanza and gold baselines have the same token count on dev in the current output. This made occurrence-safe token comparison possible.

## 12. Gold vs Stanza Comparison Workflow

Notebook:

`notebooks/analysis/10_stanza_vs_gold_analysis.ipynb`

Inputs:

- `experiments/stanza/gold_ud/dev_baseline_all.csv`
- `experiments/stanza/gold_ud/dev_baseline_meaningful.csv`
- `experiments/stanza/baseline/stanza_dev_baseline_all.csv`
- `experiments/stanza/baseline/stanza_dev_baseline_meaningful.csv`

Purpose:

Compare Pipeline v1 behavior when input comes from gold UD versus Stanza parser output.

Join key:

- `sent_id`
- `token_form`
- occurrence index within each `(sent_id, token_form)` group

Reason for occurrence index:

The same token form can appear multiple times in one sentence. Occurrence indexing prevents incorrect row matches.

Matched comparison fields:

- `sent_id`
- `sentence_text`
- `token_form`
- `gold_deprel`
- `stanza_deprel`
- `gold_case_marker`
- `stanza_case_marker`
- `gold_verifier_rule_id`
- `stanza_verifier_rule_id`
- `gold_final_decision`
- `stanza_final_decision`

Gold vs Stanza comparison counts:

- Gold rows: 35,217
- Stanza rows: 35,217
- Matched rows: 35,217
- Unmatched gold rows: 0
- Unmatched Stanza rows: 0

Agreement results:

- `final_decision`: 34,359 of 35,217, 97.56 percent
- `verifier_rule_id`: 35,011 of 35,217, 99.42 percent
- `deprel`: 33,512 of 35,217, 95.16 percent
- `case_marker`: 35,001 of 35,217, 99.39 percent

Disagreement counts:

- `final_decision`: 858
- `verifier_rule_id`: 206
- `deprel`: 1,705
- `case_marker`: 216

Generated comparison CSVs:

- `experiments/stanza/comparisons/stanza_vs_gold_matched.csv`
- `experiments/stanza/comparisons/stanza_vs_gold_final_decision_disagreements.csv`
- `experiments/stanza/comparisons/stanza_vs_gold_rule_disagreements.csv`
- `experiments/stanza/comparisons/stanza_vs_gold_deprel_disagreements.csv`
- `experiments/stanza/comparisons/stanza_vs_gold_case_marker_disagreements.csv`
- `experiments/stanza/comparisons/stanza_vs_gold_unmatched_gold.csv`
- `experiments/stanza/comparisons/stanza_vs_gold_unmatched_stanza.csv`

Interpretation:

Aggregate final decision and verifier rule distributions are very similar between gold UD and Stanza, but there are still token-level differences that matter for error analysis.

## 13. Rule Disagreement Analysis Workflow

Notebook:

`notebooks/analysis/11_rule_disagreement_analysis.ipynb`

Inputs:

- `experiments/stanza/comparisons/stanza_vs_gold_rule_disagreements.csv`
- `experiments/stanza/comparisons/stanza_vs_gold_matched.csv`

Purpose:

Analyze exactly why verifier rule triggers differ between gold UD output and Stanza output.

Categories:

- R1 lost: gold fired R1, Stanza did not.
- R1 gained: Stanza fired R1, gold did not.
- Same pattern for R2, R3, R4, and R5.

Total rule disagreements:

206

Category summary:

- R1_lost: 4, 1.94 percent, most common cause: case marker changed `ने` to empty.
- R1_gained: 8, 3.88 percent, most common cause: deprel changed `conj` to `nsubj`.
- R2_lost: 16, 7.77 percent, most common cause: deprel changed `obl` to `nmod`.
- R2_gained: 33, 16.02 percent, most common cause: deprel changed `nmod` to `obl`.
- R3_lost: 7, 3.40 percent, most common cause: case marker changed `पर` to empty.
- R3_gained: 12, 5.83 percent, most common cause: deprel changed `nmod` to `obl`.
- R4_lost: 29, 14.08 percent, most common cause: deprel changed `obl` to `nmod`.
- R4_gained: 48, 23.30 percent, most common cause: deprel changed `obj` to `obl`.
- R5_lost: 22, 10.68 percent, most common cause: deprel changed `iobj` to `nsubj`.
- R5_gained: 27, 13.11 percent, most common cause: deprel changed `nsubj` to `obj`.

Generated rule disagreement CSVs:

- `experiments/stanza/comparisons/rule_disagreement_summary.csv`
- `experiments/stanza/comparisons/R1_lost_examples.csv`
- `experiments/stanza/comparisons/R1_gained_examples.csv`
- `experiments/stanza/comparisons/R2_lost_examples.csv`
- `experiments/stanza/comparisons/R2_gained_examples.csv`
- `experiments/stanza/comparisons/R3_lost_examples.csv`
- `experiments/stanza/comparisons/R3_gained_examples.csv`
- `experiments/stanza/comparisons/R4_lost_examples.csv`
- `experiments/stanza/comparisons/R4_gained_examples.csv`
- `experiments/stanza/comparisons/R5_lost_examples.csv`
- `experiments/stanza/comparisons/R5_gained_examples.csv`

Interpretation:

Most verifier rule disagreements are caused by parser label changes or case-marker attachment changes. R4 has the largest disagreement footprint, especially gained R4 cases where Stanza labeled a token as `obl` and attached `से`.

## 14. All Generated CSV Outputs and Their Meanings

Verifier-only outputs:

`experiments/stanza/gold_ud/verifier_batch_all.csv`

- Meaning: verifier-only rows for all tokens in first 50 train sentences.
- Used by: notebooks 05 and 06.

`experiments/stanza/gold_ud/verifier_batch_meaningful.csv`

- Meaning: verifier-only rows where `decision_type` is not `no_decision`.
- Used by: notebooks 05 and 06.

Gold pipeline outputs:

`experiments/stanza/gold_ud/gold_ud_pipeline_all.csv`

- Meaning: mapper plus verifier pipeline output for first 50 gold train sentences, all rows.
- Used by: notebook 07.

`experiments/stanza/gold_ud/gold_ud_pipeline_meaningful.csv`

- Meaning: same as above, only rows where `final_decision` is not `no_decision`.
- Used by: notebook 07.

Gold dev baseline outputs:

`experiments/stanza/gold_ud/dev_baseline_all.csv`

- Meaning: full dev split pipeline output using gold UD trees.
- Used by: notebooks 09 and 10.

`experiments/stanza/gold_ud/dev_baseline_meaningful.csv`

- Meaning: meaningful subset of full gold dev baseline.
- Used by: notebooks 09 and 10.

Stanza sample outputs:

`experiments/stanza/baseline/stanza_pipeline_sample_all.csv`

- Meaning: Pipeline v1 output for five fixed sample sentences parsed by Stanza.

`experiments/stanza/baseline/stanza_pipeline_sample_meaningful.csv`

- Meaning: meaningful subset of Stanza sample output.

Stanza dev baseline outputs:

`experiments/stanza/baseline/stanza_dev_baseline_all.csv`

- Meaning: full dev split pipeline output using Stanza parser output.
- Used by: notebook 10.

`experiments/stanza/baseline/stanza_dev_baseline_meaningful.csv`

- Meaning: meaningful subset of Stanza dev baseline.
- Used by: notebook 10.

Gold vs Stanza comparison outputs:

`experiments/stanza/comparisons/stanza_vs_gold_matched.csv`

- Meaning: matched token-level rows comparing gold and Stanza pipeline outputs.

`experiments/stanza/comparisons/stanza_vs_gold_final_decision_disagreements.csv`

- Meaning: matched rows where `final_decision` differs.

`experiments/stanza/comparisons/stanza_vs_gold_rule_disagreements.csv`

- Meaning: matched rows where verifier rule id differs.

`experiments/stanza/comparisons/stanza_vs_gold_deprel_disagreements.csv`

- Meaning: matched rows where UD dependency label differs.

`experiments/stanza/comparisons/stanza_vs_gold_case_marker_disagreements.csv`

- Meaning: matched rows where extracted case marker differs.

`experiments/stanza/comparisons/stanza_vs_gold_unmatched_gold.csv`

- Meaning: gold rows without matching Stanza row. Current count is zero.

`experiments/stanza/comparisons/stanza_vs_gold_unmatched_stanza.csv`

- Meaning: Stanza rows without matching gold row. Current count is zero.

Rule disagreement outputs:

`experiments/stanza/comparisons/rule_disagreement_summary.csv`

- Meaning: counts and most common causes for R1 to R5 lost/gained categories.

`experiments/stanza/comparisons/R1_lost_examples.csv`

- Meaning: gold R1 fired, Stanza R1 did not.

`experiments/stanza/comparisons/R1_gained_examples.csv`

- Meaning: Stanza R1 fired, gold R1 did not.

`experiments/stanza/comparisons/R2_lost_examples.csv`

- Meaning: gold R2 fired, Stanza R2 did not.

`experiments/stanza/comparisons/R2_gained_examples.csv`

- Meaning: Stanza R2 fired, gold R2 did not.

`experiments/stanza/comparisons/R3_lost_examples.csv`

- Meaning: gold R3 fired, Stanza R3 did not.

`experiments/stanza/comparisons/R3_gained_examples.csv`

- Meaning: Stanza R3 fired, gold R3 did not.

`experiments/stanza/comparisons/R4_lost_examples.csv`

- Meaning: gold R4 fired, Stanza R4 did not.

`experiments/stanza/comparisons/R4_gained_examples.csv`

- Meaning: Stanza R4 fired, gold R4 did not.

`experiments/stanza/comparisons/R5_lost_examples.csv`

- Meaning: gold R5 fired, Stanza R5 did not.

`experiments/stanza/comparisons/R5_gained_examples.csv`

- Meaning: Stanza R5 fired, gold R5 did not.

Other result file:

`experiments/stanza/gold_ud/run_on_sentence_output.txt`

- Meaning: human-readable verifier output for first 5 train sentences.

## 15. Current Research Findings

Finding 1: Postposition evidence is stable between train and dev.

The train-dev postposition comparison showed that the focus postpositions (`ने`, `में`, `पर`, `से`, `को`) behave similarly across splits for the rule-critical patterns.

Finding 2: Verifier v1 is conservative and reproducible.

It produces many `no_decision` rows, but this is expected because it only handles five rule patterns.

Finding 3: R1 is the strongest rule.

`nsubj` plus `ने` is highly reliable in manual inspection and has strong corpus support.

Finding 4: R2 is useful but potentially broad.

`obl` plus `में` often indicates location, but examples include time, extent, manner, and abstract locus.

Finding 5: R4 and R5 correctly preserve ambiguity in v1.

`से` and `को` remain difficult to disambiguate without verb-frame information.

Finding 6: Stanza aggregate behavior is close to gold UD behavior.

Gold and Stanza dev baselines have similar total tokens, meaningful rows, final decision counts, and rule counts.

Finding 7: Token-level Stanza errors still affect symbolic rule firing.

There are 1,705 deprel disagreements, 216 case marker disagreements, and 206 verifier rule disagreements between gold and Stanza outputs.

Finding 8: R4 is the largest parser-driven disagreement area.

R4 gained has 48 examples and R4 lost has 29 examples. This suggests that `obl` plus `से` is sensitive to parser label differences.

Finding 9: Rule disagreements mostly come from deprel changes.

Common changes include `nmod` to `obl`, `obl` to `nmod`, `obj` to `obl`, `iobj` to `nsubj`, and `nsubj` to `obj`.

Finding 10: Correction should not be designed yet.

The project now has enough evidence to study parser errors, but the next step should remain diagnostic unless a formal v2 plan is requested.

## 16. Current Open Questions

Open question 1:

How does the system behave on the test split?

Open question 2:

Which final decision disagreements are linguistically important, not just technically different?

Open question 3:

How many Stanza parser differences cause harmful rule changes versus harmless changes?

Open question 4:

Should `mapping_hypothesis` rows be reported to users, hidden by default, or separated into a lower-confidence output layer?

Open question 5:

Can R2 be refined to separate spatial location from time, extent, and manner without overfitting?

Open question 6:

Can R4 and R5 be improved using verb-frame evidence?

Open question 7:

What should count as a `corrected` decision in a future pipeline?

Open question 8:

Is there an available Paninian Karaka gold resource for evaluation, or must evaluation remain qualitative?

Open question 9:

How should parser error analysis be summarized for the final research report?

## 17. Recommended Next Implementation Steps

Step 1: Create a Stanza vs Gold summary report document.

- Suggested path: `docs/stanza_vs_gold_analysis_v1.md`
- Use results from notebooks 10 and 11.
- Summarize final decision agreement, rule agreement, deprel agreement, case marker agreement, and rule disagreement categories.

Step 2: Analyze final decision disagreements in detail.

- Input: `experiments/stanza/comparisons/stanza_vs_gold_final_decision_disagreements.csv`
- Goal: classify whether disagreements are caused by deprel changes, case marker changes, or both.
- Do not implement correction yet.

Step 3: Run the gold baseline on the test split.

- Suggested script: `src/pipeline/run_test_baseline.py`
- Input: `data/raw/hi_hdtb-ud-test.conllu`
- Outputs: `experiments/stanza/gold_ud/test_baseline_all.csv`, `experiments/stanza/gold_ud/test_baseline_meaningful.csv`

Step 4: Run the Stanza baseline on the test split.

- Suggested script: `src/pipeline/run_stanza_test_baseline.py`
- Input: raw text from `data/raw/hi_hdtb-ud-test.conllu`
- Outputs: `experiments/stanza/baseline/stanza_test_baseline_all.csv`, `experiments/stanza/baseline/stanza_test_baseline_meaningful.csv`

Step 5: Create test split Gold vs Stanza comparison.

- Follow the workflow from notebook 10.
- Compare whether dev findings generalize to test.

Step 6: Only after test analysis, decide whether verifier v2 is justified.

- Candidate topics for v2 may include R2 subtypes, R4 manner filtering, R5 verb-frame handling, and corrected decisions.
- These should not be implemented until the diagnostic reports justify them.

Step 7: Update project-level documentation.

- Update `README.md`, which still does not fully reflect the current implementation.
- Update `docs/methodology/rule_specification_v1.md` header to reflect that verifier v1 is implemented.
- Expand `docs/archive/research_notes.md` with current findings.

## 18. Current Project Status

Completed:

- Dataset exploration.
- Postposition analysis.
- Train-dev validation.
- Mapping specification v1.
- Rule specification v1.
- Rule audit.
- Verifier v1 implementation.
- Verifier-only batch evaluation.
- Verifier failure analysis.
- Mapper v1 implementation.
- Gold UD combined pipeline.
- Full gold UD dev baseline.
- Stanza parser integration.
- Stanza sample pipeline.
- Full Stanza dev baseline.
- Gold vs Stanza comparison.
- Rule disagreement analysis.

Frozen:

- Mapper v1.
- Verifier v1.
- Pipeline v1 merge logic.

Not implemented:

- Verifier v2.
- Correction logic.
- Test split baseline.
- Final report.
- Gold Karaka evaluation.

Estimated implementation completion:

Approximately 80 percent for the v1 baseline and parser comparison phase.

The remaining 20 percent is mostly test split evaluation, final diagnostic reporting, and project write-up. It does not require verifier v2 or correction logic unless a later phase explicitly starts that work.

## 19. Quick Command Reference

Run verifier on first 5 train sentences:

```bash
python src/verifier/run_on_sentence.py
```

Run verifier batch on first 50 train sentences:

```bash
python src/verifier/run_verifier_batch.py
```

Run gold UD pipeline on first 50 train sentences:

```bash
python src/pipeline/run_gold_ud_pipeline.py
```

Run full gold UD dev baseline:

```bash
python src/pipeline/run_dev_baseline.py
```

Run Stanza sample pipeline:

```bash
python src/pipeline/run_stanza_pipeline_sample.py
```

Run full Stanza dev baseline:

```bash
python src/pipeline/run_stanza_dev_baseline.py
```

Run notebooks from Jupyter or VS Code:

```bash
jupyter notebook
```

## 20. Suggested Reading Order for a New Researcher

1. `docs/methodology/project_context.md`
2. `docs/archive/project_handover_v2.md`
3. `docs/methodology/ud_to_karaka_mapping_v1.md`
4. `docs/methodology/rule_specification_v1.md`
5. `src/mapper/simple_mapper.py`
6. `src/verifier/simple_verifier.py`
7. `src/pipeline/run_gold_ud_pipeline.py`
8. `src/parser/stanza_parser.py`
9. `src/pipeline/run_stanza_dev_baseline.py`
10. `notebooks/analysis/10_stanza_vs_gold_analysis.ipynb`
11. `notebooks/analysis/11_rule_disagreement_analysis.ipynb`

