# Project Archive v1

**Single source of truth for the final project state**

**Last updated:** Post-freeze documentation (2026)  
**Audience:** Future readers returning to the repository without reading every handover, checkpoint, or migration note.

**Companion documents (detail, not required for overview):**

| Document | Role |
|----------|------|
| `docs/final/final_project_reference.md` | Full implementation handbook (pre- and post-freeze phases) |
| `docs/final/project_update_after_freeze.md` | Chronology of post-freeze work only |
| `docs/final/final_train_dev_results.md` | Stanza train/dev metrics |
| `docs/final/final_test_results.md` | Stanza test + cross-parser comparison |
| `docs/final/correction_layer_log.md` | H1 acceptance, DR1 rejection, passive diagnostics |
| `MIGRATION_LOG.md` | Repository reorganization path map |

---

## 1. Project Identity

### Final title

**Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses**

### Final framing

The project improves **Karaka (semantic role) extraction from neural Universal Dependencies parses**. It does **not** claim to improve UD dependency parsing accuracy (UAS/LAS/deprel accuracy on the final system).

### Main goal

Build and evaluate a **small, frozen, auditable neuro-symbolic layer** — Mapper v1, Verifier v1, and Correction Layer v2.1 — that interprets Hindi neural parser output into Paninian-inspired Karaka labels, evaluated against HDTB-derived gold Karaka annotations aligned to Hindi-HDTB UD.

### What this project is

- A **Karaka extraction pipeline** over Stanza (primary) and UDPipe (robustness) parses.
- A **rule-based verifier** using postposition evidence with explicit ambiguity handling.
- One **validated correction rule (H1)** for locative `nmod + में/पर → Adhikarana`.
- An **alignment-based evaluation setup** linking Hindi-HDTB UD to original HDTB gold.
- A **documented negative result** (DR1) separating Karaka correction from deprel repair.

### What this project is not

- Not a Hindi dependency parser or parser retraining project.
- Not a full Paninian Karaka analyzer covering all HDTB semantic labels.
- Not a UDPipe-tuned second symbolic system (UDPipe uses identical frozen rules).
- Not a claim that postposition rules alone resolve all Karaka ambiguity.

---

## 2. Final Repository Structure

After reorganization (see `MIGRATION_LOG.md`), the repository layout is:

```text
neuro-symbolic-hindi-parser/
├── src/                    # Core Python packages
│   ├── mapper/             # Mapper v1
│   ├── verifier/           # Verifier v1
│   ├── parser/             # Stanza + UDPipe wrappers
│   ├── pipeline/           # Runners, correction layer, DR1 (rejected)
│   └── paths.py            # Central path constants
├── scripts/
│   ├── data_prep/          # Alignment, gold label extraction
│   ├── evaluation/         # Metrics, correction application
│   ├── analysis/           # Error analysis, audits
│   ├── experiments/        # DR1, UDPipe smoke tests
│   └── legacy/             # Superseded split-specific scripts
├── data/
│   ├── raw/                # Hindi-HDTB CoNLL-U, HDTB .dat (not all in git)
│   └── processed/
├── experiments/
│   ├── stanza/             # Stanza baseline + corrected CSVs (large; gitignored)
│   ├── udpipe/             # UDPipe baseline + corrected CSVs (large; gitignored)
│   └── rejected/           # DR1 experiment artifacts
├── outputs/
│   ├── alignment/          # UD–HDTB sentence alignment
│   ├── gold/               # gold_karaka_labels.csv
│   ├── metrics/            # Evaluation metric CSVs
│   └── error_analysis/     # Final error-analysis + paper tables
├── docs/
│   ├── final/              # Completion record (this archive lives here)
│   ├── paper/              # Paper outline and assets
│   ├── methodology/        # Scope, rules, mapping specs
│   ├── experiments/        # Verifier experiments, passive notes
│   └── archive/            # Historical handovers and checkpoints
└── notebooks/
    ├── exploration/        # Dataset and postposition analysis
    └── analysis/           # Verifier and pipeline pilots
```

### `src/paths.py`

Added during reorganization so scripts and pipeline runners import **one canonical path module** instead of hard-coded relative paths. It defines locations for `experiments/stanza/`, `experiments/udpipe/`, `outputs/metrics/`, `outputs/error_analysis/`, and helper functions such as `stanza_corrected_all(split)` and `udpipe_corrected_all(split)`. Reorganizations update paths in one place only.

### Import bootstrap

`scripts/_bootstrap.py` adds reorganized script subfolders to `sys.path` for cross-script imports.

---

## 3. Final Architecture

### End-to-end pipeline

```text
Sentence
  → Neural parser (Stanza or UDPipe)
  → UD token rows + case markers (from child case nodes)
  → Mapper v1          → mapper_candidates
  → Verifier v1        → final_candidates
  → Correction v2.1    → corrected_candidates
  → Karaka prediction / evaluation against gold
```

### Frozen components

| Layer | Module | Output column |
|-------|--------|---------------|
| Parser | `src/parser/stanza_parser.py` or `src/parser/udpipe_parser.py` | token rows, deprel, case_marker |
| Mapper v1 | `src/mapper/simple_mapper.py` | `mapper_candidates` |
| Verifier v1 | `src/verifier/simple_verifier.py` | `final_candidates` |
| Correction v2.1 | `src/pipeline/correction_layer_v2.py` | `corrected_candidates` |

**Mapper v1:** Conservative UD deprel → Karaka candidate mapping (neural-only baseline input to verifier).

**Verifier v1 rules (R1–R5):**

| Rule | Pattern | Karaka outcome | Decision type |
|------|---------|----------------|---------------|
| R1 | `nsubj` + `ने` | Karta | confirmed |
| R2 | `obl` + `में` | Adhikarana | confirmed |
| R3 | `obl` + `पर` | Adhikarana | confirmed |
| R4 | `obl` + `से` | Karana, Apadana | ambiguous |
| R5 | `obj`/`iobj` + `को` | Karma, Sampradana | ambiguous |

**Correction Layer v2.1 — H1 only (accepted):**

```python
# Rule ID: H1_NMOD_LOCATIVE_ADHIKARANA
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

**Diagnostic flags only (not auto-corrections):**

- `possible_passive_karta`
- `possible_passive_karma`
- `se_ambiguous_requires_verb_context`

### Evaluated systems

| System name | Column evaluated |
|-------------|------------------|
| Neural only | `mapper_candidates` |
| Verifier v1 | `final_candidates` |
| Correction v2.1 | `corrected_candidates` |

**Scoring modes:** candidate-set (secondary) and **strict** (primary — exactly one predicted label matching gold).

---

## 4. Datasets and Alignment

### Data sources

- **UD Hindi-HDTB:** CoNLL-U train/dev/test splits (`data/raw/hi_hdtb-ud-*.conllu`).
- **Original HDTB:** `.dat` annotation files for Paninian labels (news/heritage domain).

UD Hindi-HDTB alone does not contain Karaka gold labels. The project aligns UD sentences to HDTB and extracts a **restricted six-Karaka label set** for evaluation.

### Gold Karaka recovery

Pipeline: UD + HDTB alignment → token-level gold Karaka extraction → `outputs/gold/gold_karaka_labels.csv`.

Mapped labels include: **Karta, Karma, Karana, Sampradana, Apadana, Adhikarana** (many HDTB Paninian labels excluded — see methodology docs).

### Sentence alignment

- Normalization: Unicode NFC, nukta handling, punctuation cleanup, `NULL` token removal.
- Exact match plus high-confidence fuzzy alignment (`SequenceMatcher`).
- Artifacts: `outputs/alignment/aligned_ud_hdtb_sentences.csv`.

### Token matching protocol (evaluation)

Gold rows are joined to pipeline rows by:

```text
split + sent_id + normalized_token + occurrence_order
```

Implementation: `scripts/evaluation/evaluate_pipeline_against_gold.py` (`normalize_token`, deque-based occurrence indexing).

### Gold row counts

| Split | Gold Karaka rows |
|-------|-----------------:|
| Train | 47,378 |
| Dev | 5,902 |
| Test | 5,946 |

### Match quality (dev and test)

| Split | Matched | Unmatched | Match rate |
|-------|--------:|------------:|-----------:|
| Dev | 5,880 | 22 | 99.63% |
| Test | 5,924 | 22 | 99.63% |

Unmatched gold rows receive empty predictions and count as errors under strict scoring. Match rate is parser-independent (same 22 unmatched per split for Stanza and UDPipe).

---

## 5. Final Stanza Experiments

Primary evaluation branch: `experiments/stanza/`. Metrics: `outputs/metrics/{train,dev,test}_correction_v2_metrics.csv`.

### Overall metrics

| Split | System | Candidate acc. | Strict acc. |
|-------|--------|---------------:|------------:|
| Train | Neural only | 0.7865 | 0.5310 |
| Train | Verifier v1 | 0.7864 | 0.6259 |
| Train | Correction v2.1 | 0.8004 | **0.6400** |
| Dev | Neural only | 0.7369 | 0.4909 |
| Dev | Verifier v1 | 0.7403 | 0.5947 |
| Dev | Correction v2.1 | 0.7574 | **0.6118** |
| Test | Neural only | 0.7356 | 0.4850 |
| Test | Verifier v1 | 0.7373 | 0.5785 |
| Test | Correction v2.1 | 0.7568 | **0.5980** |

### Strict accuracy progression (held-out test)

| Stage | Strict accuracy |
|-------|----------------:|
| Neural only | 0.4850 |
| Verifier v1 | 0.5785 (+0.0935) |
| Correction v2.1 | 0.5980 (+0.0195 over verifier) |

Verifier v1 provides the **largest strict gain**; H1 adds a smaller but consistent increment localized to Adhikarana.

### H1 firing counts (Stanza)

| Split | H1 fires |
|-------|--------:|
| Train | 830 |
| Dev | 121 |
| Test | 130 |

### Adhikarana F1 gains (Stanza, Correction v2.1)

| Split | Candidate F1 | Strict F1 |
|-------|-------------:|----------:|
| Train | 0.9325 | 0.8265 |
| Dev | 0.9241 | 0.8335 |
| Test | 0.9239 | 0.8237 |

Test Adhikarana improvement from Verifier v1 → Correction v2.1: candidate F1 +0.0424, strict F1 +0.0524. H1 did not change F1 for other Karakas on test.

### DR1 rejected result

**Dependency Repair v1** tested relabeling `nmod + में/पर → obl` to unlock Verifier R2/R3 at the deprel layer.

| Metric (dev, vs gold UD deprel) | Value |
|----------------------------------|------:|
| Original deprel accuracy | 95.16% |
| After DR1 | 94.85% |
| Repairs | 121 |
| Improved | 5 |
| Worsened | 113 |

**DR1 was rejected.** Karaka-layer H1 was retained instead. See `docs/final/correction_layer_log.md` and `experiments/rejected/dependency_repair_v1/`.

---

## 6. UDPipe Robustness Experiment

### Purpose

**Parser robustness check after freeze** — verify whether the frozen symbolic stack transfers to a second Hindi UD parser without rule changes. **Not** system improvement or UDPipe-specific tuning.

### Package and model

- **Package:** `ufal.udpipe>=1.2.0` (`requirements.txt`)
- **Model:** `hindi-hdtb-ud-2.5-191206.udpipe` (cached under `models/udpipe/`, gitignored)

### Files added

| File | Role |
|------|------|
| `src/parser/udpipe_parser.py` | UDPipe wrapper (same token-row schema as Stanza) |
| `src/pipeline/run_udpipe_baseline.py` | Split-aware UDPipe baseline runner |
| `src/paths.py` (helpers) | `udpipe_baseline_all()`, `udpipe_corrected_all()`, etc. |
| `scripts/evaluation/* --parser udpipe` | Same correction/evaluation with parser flag |
| `scripts/analysis/audit_udpipe_token_matching.py` | Token alignment audit |

**No mapper, verifier, correction, or evaluation formulas were changed for UDPipe.**

### Token matching

| Split | Matched / total | Unmatched | Rate |
|-------|----------------:|----------:|-----:|
| Dev | 5,880 / 5,902 | 22 | 99.63% |
| Test | 5,924 / 5,946 | 22 | 99.63% |

Same unmatched rows as Stanza — alignment is parser-independent.

### Overall metrics (Correction v2.1)

| Split | Candidate acc. | Strict acc. |
|-------|---------------:|------------:|
| UDPipe dev | 0.7135 | 0.5701 |
| UDPipe test | 0.7153 | 0.5646 |

### Stanza vs UDPipe (Correction v2.1)

| Metric | Stanza dev | UDPipe dev | Stanza test | UDPipe test |
|--------|----------:|----------:|------------:|------------:|
| Candidate accuracy | 0.7574 | 0.7135 | 0.7568 | 0.7153 |
| Strict accuracy | 0.6118 | 0.5701 | 0.5980 | 0.5646 |
| Adhikarana strict F1 | 0.8335 | 0.8322 | 0.8237 | 0.8233 |
| Adhikarana candidate F1 | 0.9241 | 0.9157 | 0.9239 | 0.9116 |
| H1 firing count | 121 | 132 | 130 | 137 |

**Interpretation:** Overall strict accuracy is lower for UDPipe, but **Adhikarana / H1 behavior is stable across parsers**. The experiment supports cross-parser robustness claims, not a second tuned system.

Sources: `outputs/metrics/udpipe_*_correction_v2_metrics.csv`.

---

## 7. Final Error Analysis

### Script

`scripts/analysis/analyze_final_error_patterns.py`

- CLI: `--split {dev,test}` `--parser {stanza,udpipe}`
- Joins gold to corrected pipeline rows using the evaluation matching key.
- Classifies each gold row: `strict_correct`, `candidate_correct_strict_fail`, `candidate_wrong`, `no_prediction`, `unmatched_gold`.

### Key outputs (`outputs/error_analysis/`)

Per parser/split: `final_error_rows`, `failure_by_karaka`, `error_patterns`, `confusion_summary`, `karma_sampradana_cases`, `karana_apadana_cases`, `h1_success_rows`.

### Publication table

- `outputs/error_analysis/paper_error_analysis_table_v2.csv`
- `outputs/error_analysis/paper_error_analysis_table_v2.md`

Six-row compact summary with interpretations and likely future directions.

### Sanity check

`outputs/error_analysis/paper_error_analysis_sanity_check.md` — 20 sampled test cases validated the largest error bucket (unsupported UD dependency relations).

### Failure categories (test, merged patterns)

| Category | Stanza count | UDPipe count |
|----------|-------------:|-------------:|
| Unsupported UD dependency relations (`mark`, `compound`, `cc`, `root`) | 818 | 800 |
| Karma–Sampradana ambiguity with `को` | 480 | 450 |
| Karana–Apadana ambiguity with `से` | 171 | 166 |
| Residual Adhikarana ambiguity | 290 | 284 |
| Karta recall gaps | 278 | 373 |
| Gold–parser alignment limit | 22 | 22 |

### Main conclusion

Most remaining errors arise from **unsupported dependency relations** or **linguistically ambiguous markers** (`को`, `से`), not from missing postposition rules alone. **Future gains likely require richer semantic context** (verb class, recipient/beneficiary cues, locative/time expressions beyond `में`/`पर`) rather than only additional postposition-based rules.

Hard wrong-label cases are more frequent for UDPipe (303 vs 404 `candidate_wrong` on test) but are treated as parser noise, not a separate paper table row.

---

## 8. Rejected / Negative Results

### Passive diagnostics — rejected as auto-corrections

Flags `possible_passive_karta` and `possible_passive_karma` were investigated (`scripts/analysis/analyze_passive_diagnostics.py`, `docs/experiments/passive_example_manual_summary.md`). Manual review did not support safe automatic passive correction rules. Flags remain diagnostic only.

### DR1 dependency repair — rejected

Relabeling `nmod + में/पर → obl` **harmed gold-UD deprel accuracy** (95.16% → 94.85% on dev) despite linguistic similarity to H1 motivation. Demonstrates that **Karaka correction ≠ dependency label repair**.

### Why excluded from final system

- Risk of overcorrection on passive and `से` cases without verb-frame context.
- DR1 worsened UD labels while H1 improved Karaka F1 at the semantic layer.
- Final system intentionally contains **one conservative Karaka correction (H1)** only.

---

## 9. Final Scientific Contributions

1. **Neuro-symbolic Karaka extraction pipeline** over neural UD parses (Stanza primary), with frozen Mapper v1, Verifier v1, and Correction v2.1.
2. **Alignment-based gold Karaka evaluation setup** linking Hindi-HDTB UD to original HDTB annotations.
3. **Frozen symbolic verifier and correction layer** with explicit ambiguity handling and one validated H1 rule.
4. **Cross-parser evaluation** using Stanza and UDPipe under identical rules — H1 and Adhikarana F1 stable across parsers.
5. **Structured error analysis and limitations** — failure taxonomy, paper-ready table, sanity-checked categories.
6. **Negative result:** DR1 shows Karaka-oriented correction must not be conflated with UD dependency repair.

---

## 10. Final Limitations

- **Hindi only** — no cross-linguistic evaluation.
- **Six Karaka categories only** — many HDTB Paninian labels excluded.
- **Compact rule set** — Mapper v1 + five verifier rules + one correction rule; no learned reranker.
- **Karana and Apadana largely unresolved** under strict scoring (0.0000 strict F1 on test after Verifier v1).
- **Karma / Sampradana ambiguity** — `को` cases often multi-candidate; strict scoring penalizes legitimate ambiguity.
- **Not a full standalone Karaka analyzer** — operates on parser output, not raw text with full Paninian grammar.
- **Not directly comparable** to full rule-based Karaka systems on clean simple sentences without explaining task and input differences.
- **Alignment high quality but not perfect** — 99.63% token match; 22 unmatched gold rows per dev/test split.
- **No new languages yet** — UDPipe tests parser robustness within Hindi only.
- **Domain** — news/heritage HDTB; generalization beyond this domain not established.
- **Parser errors propagate** — symbolic layer cannot recover from all neural parse mistakes.

---

## 11. Paper Status

- An **IEEE / INDISCON-style draft** existed during the internship but was **not submitted**.
- **Current likely target:** SPELLL short paper / **Springer CCIS** format (venue TBD).
- **Paper still needs:**
  - Springer CCIS template conversion
  - Stronger related-work comparison (neuro-symbolic SRL, Hindi Karaka systems, UD-based role labeling)
  - Updated results section including UDPipe cross-parser robustness (Section 6 above)
  - Updated error analysis using `paper_error_analysis_table_v2`
  - Threats to validity (alignment, strict scoring, parser dependence, label subset)
  - Double-blind anonymization before submission

Outline: `docs/paper/paper_outline.md` (includes §6.1 Cross-Parser Robustness and expanded §7 Error Analysis).

---

## 12. Reproduction Commands

Run from repository root with project virtual environment active. Large pipeline CSVs are gitignored; baselines must exist under `experiments/` before evaluation (already generated for the frozen project — **do not rerun test baselines for paper claims without starting a new research phase**).

### Stanza test evaluation

```bash
python src/pipeline/run_stanza_baseline.py --split test
python scripts/evaluation/apply_correction_v2.py --split test
python scripts/evaluation/evaluate_correction_v2.py --split test
python scripts/evaluation/compare_correction_v2_per_karaka.py --split test
```

### UDPipe test evaluation

```bash
python src/pipeline/run_udpipe_baseline.py --split test
python scripts/analysis/audit_udpipe_token_matching.py --split test
python scripts/evaluation/apply_correction_v2.py --split test --parser udpipe
python scripts/evaluation/evaluate_correction_v2.py --split test --parser udpipe
python scripts/evaluation/compare_correction_v2_per_karaka.py --split test --parser udpipe
```

### Final error analysis (reporting only)

```bash
python scripts/analysis/analyze_final_error_patterns.py --split test --parser stanza
python scripts/analysis/analyze_final_error_patterns.py --split test --parser udpipe
```

Replace `test` with `dev` for development-split analysis. Metrics land in `outputs/metrics/`; error analysis in `outputs/error_analysis/`.

---

## 13. What Must Not Be Changed Without Starting a New Research Phase

1. **Do not add correction rules after held-out test evaluation** and still claim the same frozen Correction v2.1 system.
2. **Do not tune rules or thresholds based on test results** — test was run once after freeze.
3. **Do not modify H1** (or add H2, H3, …) and report numbers as the same frozen system without a new evaluation protocol and a new held-out policy.
4. **Do not compare numerically with unrelated Karaka analyzers** without explaining differences in input (raw text vs UD parses), label inventory, and scoring.
5. **Do not claim dependency parsing improvement** — the project evaluates Karaka extraction; DR1 showed deprel repair can harm UD accuracy.
6. **Do not regenerate Stanza test baselines** for primary paper claims unless documenting a deliberate new research phase.
7. **Do not conflate UDPipe robustness results with a second tuned system** — UDPipe uses identical symbolic rules by design.

---

## Document Index (quick navigation)

| Section | Topic |
|---------|-------|
| 1 | Project identity and framing |
| 2 | Repository structure |
| 3 | Frozen architecture (Mapper, Verifier R1–R5, H1) |
| 4 | Datasets, alignment, matching |
| 5 | Stanza train/dev/test results |
| 6 | UDPipe robustness experiment |
| 7 | Final error analysis |
| 8 | Rejected / negative results |
| 9 | Scientific contributions |
| 10 | Limitations |
| 11 | Paper status |
| 12 | Reproduction commands |
| 13 | Research-phase boundaries |

*End of Project Archive v1*
