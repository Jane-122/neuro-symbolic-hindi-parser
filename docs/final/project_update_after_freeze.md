# Project Update After Freeze

**Document purpose:** Chronological record of all work completed after the original frozen neuro-symbolic system was finalized. This supplements `docs/final/final_project_reference.md` and the frozen train/dev/test result reports.

**Scope:** Documentation of repository changes, UDPipe robustness evaluation, and final error analysis. No changes to the frozen symbolic system are described here because none were made.

---

## 1. Original Frozen System

Before any post-freeze work, the project delivered a **frozen neuro-symbolic Karaka extraction pipeline** evaluated on Hindi-HDTB with HDTB-derived gold Karaka labels.

### Components

| Layer | Module | Role |
|-------|--------|------|
| Parser | `src/parser/stanza_parser.py` | Stanza Hindi dependency parsing |
| Mapper v1 | `src/mapper/simple_mapper.py` | Conservative UD deprel → Karaka candidate mapping |
| Verifier v1 | `src/verifier/simple_verifier.py` | Postposition-based candidate refinement |
| Correction Layer v2.1 | `src/pipeline/correction_layer_v2.py` | Single accepted rule **H1** only |

**H1 (only accepted correction rule):**

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

### Evaluation

- **Splits:** train (development), dev (development), test (held-out, run once after freeze).
- **Systems scored:** neural only (`mapper_candidates`), Verifier v1 (`final_candidates`), Correction v2.1 (`corrected_candidates`).
- **Modes:** candidate-set and **strict** (primary).
- **Token matching:** `split + sent_id + normalized token + occurrence order`.

### Final frozen results (Stanza, test)

| System | Strict accuracy | Candidate accuracy |
|--------|----------------:|-------------------:|
| Neural only | 0.4850 | 0.7356 |
| Verifier v1 | 0.5785 | 0.7373 |
| Correction v2.1 | **0.5980** | **0.7568** |

H1 fired **130** times on test; Adhikarana strict F1 improved from 0.7713 to 0.8237.

### Rejected extension: DR1

**Dependency Repair v1 (DR1)** — relabeling `nmod + में/पर` to `obl` — was evaluated on dev and **rejected**. It reduced gold-UD deprel accuracy and was not integrated into the frozen system. Documented in `docs/final/correction_layer_log.md`.

### Original contribution (pre-freeze)

A reproducible **neuro-symbolic Karaka extraction layer over Stanza parses**: frozen Mapper v1 + Verifier v1 + one validated locative correction (H1), evaluated against HDTB-aligned gold Karaka labels, with strict accuracy improving from 0.4850 to 0.5980 on held-out test. The contribution is **semantic role interpretation**, not UD parsing improvement.

---

## 2. Repository Reorganization

**When:** 2026-06-18 (see `MIGRATION_LOG.md`)

**Motivation:** Prepare the repository for a UDPipe parser branch without changing frozen Stanza logic or regenerating existing results.

### Folder restructuring

| Old | New |
|-----|-----|
| `output/` | `outputs/` (`alignment/`, `gold/`, `metrics/`, `error_analysis/`, …) |
| `results/` | `experiments/stanza/` (+ `experiments/udpipe/`, `experiments/rejected/`) |
| Flat `scripts/` | `scripts/{data_prep,evaluation,analysis,experiments,legacy}/` |
| Flat `docs/` | `docs/{final,paper,methodology,experiments,archive}/` |
| Flat `notebooks/` | `notebooks/{exploration,analysis}/` |

### Infrastructure added

- **`src/paths.py`** — central path constants for data, experiments, outputs, and parser branches.
- **`scripts/_bootstrap.py`** — import bootstrap for reorganized script subpackages.

### Documentation cleanup

- Final reference and results moved to `docs/final/`.
- Paper planning assets moved to `docs/paper/`.
- Historical handover notes archived under `docs/archive/`.
- Methodology docs consolidated under `docs/methodology/`.

### Guarantee

All existing Stanza CSV artifacts were **moved**, not regenerated. Frozen mapper, verifier, correction layer, and evaluation formulas were unchanged.

---

## 3. UDPipe Parser Extension

### Purpose

**Parser robustness evaluation** — test whether the frozen symbolic stack generalizes when the neural parser is swapped from Stanza to UDPipe.

This was **not** system improvement: no symbolic rules were added, modified, or tuned for UDPipe.

### Implementation

| Component | Path | Notes |
|-----------|------|-------|
| Package | `ufal.udpipe>=1.2.0` in `requirements.txt` | UDPipe Python bindings |
| Model | `models/udpipe/hindi-hdtb-ud-2.5-191206.udpipe` | Hindi-HDTB UD 2.5 model (~25 MB, gitignored) |
| Parser wrapper | `src/parser/udpipe_parser.py` | Same token-row schema as Stanza wrapper |
| Baseline runner | `src/pipeline/run_udpipe_baseline.py` | Mirrors `run_stanza_baseline.py` |
| Correction application | `scripts/evaluation/apply_correction_v2.py --parser udpipe` | Same H1 logic, no changes |
| Evaluation | `scripts/evaluation/evaluate_correction_v2.py --parser udpipe` | Same formulas and matching |
| Per-Karaka comparison | `scripts/evaluation/compare_correction_v2_per_karaka.py --parser udpipe` | Same metrics |
| Token matching audit | `scripts/analysis/audit_udpipe_token_matching.py` | Split-aware alignment checks |
| Path helpers | `src/paths.py` | `udpipe_baseline_all()`, `udpipe_corrected_all()`, etc. |
| Smoke test | `scripts/experiments/smoke_test_udpipe.py` | Parser sanity check |

### Bug fix (parser wrapper only)

UDPipe CoNLL-U output initially overwrote `sent_id` with `"1"`. The wrapper was fixed to preserve passed sentence IDs (e.g. `dev-s1`, `test-s1`) for gold alignment. This did not change mapper, verifier, or correction logic.

### Explicit statement

**NO symbolic rules changed.** Mapper v1, Verifier v1, Correction Layer v2.1 (H1 only), and evaluation formulas are identical for both parser branches.

---

## 4. UDPipe Experimental Results

**Purpose:** Assess parser robustness, not model tuning. The same frozen symbolic stack was applied to UDPipe parses without parser-specific rule changes.

Sources: `outputs/metrics/udpipe_*_correction_v2_metrics.csv`, token matching audits, per-Karaka comparison files.

### Dev (Correction v2.1)

| Metric | Stanza | UDPipe |
|--------|-------:|-------:|
| Matched gold rows | 5,880 / 5,902 | 5,880 / 5,902 |
| Unmatched gold rows | 22 | 22 |
| Match rate | 99.63% | 99.63% |
| Candidate accuracy | 0.7574 | 0.7135 |
| Strict accuracy | 0.6118 | 0.5701 |
| Adhikarana strict F1 | 0.8335 | 0.8322 |
| Adhikarana candidate F1 | 0.9241 | 0.9157 |
| H1 firing count | 121 | 132 |

UDPipe dev strict accuracy is lower than Stanza, but **token matching and Adhikarana gains from H1 are nearly identical**, indicating the symbolic layer behaves consistently across parsers on the locative pattern H1 targets.

### Test (Correction v2.1)

| Metric | Stanza | UDPipe |
|--------|-------:|-------:|
| Matched gold rows | 5,924 / 5,946 | 5,924 / 5,946 |
| Unmatched gold rows | 22 | 22 |
| Match rate | 99.63% | 99.63% |
| Candidate accuracy | 0.7568 | 0.7153 |
| Strict accuracy | **0.5980** | **0.5646** |
| Adhikarana strict F1 | 0.8237 | 0.8233 |
| Adhikarana candidate F1 | 0.9239 | 0.9116 |
| H1 firing count | 130 | 137 |

**Comparison with Stanza:** UDPipe test strict accuracy is ~3.3 points lower (0.5646 vs 0.5980), mainly from parser-induced differences on subject-like and object-like relations. **Adhikarana strict F1 is virtually unchanged** (0.8237 vs 0.8233), and H1 fires slightly more often on UDPipe (137 vs 130) without parser-specific tuning.

### Interpretation

The UDPipe branch confirms that the **frozen symbolic layer transfers** to a second Hindi UD parser, with the strongest cross-parser stability on H1-targeted Adhikarana cases. Lower overall UDPipe strict accuracy reflects parser quality differences, not symbolic rule failure. This supports reporting parser robustness as a **validation experiment**, not a second tuned system.

---

## 5. Final Error Analysis Additions

### New script

**`scripts/analysis/analyze_final_error_patterns.py`**

- CLI: `--split {dev,test}` `--parser {stanza,udpipe}`
- Joins gold Karaka rows to corrected pipeline outputs using the same matching key as evaluation.
- Classifies each gold row into a failure taxonomy:
  - `strict_correct`
  - `candidate_correct_strict_fail`
  - `candidate_wrong`
  - `no_prediction`
  - `unmatched_gold`

### Outputs per parser/split (`outputs/error_analysis/`)

| File | Content |
|------|---------|
| `{parser}_{split}_final_error_rows.csv` | Row-level error records |
| `{parser}_{split}_failure_by_karaka.csv` | Counts by gold Karaka × failure type |
| `{parser}_{split}_error_patterns.csv` | Counts by gold Karaka × deprel × case marker |
| `{parser}_{split}_confusion_summary.csv` | Gold vs strict prediction pairs |
| `{parser}_{split}_karma_sampradana_cases.csv` | Focused Karma/Sampradana subset |
| `{parser}_{split}_karana_apadana_cases.csv` | Focused Karana/Apadana subset |
| `{parser}_{split}_h1_success_rows.csv` | Rows where H1 fired |

### Summaries produced

**Failure taxonomy (test, Correction v2.1):**

| failure_type | Stanza | UDPipe |
|---|---:|---:|
| strict_correct | 3,556 | 3,357 |
| no_prediction | 1,121 | 1,267 |
| candidate_correct_strict_fail | 944 | 896 |
| candidate_wrong | 303 | 404 |
| unmatched_gold | 22 | 22 |

**Top recurring error categories (merged, test):**

1. Unsupported UD dependency relations (`mark`, `compound`, `cc`, `root`) — ~818 / ~800
2. Karma–Sampradana ambiguity with `को` — 480 / 450
3. Karana–Apadana ambiguity with `से` — 171 / 166
4. Residual Adhikarana ambiguity — 290 / 284
5. Karta recall gaps — 278 / 373

**H1 success analysis:** 117 Stanza and 123 UDPipe gold-aligned test rows where H1 fired; sampled cases are Adhikarana `nmod + में/पर` with strict correct predictions.

**Sanity check:** `outputs/error_analysis/paper_error_analysis_sanity_check.md` — 20 random samples confirmed the unsupported-UD row is valid (`no_prediction` on structural deprels).

**Publication-ready table:**

- `outputs/error_analysis/paper_error_analysis_table_v2.csv`
- `outputs/error_analysis/paper_error_analysis_table_v2.md`

Six-row compact table with interpretations and likely future directions for the paper.

---

## 6. Scientific Conclusions Strengthened

Post-freeze work supports the following claims without changing the frozen system:

1. **Cross-parser evaluation:** The symbolic layer (Mapper v1, Verifier v1, H1) was evaluated on both Stanza and UDPipe under identical rules and metrics.
2. **H1 is not Stanza-specific:** Adhikarana strict F1 on test is 0.8237 (Stanza) vs 0.8233 (UDPipe); H1 fires on both parsers without parser-specific tuning.
3. **Remaining failures are linguistically interpretable:** Error analysis groups failures into unsupported deprels, `को`/`से` ambiguity, residual Adhikarana gaps, and Karta recall issues — not opaque model errors.
4. **Future work is evidence-motivated:** The paper table maps each error category to concrete directions (semantic disambiguation, locative expansion, alignment audit) rather than ad hoc rule addition.
5. **Parser choice affects magnitude, not mechanism:** UDPipe lowers strict accuracy but does not invalidate the symbolic pipeline design; hard wrong-label cases are more frequent for UDPipe but are treated as parser noise, not a separate linguistic category.

---

## 7. What Did NOT Change

The following were explicitly frozen and remain unchanged:

| Component | Status |
|-----------|--------|
| Mapper v1 (`src/mapper/simple_mapper.py`) | Unchanged |
| Verifier v1 (`src/verifier/simple_verifier.py`) | Unchanged |
| Correction Layer v2.1 / H1 (`src/pipeline/correction_layer_v2.py`) | Unchanged |
| Symbolic rules (R1–R5, H1; no new rules) | Unchanged |
| Evaluation formulas (`evaluate_pipeline_against_gold.py`, `evaluate_correction_v2.py`) | Unchanged |
| Stanza train/dev/test metrics (`outputs/metrics/*` Stanza files) | Unchanged |
| Frozen symbolic system specification | Unchanged |
| DR1 | Remains rejected; not integrated |

Post-freeze work added **parallel UDPipe experiment artifacts**, **error-analysis outputs**, **documentation**, and **repository structure** only.

---

## Related Documents

| Document | Role |
|----------|------|
| `docs/final/final_project_reference.md` | Full pre-freeze implementation handbook |
| `docs/final/final_train_dev_results.md` | Stanza train/dev metrics + UDPipe dev note |
| `docs/final/final_test_results.md` | Stanza test metrics + cross-parser section |
| `docs/final/project_timeline.md` | One-page project timeline |
| `docs/final/project_context.md` | Current repository status |
| `MIGRATION_LOG.md` | Reorganization path map |
| `outputs/error_analysis/paper_error_analysis_table_v2.md` | Paper-ready error table |
