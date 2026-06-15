# Project Handover Document (Version 1)

**Document purpose:** Complete implementation handover for the neuro-symbolic Hindi parser research project. A new collaborator or AI assistant should be able to continue work from this document alone.

**Last updated:** June 2026  
**Pipeline version:** v1 (frozen for baseline evaluation; v2 not yet designed)  
**Primary authority:** `docs/project_context.md`

---

## Section 1: Project Overview

### 1.1 Full Project Title

**Neuro-Symbolic Dependency Parsing for Hindi: Integrating Paninian Karaka Rules with Neural Parsers**

### 1.2 Research Objective

Build a small, reproducible neuro-symbolic pipeline that:

1. Takes Hindi dependency parses (Universal Dependencies format).
2. Applies a conservative UD-to-Karaka mapping as an initial hypothesis.
3. Runs a Paninian rule-based verifier over those hypotheses using postposition evidence.
4. Produces structured outputs with explicit decision types.
5. Evaluates where symbolic reasoning helps, where it fails, and where it correctly withholds judgment.

**Research question:** Can Paninian Karaka-based symbolic rules verify or correct the outputs of a Hindi dependency parser?

### 1.3 Why Hindi-HDTB (UD) Is Used

Hindi-HDTB (`hi_hdtb-ud-train/dev/test.conllu`) is the project's current data source because:

- It provides gold-standard UD dependency trees for Hindi at scale.
- It includes rich postposition (`case`) annotations needed for rule design.
- It is publicly available, well documented, and standard in UD-based NLP research.
- It allows reproducible analysis before integrating a separate neural parser.

Current pipeline runs use **gold UD trees** from the treebank. This is intentional for v1: it isolates mapper and verifier behavior from parser noise.

### 1.4 Why Paninian Dependency Labels Are Not Used Yet

The project does **not** use a Paninian-style dependency annotation scheme or Karaka gold labels because:

- Hindi-HDTB is annotated in Universal Dependencies, not in Paninian Karaka roles.
- No Karaka gold standard exists in the repository for automatic evaluation.
- The research contribution is a **verifier over UD outputs**, not a full treebank conversion.
- v1 rules are hypotheses derived from UD postposition statistics and manual inspection, not from a complete Paninian grammar implementation.

Karaka names (Kartā, Karma, etc.) appear as **candidate outputs**, not as input labels.

### 1.5 Role of the Mapper

**File:** `src/mapper/simple_mapper.py`

The mapper provides a **conservative, deprel-only** initial Karaka hypothesis:

- Input: UD `deprel` label only.
- Output: `karaka_candidates`, `confidence`, `mapping_status`, `reason`.
- It does **not** use postpositions.
- It is a starting guess for the pipeline, not final truth.

When the verifier has no opinion, the pipeline may surface the mapper output as `mapping_hypothesis`.

### 1.6 Role of the Verifier

**File:** `src/verifier/simple_verifier.py`

The verifier is the **primary research contribution**. It:

- Takes `deprel` plus an optional child `case` marker (postposition form).
- Applies rules R1 to R5 from `docs/rule_specification_v1.md`.
- Returns `confirmed`, `ambiguous`, or `no_decision` (v1 code does not return `corrected` yet).
- Prefers `ambiguous` or `no_decision` over forced wrong assignments.

The verifier uses postposition evidence because train/dev analysis showed strong associations between postpositions and parent deprels.

### 1.7 Long-Term Neuro-Symbolic Goal

Long term, the system should:

1. Accept parses from a neural Hindi UD parser (e.g. Stanza) instead of gold trees only.
2. Map UD outputs to Karaka hypotheses.
3. Verify or correct those hypotheses with symbolic Paninian rules.
4. Report explicit decisions (`confirmed`, `corrected`, `ambiguous`, `no_decision`, and pipeline-level `mapping_hypothesis`).
5. Measure where symbolic reasoning improves interpretability or accuracy over parser output alone.

v1 deliberately stops before Stanza integration and verifier v2 design.

---

## Section 2: Current Repository Structure

### 2.1 High-Level Tree (Important Files Only)

```
neuro-symbolic-hindi-parser/
├── data/
│   └── raw/
│       ├── hi_hdtb-ud-train.conllu    # Train split (used for rule design, pilots)
│       ├── hi_hdtb-ud-dev.conllu      # Dev split (full baseline completed)
│       └── hi_hdtb-ud-test.conllu     # Test split (not yet used)
├── docs/
│   ├── project_context.md             # Primary project authority
│   ├── project_handover_v1.md         # This document
│   ├── ud_to_karaka_mapping_v1.md   # Mapping hypothesis (v1)
│   ├── rule_specification_v1.md       # Verifier rules R1-R5 (spec)
│   ├── rule_specification_audit.md    # Statistical audit of rule spec
│   ├── verifier_output_observations_v1.md
│   ├── verifier_failure_analysis_v1.md
│   ├── verifier_v1_dev_baseline.md
│   ├── research_notes.md              # Partially filled
│   ├── project_scope.md               # Placeholder sections
│   └── ud_to_karaka_mapping.md        # Placeholder sections
├── notebooks/
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_postposition_analysis.ipynb
│   ├── 03_dev_postposition_comparison.ipynb
│   ├── 05_verifier_output_analysis.ipynb
│   ├── 06_verifier_failure_analysis.ipynb
│   ├── 07_pipeline_analysis.ipynb
│   └── 09_dev_baseline_analysis.ipynb
├── results/
│   ├── run_on_sentence_output.txt
│   ├── verifier_batch_all.csv
│   ├── verifier_batch_meaningful.csv
│   ├── gold_ud_pipeline_all.csv
│   ├── gold_ud_pipeline_meaningful.csv
│   ├── dev_baseline_all.csv
│   └── dev_baseline_meaningful.csv
├── src/
│   ├── mapper/
│   │   └── simple_mapper.py
│   ├── verifier/
│   │   ├── simple_verifier.py
│   │   ├── run_on_sentence.py
│   │   └── run_verifier_batch.py
│   └── pipeline/
│       ├── run_gold_ud_pipeline.py
│       └── run_dev_baseline.py
├── README.md                          # Outdated status section
└── requirements.txt                   # Python dependencies (Jupyter, pandas, etc.)
```

**Note:** There is no `src/parser/` or `src/evaluation/` implementation yet. Notebook 04 and 08 do not exist.

### 2.2 Documentation Files

| File | Purpose | Status | How Used |
|------|---------|--------|----------|
| `project_context.md` | Research goals, scope, decision types, style rules | **Active** | Primary reference for all work |
| `project_handover_v1.md` | Implementation handover (this file) | **Active** | Onboarding and continuation |
| `ud_to_karaka_mapping_v1.md` | v1 mapping hypothesis table | **Active** | Mapper design reference |
| `rule_specification_v1.md` | Verifier rules R1-R5 | **Active** (header says "not implemented"; code exists) | Verifier design reference |
| `rule_specification_audit.md` | Audit of rule percentages vs notebook 02 | **Active** | Evidence validation |
| `verifier_output_observations_v1.md` | 50-sentence batch inspection notes | **Active** | Qualitative verifier review |
| `verifier_failure_analysis_v1.md` | Failure modes from meaningful batch rows | **Active** | v2 planning input |
| `verifier_v1_dev_baseline.md` | Full dev baseline statistics | **Active** | Baseline report |
| `research_notes.md` | Scratch pad for pipeline labels | **Partial** | Pipeline decision definitions only |
| `project_scope.md` | Intended scope outline | **Placeholder** | Not filled in |
| `ud_to_karaka_mapping.md` | Non-versioned mapping doc | **Placeholder** | Superseded by `_v1` |

### 2.3 Notebooks

| Notebook | Purpose | Status | How Used |
|----------|---------|--------|----------|
| `01_dataset_exploration.ipynb` | Train corpus stats, deprel counts | **Active** | Phase 1 evidence |
| `02_postposition_analysis.ipynb` | Postposition to parent deprel stats (train) | **Active** | Rule design evidence |
| `03_dev_postposition_comparison.ipynb` | Train vs dev postposition comparison | **Active** | Rule generalization check |
| `05_verifier_output_analysis.ipynb` | Inspect verifier batch meaningful CSV | **Active** | Verifier output QA |
| `06_verifier_failure_analysis.ipynb` | Failure analysis on meaningful rows | **Active** | v2 planning input |
| `07_pipeline_analysis.ipynb` | Inspect combined pipeline (50 train sents) | **Active** | Pipeline QA |
| `09_dev_baseline_analysis.ipynb` | Dev baseline summary and examples | **Active** | Dev evaluation review |

### 2.4 Source Code

| File | Purpose | Status | How Used |
|------|---------|--------|----------|
| `mapper/simple_mapper.py` | `map_ud_to_karaka(deprel)` | **Active** | Pipeline step 1 |
| `verifier/simple_verifier.py` | `verify_token(deprel, case_marker)` | **Active** | Pipeline step 2 |
| `verifier/run_on_sentence.py` | Verifier on 5 train sentences | **Active** | Smoke test, debug |
| `verifier/run_verifier_batch.py` | Verifier on 50 train sentences | **Active** | Early batch CSV |
| `pipeline/run_gold_ud_pipeline.py` | Combined pipeline, 50 train sentences | **Active** | Train pilot |
| `pipeline/run_dev_baseline.py` | Combined pipeline, full dev split | **Active** | Dev baseline |

### 2.5 Results Files

| File | Purpose | Status | How Used |
|------|---------|--------|----------|
| `run_on_sentence_output.txt` | Printed verifier output (5 sentences) | **Active** | Manual inspection |
| `verifier_batch_all.csv` | Verifier only, 50 sents, all tokens | **Active** | Notebook 05, 06 input |
| `verifier_batch_meaningful.csv` | Verifier only, non-no_decision rows | **Active** | Notebook 05, 06 input |
| `gold_ud_pipeline_all.csv` | Pipeline, 50 sents, all tokens | **Active** | Notebook 07 |
| `gold_ud_pipeline_meaningful.csv` | Pipeline, 50 sents, meaningful rows | **Active** | Notebook 07 |
| `dev_baseline_all.csv` | Pipeline, full dev, all tokens | **Active** | Notebook 09, baseline report |
| `dev_baseline_meaningful.csv` | Pipeline, full dev, meaningful rows | **Active** | Notebook 09, baseline report |

Regenerate commands:

```bash
python src/verifier/run_verifier_batch.py
python src/pipeline/run_gold_ud_pipeline.py
python src/pipeline/run_dev_baseline.py
```

---

## Section 3: Completed Phases

### Phase 1: Dataset Exploration

**Objective:** Understand Hindi-HDTB train structure before rule design.

**Files created:**
- `notebooks/01_dataset_exploration.ipynb`

**Key findings:**
- Train: 13,306 sentences, 28 unique deprel labels.
- 53,121 `case` tokens; `case` is the most frequent deprel.
- Examples documented for `nsubj`, `obj`, `obl`, `iobj`, `case`.

**Outputs:** Notebook tables and counts; input to mapping v1 document.

---

### Phase 2: Postposition Analysis

**Objective:** Measure postposition to parent-deprel associations on train data for rule evidence.

**Files created:**
- `notebooks/02_postposition_analysis.ipynb`

**Key findings (train, focus postpositions):**

| Postposition | Top parent | Train % |
|--------------|------------|--------:|
| ने | nsubj | 98.4% |
| में | obl | 87.6% |
| पर | obl | 89.8% |
| से | obl | 69.5% |
| को | obj | 45.2% |

**Outputs:** Statistical basis for R1 to R5 in `docs/rule_specification_v1.md`.

---

### Phase 3: Train-Dev Validation

**Objective:** Check whether postposition patterns generalize to dev split.

**Files created:**
- `notebooks/03_dev_postposition_comparison.ipynb`

**Key findings:**
- Dev: 6,674 `case` tokens.
- Rule-critical patterns stable (differences mostly under 2.5 pp for top labels).
- Largest R5 shift: `को`+`obl` (17.6% train vs 13.3% dev, 4.3 pp).
- R1 to R4 patterns hold on dev.

**Outputs:** Evidence that train-derived rules are reasonable for dev evaluation.

---

### Phase 4: Rule Specification

**Objective:** Formalize v1 verifier rules as documented hypotheses.

**Files created:**
- `docs/ud_to_karaka_mapping_v1.md`
- `docs/rule_specification_v1.md`
- `docs/rule_specification_audit.md`

**Key findings:**
- Five rules (R1 to R5) cover `ने`, `में`, `पर`, `से`, `को` on specific parent deprels.
- Audit confirmed cited train percentages against notebook 02.
- Karaka role claims remain linguistic hypotheses without gold Karaka evaluation.

**Outputs:** Rule spec and audit report.

---

### Phase 5: Verifier v1

**Objective:** Implement token-level verifier in code.

**Files created:**
- `src/verifier/simple_verifier.py`
- `src/verifier/run_on_sentence.py`

**Key findings:**
- `verify_token(deprel, case_marker)` implements R1 to R5.
- Returns dict with `karaka_candidates`, `decision_type`, `confidence`, `rule_id`, `reason`.
- Manual test block included under `if __name__ == "__main__"`.

**Outputs:** Working verifier module; `results/run_on_sentence_output.txt`.

---

### Phase 6: Verifier Batch Evaluation

**Objective:** Run verifier on 50 train sentences and save CSV outputs.

**Files created:**
- `src/verifier/run_verifier_batch.py`
- `results/verifier_batch_all.csv`
- `results/verifier_batch_meaningful.csv`

**Key findings (50 sentences, 779 tokens):**
- `confirmed`: 19
- `ambiguous`: 17
- `no_decision`: 743
- Rules: R1:3, R2:15, R3:1, R4:11, R5:6

**Outputs:** Batch CSVs for analysis notebooks.

---

### Phase 7: Failure Analysis

**Objective:** Inspect verifier meaningful outputs for strengths, gaps, and v2 candidates.

**Files created:**
- `notebooks/05_verifier_output_analysis.ipynb`
- `notebooks/06_verifier_failure_analysis.ipynb`
- `docs/verifier_output_observations_v1.md`
- `docs/verifier_failure_analysis_v1.md`

**Key findings:**
- R1 strongest; R2 over-confirms extent/time/manner `में` cases.
- R4 manner adverbials (`रूप से`, `तरह से`) grouped with Karaṇa|Apādāna.
- R5 often object-like but correctly left ambiguous.
- 73 tokens in batch had case markers but no rule match.

**Outputs:** Qualitative failure taxonomy for future rule refinement.

---

### Phase 8: Mapper v1

**Objective:** Implement conservative deprel-only UD-to-Karaka mapper.

**Files created:**
- `src/mapper/simple_mapper.py`

**Key findings:**
- Maps `nsubj`, `obj`, `iobj`, `obl`, `root`, `case` only.
- All other deprels return `unsupported`.
- No postposition logic by design.

**Outputs:** `map_ud_to_karaka(deprel)` function.

---

### Phase 9: Combined Pipeline

**Objective:** Run mapper and verifier together on gold UD sentences.

**Files created:**
- `src/pipeline/run_gold_ud_pipeline.py`
- `notebooks/07_pipeline_analysis.ipynb`
- `results/gold_ud_pipeline_all.csv`
- `results/gold_ud_pipeline_meaningful.csv`

**Key findings (50 train sentences, 779 tokens):**

| final_decision | Count | % |
|----------------|------:|--:|
| no_decision | 662 | 84.98% |
| mapping_hypothesis | 81 | 10.40% |
| confirmed | 19 | 2.44% |
| ambiguous | 17 | 2.18% |

- Label renamed from `mapper_only` to `mapping_hypothesis` for scientific accuracy.
- Many `mapping_hypothesis` nsubj rows are copular subjects (weak Kartā guesses).

**Outputs:** Combined pipeline CSVs and pipeline analysis notebook.

---

### Phase 10: Full Dev Baseline Evaluation

**Objective:** Run Pipeline v1 on entire dev split and record baseline statistics.

**Files created:**
- `src/pipeline/run_dev_baseline.py`
- `notebooks/09_dev_baseline_analysis.ipynb`
- `docs/verifier_v1_dev_baseline.md`
- `results/dev_baseline_all.csv`
- `results/dev_baseline_meaningful.csv`

**Key findings:** See Section 7 (dev baseline).

**Outputs:** Full dev baseline CSVs and report.

---

## Section 4: Verifier v1 Specification

Rules are implemented in `src/verifier/simple_verifier.py` and documented in `docs/rule_specification_v1.md`.

### 4.1 Rule Summary

| Rule | Condition | Karaka | Decision | Confidence (code) |
|------|-----------|--------|----------|-------------------|
| **R1** | `nsubj` + child `case` = `ने` | Kartā | `confirmed` | high |
| **R2** | `obl` + child `case` = `में` | Adhikaraṇa | `confirmed` | medium-high |
| **R3** | `obl` + child `case` = `पर` | Adhikaraṇa | `confirmed` | medium-high |
| **R4** | `obl` + child `case` = `से` | Karaṇa or Apādāna | `ambiguous` | low-medium |
| **R5** | `obj` or `iobj` + child `case` = `को` | Karma or Sampradāna | `ambiguous` | low-medium |

### 4.2 Per-Rule Detail

**R1**
- **Trigger:** Parent has `deprel = nsubj` and a child case token with form `ने`.
- **Karaka:** Kartā (agent).
- **Decision:** `confirmed`.
- **Confidence philosophy:** Strongest postposition association in corpus (~98.4% `ने` to `nsubj` on train). High confidence is justified for this UD configuration, but this is not gold Karaka validation.

**R2**
- **Trigger:** Parent `obl` + case `में`.
- **Karaka:** Adhikaraṇa (locative/locus).
- **Decision:** `confirmed`.
- **Confidence philosophy:** Strong obl association (~87.6% train). Medium-high because `में` also marks extent, time, and manner in practice.

**R3**
- **Trigger:** Parent `obl` + case `पर`.
- **Karaka:** Adhikaraṇa (surface/location).
- **Decision:** `confirmed`.
- **Confidence philosophy:** Strong obl association (~89.8% train). Medium-high; surface location is the intended reading.

**R4**
- **Trigger:** Parent `obl` + case `से`.
- **Karaka:** Karaṇa (instrument) or Apādāna (source/separation).
- **Decision:** `ambiguous`.
- **Confidence philosophy:** `से` is mixed (instrument, source, manner). UD `obl` alone cannot disambiguate. Verifier must not force one label.

**R5**
- **Trigger:** Parent `obj` or `iobj` + case `को`.
- **Karaka:** Karma (patient) or Sampradāna (recipient).
- **Decision:** `ambiguous`.
- **Confidence philosophy:** `को` is highly mixed across parent deprels. Syntax alone does not separate Karma from Sampradāna.

### 4.3 Verifier Decision Types

| Type | Meaning in v1 code |
|------|-------------------|
| `confirmed` | Postposition evidence supports a single Karaka candidate (R1, R2, R3). |
| `ambiguous` | Multiple Karaka candidates remain plausible (R4, R5). |
| `no_decision` | No rule matched; includes missing case marker, wrong deprel, or unsupported combinations. |
| `corrected` | **Specified in docs but not implemented in v1 code.** Reserved for mapper-verifier conflict resolution. |

---

## Section 5: Mapper v1 Specification

**File:** `src/mapper/simple_mapper.py`  
**Reference:** `docs/ud_to_karaka_mapping_v1.md`

### 5.1 Supported Deprels

| deprel | karaka_candidates | confidence | mapping_status |
|--------|-------------------|------------|----------------|
| `nsubj` | Kartā | low-medium | mapped |
| `obj` | Karma | medium | mapped |
| `iobj` | Sampradāna | medium | mapped |
| `obl` | Adhikaraṇa, Apādāna, Karaṇa | low | context_dependent |
| `root` | (none) | high | no_karaka |
| `case` | (none) | high | evidence_only |
| all others | (none) | none | unsupported |

### 5.2 Mapping Logic

Function: `map_ud_to_karaka(deprel: str) -> dict`

Returns: `karaka_candidates`, `confidence`, `mapping_status`, `reason`.

No access to postpositions, verb lemmas, or sentence context.

### 5.3 Limitations

- `nsubj` is not always Kartā (copular subjects, non-agent topics).
- `obl` mapping is a triple disjunction without resolution.
- Most tokens in a sentence are `unsupported` (e.g. `compound`, `det`, `amod`, `punct`).
- Mapper cannot emit `corrected` or compare against verifier output.

### 5.4 Why the Mapper Does Not Use Postpositions

Postposition disambiguation is the **verifier's job** by project design:

- The mapper is a conservative syntactic hypothesis layer.
- Postposition rules (R1 to R5) were derived from statistical analysis and belong in the verifier.
- Keeping layers separate avoids duplicating logic and makes pipeline decisions interpretable: mapper guess vs verifier-backed judgment.

---

## Section 6: Pipeline v1 Architecture

**Core logic:** `src/pipeline/run_gold_ud_pipeline.py` (reused by `run_dev_baseline.py`)

### 6.1 Step-by-Step Flow

```
CONLL-U sentence
    |
    v
For each token:
    extract deprel, case_marker (first child with deprel=case)
    |
    +--> map_ud_to_karaka(deprel)
    |         mapper_candidates, mapper_status, mapper_confidence
    |
    +--> verify_token(deprel, case_marker)
    |         verifier_candidates, verifier_decision, verifier_rule_id
    |
    v
combine_results(mapper, verifier)
    |
    v
final_candidates, final_decision, final_reason
    |
    v
CSV row
```

### 6.2 Merge Priority (v1)

1. If verifier returns `confirmed`: use verifier candidates; `final_decision = confirmed`.
2. If verifier returns `ambiguous`: use verifier candidates; `final_decision = ambiguous`.
3. If verifier returns `no_decision` and mapper has candidates: use mapper candidates; `final_decision = mapping_hypothesis`.
4. Otherwise: empty candidates; `final_decision = no_decision`.

### 6.3 Final Decision Types (Pipeline Level)

| final_decision | Source | Meaning |
|----------------|--------|---------|
| `confirmed` | Verifier | Postposition rule strongly supports one Karaka. |
| `ambiguous` | Verifier | Multiple Karakas remain plausible. |
| `mapping_hypothesis` | Mapper | Unverified guess from UD deprel only; verifier silent. |
| `no_decision` | Neither | No usable Karaka candidate from either layer. |

**Note:** `corrected` is not yet a pipeline output.

---

## Section 7: Current Results

### 7.1 Train Pilot (50 Sentences, Gold UD)

**Script:** `run_gold_ud_pipeline.py`  
**Tokens:** 779  
**Sentences:** 50

| final_decision | Count | % of tokens |
|----------------|------:|------------:|
| no_decision | 662 | 84.98% |
| mapping_hypothesis | 81 | 10.40% |
| confirmed | 19 | 2.44% |
| ambiguous | 17 | 2.18% |
| **Meaningful total** | **117** | **15.02%** |

Verifier-only batch (same 50 sentences): 36 meaningful rows (19 confirmed, 17 ambiguous).

**Meaning:** Small manual-review pilot. Confirmed cases are mostly R1 agents and spatial R2/R3. Many mapping_hypothesis rows are copular nsubj mapped to Kartā.

### 7.2 Full Dev Baseline (1,659 Sentences, Gold UD)

**Script:** `run_dev_baseline.py`  
**Tokens:** 35,217  
**Sentences:** 1,659

| final_decision | Count | % of all tokens |
|----------------|------:|----------------:|
| no_decision | 28,198 | 80.07% |
| mapping_hypothesis | 4,464 | 12.68% |
| confirmed | 1,715 | 4.87% |
| ambiguous | 840 | 2.39% |
| **Meaningful total** | **7,019** | **19.93%** |

**Among meaningful rows only:**

| final_decision | Count | % of meaningful |
|----------------|------:|----------------:|
| mapping_hypothesis | 4,464 | 63.60% |
| confirmed | 1,715 | 24.44% |
| ambiguous | 840 | 11.97% |

**Verifier rule hits (dev, all tokens):**

| Rule | Count | % of all tokens |
|------|------:|----------------:|
| R2 | 847 | 2.41% |
| R1 | 556 | 1.58% |
| R5 | 499 | 1.42% |
| R4 | 341 | 0.97% |
| R3 | 312 | 0.89% |
| **Total rule hits** | **2,555** | **7.26%** |

### 7.3 Why ~80% `no_decision` Is Not a Failure

High `no_decision` rate is **expected and intentional** in v1 because:

1. **Narrow rule coverage:** Only five postposition patterns on specific parent deprels trigger the verifier.
2. **Most tokens are not Karaka-bearing:** `case`, `compound`, `det`, `punct`, `amod`, and similar labels dominate the tree.
3. **Conservative design:** The verifier prefers `no_decision` over wrong forced Karaka assignments.
4. **Mapper coverage is limited:** Only six deprels are mapped; the rest are `unsupported`.
5. **Gold tree density:** Many tokens simply lack the postposition evidence v1 requires.

A low hit rate on **all tokens** does not mean the verifier failed. It means v1 correctly abstains on most tokens. Evaluation should focus on:

- Quality of `confirmed` and `ambiguous` cases (manual inspection).
- Whether `mapping_hypothesis` rows are plausible as hypotheses.
- Rule firing rates on tokens that **do** match rule conditions.

The dev meaningful rate (~20%) shows the pipeline produces reviewable output at scale.

---

## Section 8: Research Conclusions So Far

### 8.1 What Has Been Validated

- Hindi-HDTB postposition to parent-deprel associations are stable between train and dev for R1 to R4 focus patterns (notebook 03).
- Rule spec percentages were audited against notebook 02 (audit report).
- Verifier v1 implements the documented R1 to R5 logic and runs at scale on dev.
- Mapper v1 and pipeline v1 integrate without modifying each other's logic.
- R1 (`ने`+`nsubj`) and clear spatial R2/R3 cases appear sensible in manual inspection (small samples).
- Pipeline produces structured CSV outputs suitable for analysis and future parser comparison.

### 8.2 What Has Not Been Validated

- Karaka correctness against gold Paninian annotations (no gold Karaka dataset in repo).
- Verifier accuracy on **parser-produced** UD (Stanza not integrated).
- Test split baseline (not yet run).
- Whether `confirmed` R2 labels are always true Adhikaraṇa (extent/time/manner cases are problematic).
- Automatic disambiguation of R4 and R5.
- `corrected` decision logic when mapper and verifier disagree.

### 8.3 Strengths of v1

- Small, readable, modular codebase.
- Explicit decision types and CSV audit trail.
- Conservative abstention instead of over-labeling.
- Reproducible notebooks and documented evidence chain from data to rules to code.
- Dev baseline establishes reference statistics for future comparison.

### 8.4 Weaknesses of v1

- R2 over-generalizes `में` to Adhikaraṇa for extent, time, and manner.
- R4 groups manner adverbials with Karaṇa|Apādāna.
- R5 cannot resolve Karma vs Sampradāna.
- Mapper assigns Kartā to many non-agent `nsubj` tokens.
- No `corrected` output for mapper-verifier conflict.
- CONLL-U loading duplicated across scripts.
- README and rule spec header are partially outdated.

---

## Section 9: Next Steps

### 9.1 Immediate Next Step: Full Test Baseline

Run Pipeline v1 on the entire test split using the same pattern as dev:

- Create `src/pipeline/run_test_baseline.py` (or parameterize `run_dev_baseline.py`).
- Input: `data/raw/hi_hdtb-ud-test.conllu`
- Output: `results/test_baseline_all.csv`, `results/test_baseline_meaningful.csv`
- Document in `docs/verifier_v1_test_baseline.md` and optional notebook.

This completes gold-UD baselines for all three splits before parser integration.

### 9.2 After That: Stanza Integration

- Run Stanza Hindi UD parser on raw sentences.
- Feed parser output (not gold trees) into the same mapper + verifier pipeline.
- Compare Stanza-driven vs gold-UD decision distributions.
- Measure parser error impact on rule firing rates.

Do **not** start Stanza until test baseline is done and verifier v1 is frozen.

### 9.3 After That: Parser Error Analysis

- Identify where parser deprel or attachment errors break rule conditions.
- Categorize errors by rule (R1 to R5) and by final_decision type.
- Use errors as **evidence for v2**, not speculation.

### 9.4 After That: Verifier v2 Design

- Design v2 only after test baseline and Stanza error analysis.
- Candidate refinements from failure analysis (not yet implemented):
  - R2 subtypes for spatial vs temporal/extent/manner `में`.
  - R4 manner filter for `रूप से` / `तरह से`.
  - Verb-frame disambiguation for R4 and R5.
  - `corrected` decision when mapper and verifier conflict.
- **Freeze verifier v1** before implementing v2.

---

## Section 10: Important Project Decisions

| Decision | Rationale |
|----------|-----------|
| **Main contribution is the verifier, not the mapper** | Mapping is a hypothesis; postposition rules are the research focus. |
| **Use gold UD first, parser later** | Isolates symbolic layer quality before adding parser noise. |
| **Five postposition rules only (v1)** | Evidence-based scope from train/dev statistics; avoid full Paninian grammar. |
| **Conservative abstention** | Prefer `no_decision` and `ambiguous` over wrong Karaka labels. |
| **Separate mapper and verifier** | Mapper: deprel only. Verifier: postposition evidence. |
| **Rename `mapper_only` to `mapping_hypothesis`** | Scientifically accurate: unverified guess, not a decision. |
| **Freeze verifier v1 before v2** | Dev baseline must be reference point; v2 driven by errors, not speculation. |
| **Build v2 from parser errors, not speculation** | Failure analysis and Stanza runs precede new rules. |
| **Avoid premature complexity** | No neural training, no HTDB, no full ontology in v1. |
| **No Karaka gold evaluation yet** | Report pipeline behavior counts; do not overclaim linguistic accuracy. |
| **Document style: no em dashes** | Professional, cautious scientific prose (see `project_context.md`). |
| **Incremental notebooks and CSV outputs** | Reproducibility over monolithic scripts. |

---

## Appendix A: Quick Command Reference

```bash
# Verifier smoke test (5 sentences)
python src/verifier/run_on_sentence.py

# Verifier batch (50 train sentences)
python src/verifier/run_verifier_batch.py

# Combined pipeline pilot (50 train sentences)
python src/pipeline/run_gold_ud_pipeline.py

# Full dev baseline
python src/pipeline/run_dev_baseline.py

# Mapper manual tests
python src/mapper/simple_mapper.py

# Verifier manual tests
python src/verifier/simple_verifier.py
```

---

## Appendix B: Key File Reading Order for New Contributors

1. `docs/project_context.md`
2. `docs/project_handover_v1.md` (this file)
3. `docs/ud_to_karaka_mapping_v1.md`
4. `docs/rule_specification_v1.md`
5. `src/mapper/simple_mapper.py`
6. `src/verifier/simple_verifier.py`
7. `src/pipeline/run_gold_ud_pipeline.py`
8. `docs/verifier_v1_dev_baseline.md`

---

*End of Project Handover Document v1*
