# Paper Implementation Audit

**Paper:** Neuro-Symbolic Kāraka Extraction for Hindi from Neural Dependency Parses  
**Audit date:** 2026-06-20  
**Scope:** Reproducibility and consistency audit of the conference paper against repository code, CSV outputs, and scripts. No code was modified during this audit.

**Sources checked:**
- Paper PDF: `Neurosymbolic_Karaka_Extraction (1).pdf`
- References: `references (3).bib`
- Repository outputs under `output/` and `results/`
- Core scripts under `scripts/` and `src/`

---

## A. Executive Summary

### Safe claims (fully supported)

- Final framing is **Karaka extraction over neural parses**, not UD dependency parsing improvement.
- Frozen pipeline: Stanza → Mapper v1 → Verifier v1 → Correction v2.1 (H1 only).
- Test strict accuracy **0.4850 → 0.5980** (+11.30 percentage points vs neural-only).
- Verifier strict gain on test: **+9.35** percentage points (0.5785 − 0.4850).
- Correction strict gain over verifier on test: **+1.95** percentage points (0.5980 − 0.5785).
- Test evaluation denominator is **5946 gold rows**; **22 unmatched rows are counted as incorrect**, not excluded.
- Table I dataset / alignment sentence counts match generated alignment artifacts.
- Gold Karaka mapping (`k1`…`k7p`) matches `scripts/extract_gold_karaka_labels.py`.
- Verifier rules R1–R5 match `src/verifier/simple_verifier.py`, including **R5 on both obj and iobj + को**.
- H1 is the only rule that modifies `corrected_candidates` in Correction v2.1.
- H1 firing counts: train **830**, dev **121**, test **130**.
- DR1 negative result on dev: **95.16% → 94.85%**, 121 repairs, 5 improved, 113 worsened.
- DR1 is **not** part of the final evaluated Karaka system.
- Dev error analysis counts: **1553** neural-only errors, **524** actionable, pattern **Adhikarana | nmod | में = 80** (dev only).
- Test per-Karaka strict F1 table (Table V) matches `output/test_correction_v2_metrics.csv`.
- Adhikarana verifier→correction gains: candidate F1 **+0.0424**, strict F1 **+0.0524**.
- Paper Table IV "Cand. F1" corresponds to **macro F1** in code (`macro_f1` column), not per-class F1.
- Stanza [15], HDTB [8][9], UD conversion [10], Paninian/Karaka literature [2][3][4], and neuro-symbolic motivation [5][6] are cited appropriately.

### Claims needing correction or clarification

1. **Section IV.B:** Strict evaluation is described as measuring "precision." It measures **strict accuracy** (exact single-label match rate over all gold rows).
2. **Section V.B:** Karma discussion says "strict accuracy" but Table V reports **strict F1** (0.6736 → 0.5104). Use consistent metric names.
3. **Section V.B:** Kartā improvement attributed mainly to "mapper baseline." Table V shows **no change across all three systems** (0.8790). Stanza+mapper+verifier already agree; do not imply mapper alone explains test Kartā performance.
4. **Section III.C / Table III:** Rules are described as "designed by analysing … UD Hindi-HDTB" plus Paninian analysis. This is mostly true, but should not be read as "taken directly from literature." Primary evidence is **train/dev postposition statistics** (`notebooks/02_postposition_analysis.ipynb`).
5. **PDF formatting:** Abstract/Introduction contains corrupted token `texthindi____` where **में** should appear (line ~83 in extracted PDF text).
6. **Label spelling inconsistency:** Paper tables use **Kartā / Adhikaraṇa** with diacritics; gold CSV and evaluation use **Karta / Adhikarana**. Evaluation normalizes via `LABEL_NORMALIZATION` in `evaluate_pipeline_against_gold.py`, so metrics are consistent, but paper/code spelling should be noted.
7. **Missing reporting:** Paper Table I gives sentence counts but not **gold Karaka row counts** (47378 / 5902 / 5946), which are central to evaluation.
8. **Error analysis completeness:** Paper reports **nmod + में = 80** but not **nmod + पर = 21** on dev actionable errors (same analysis file).

### Unresolved / not fully re-audited in this pass

- **Train token matching counts** were not recorded in `output/train_correction_v2_metrics.csv` (older CSV schema without `matched_gold_rows`). Train denominator is verified as **47378**, but train matched/unmatched breakdown was not exported.
- **Full recomputation from scratch** of all metrics by rerunning scripts was not performed (per user instruction: audit only). All metrics were verified against existing CSV outputs and arithmetic checks.
- **Paper PDF page references** are approximate from text extraction; line numbers in LaTeX source were not available.

---

## B. Verified Numbers Table

| Number | Claim / use | Source file / script | Status |
|--------|-------------|----------------------|--------|
| 13306 | UD train sentences | `data/raw/hi_hdtb-ud-train.conllu` (`# sent_id` count) | **Verified** |
| 1659 | UD dev sentences | `data/raw/hi_hdtb-ud-dev.conllu` | **Verified** |
| 1684 | UD test sentences | `data/raw/hi_hdtb-ud-test.conllu` | **Verified** |
| 14089 | Original HDTB train sentences | `data/raw/news_articles_and_heritage/Training/*.dat` (blank-line sentence count) | **Verified** |
| 1743 | Original HDTB dev sentences | `.../Development/*.dat` | **Verified** |
| 1804 | Original HDTB test sentences | `.../Testing/*.dat` | **Verified** |
| 13302 | Aligned train sentences | `output/aligned_ud_hdtb_sentences.csv` (`ud_split=train`) | **Verified** |
| 1659 | Aligned dev sentences | same file (`ud_split=dev`) | **Verified** |
| 1684 | Aligned test sentences | same file (`ud_split=test`) | **Verified** |
| 47378 | Gold Karaka train rows | `output/gold_karaka_labels.csv` | **Verified** |
| 5902 | Gold Karaka dev rows | same | **Verified** |
| 5946 | Gold Karaka test rows | same | **Verified** |
| 5924 | Test matched gold rows | `output/test_correction_v2_metrics.csv` (`matched_gold_rows`) | **Verified** |
| 22 | Test unmatched gold rows | same (`unmatched_gold_rows`) | **Verified** |
| 99.63% | Test match rate | 5924/5946 = 0.996299… | **Verified** |
| 5946 | Test evaluation denominator | `support` column in overall rows | **Verified** |
| 1553 | Dev neural-only errors | `output/dev_neural_only_errors.csv` (row count) | **Verified** |
| 524 | Dev actionable errors | `output/dev_actionable_neural_errors.csv` (row count) | **Verified** |
| 80 | Adhikarana \| nmod \| में (dev) | `output/dev_actionable_neural_errors.csv` (pattern count) | **Verified** |
| 21 | Adhikarana \| nmod \| पर (dev) | same (not reported in paper) | **Verified, omitted in paper** |
| 830 / 121 / 130 | H1 fires train/dev/test | `results/stanza_{split}_corrected_v2_all.csv` | **Verified** |
| 95.16% | DR1 original deprel accuracy | `output/dependency_repair_v1_dev_eval.csv` | **Verified** |
| 94.85% | DR1 repaired deprel accuracy | same | **Verified** |
| 121 / 5 / 113 | DR1 repair outcomes | same | **Verified** |
| 0.7356 / 0.5621 / 0.4850 / 0.3876 | Test neural-only metrics | `output/test_correction_v2_metrics.csv` | **Verified** |
| 0.7373 / 0.5716 / 0.5785 / 0.4220 | Test verifier metrics | same | **Verified** |
| 0.7568 / 0.5786 / 0.5980 / 0.4308 | Test correction metrics | same | **Verified** |
| 0.7865 / 0.6023 / 0.5310 / 0.4234 | Train neural-only | `output/train_correction_v2_metrics.csv` | **Verified** |
| 0.7864 / 0.6023 / 0.6259 / 0.4451 | Train verifier | same | **Verified** |
| 0.8004 / 0.6073 / 0.6400 / 0.4513 | Train correction | same | **Verified** |
| 0.7369 / 0.5599 / 0.4909 / 0.3877 | Dev neural-only | `output/dev_correction_v2_metrics.csv` | **Verified** |
| 0.7403 / 0.5724 / 0.5947 / 0.4153 | Dev verifier | same | **Verified** |
| 0.7574 / 0.5784 / 0.6118 / 0.4226 | Dev correction | same | **Verified** |
| +0.1130 | Test strict acc. gain (corr vs neural) | 0.5980 − 0.4850 | **Verified** |
| +0.0935 | Test strict acc. gain (verifier vs neural) | 0.5785 − 0.4850 | **Verified** |
| +0.0195 | Test strict acc. gain (corr vs verifier) | 0.5980 − 0.5785 | **Verified** |
| +0.0212 | Test candidate acc. gain (corr vs neural) | 0.7568 − 0.7356 | **Verified** |
| +0.0424 | Adhikarana candidate F1 (verifier→corr, test) | `output/test_correction_v2_per_karaka_comparison.csv` | **Verified** |
| +0.0524 | Adhikarana strict F1 (verifier→corr, test) | same | **Verified** |
| +0.0894 | Adhikarana candidate F1 (neural→corr, test) | same (`delta_correction_v2_1_minus_neural_only`) | **Verified, not in current PDF** |
| +0.8237 | Adhikarana strict F1 (neural→corr, test) | 0.8237 − 0.0000 | **Verified, not in current PDF** |

---

## C. Rule Verification Table

| Component | Paper claim | Code behavior | Status |
|-----------|-------------|---------------|--------|
| **Mapper v1** | nsubj→Kartā, obj→Karma, iobj→Sampradāna, obl→Adhikaraṇa/Karaṇa/Apādāna | `simple_mapper.py`: exact mappings; uses **Kartā**, **Adhikaraṇa**, **Karaṇa**, **Apādāna** spellings | **Verified** (diacritic spelling in code) |
| **Mapper v1** | root/case not Karaka labels | `root` → no_karaka; `case` → evidence_only | **Verified** |
| **Neural only baseline** | mapper_candidates | `evaluate_correction_v2.py` uses column `mapper_candidates` for `neural_only` | **Verified** |
| **R1** | nsubj + ने → Kartā | `simple_verifier.py` lines 57–65 | **Verified** |
| **R2** | obl + में → Adhikaraṇa | lines 67–75 | **Verified** |
| **R3** | obl + पर → Adhikaraṇa | lines 77–85 | **Verified** |
| **R4** | obl + से → Karaṇa / Apādāna | lines 87–95, ambiguous | **Verified** |
| **R5** | obj/iobj + को → Karma / Sampradāna | lines 97–105, `deprel in ("obj", "iobj")` | **Verified** |
| **Verifier merge** | Verifier overrides mapper when confirmed/ambiguous | `combine_results()` in `run_gold_ud_pipeline.py` | **Verified** |
| **No hidden verifier rules** | Only R1–R5 | Full file review of `simple_verifier.py` | **Verified** |
| **H1** | nmod + में/पर → Adhikarana | `correction_layer_v2.py`: only changes `corrected_candidates` when condition holds | **Verified** |
| **H1 only correction** | Single accepted rule | `apply_correction_v2.py` validates only `H1_NMOD_LOCATIVE_ADHIKARANA` may change output | **Verified** |
| **Passive diagnostics** | Do not modify predictions | `diagnostic_flag()` only sets flag column | **Verified** |
| **DR1** | nmod + में/पर → obl | `dependency_repair_v1.py`; separate from final Karaka pipeline | **Verified, rejected** |
| **Final system excludes DR1** | No dep repair in correction outputs | Test evaluation uses `corrected_candidates` from correction layer only | **Verified** |

---

## D. Metrics Verification Table

### Test (held-out)

| System | Metric | Paper (Table IV) | CSV value | Recomputed | Status |
|--------|--------|------------------|-----------|------------|--------|
| Neural | Cand. Acc. | 0.7356 | 0.7356 | 4374/5946=0.7356 | **Verified** |
| Neural | Cand. F1 (macro) | 0.5621 | 0.5621 | — | **Verified** |
| Neural | Strict Acc. | 0.4850 | 0.4850 | 2884/5946=0.4850 | **Verified** |
| Neural | Strict F1 (macro) | 0.3876 | 0.3876 | — | **Verified** |
| Verifier | Strict Acc. | 0.5785 | 0.5785 | 3440/5946=0.5785 | **Verified** |
| Correction | Strict Acc. | 0.5980 | 0.5980 | 3556/5946=0.5980 | **Verified** |

**Denominator check:** All overall rows have `support=5946`, `matched_gold_rows=5924`, `unmatched_gold_rows=22`. Unmatched rows contribute to denominator with empty predictions → incorrect.

### Train / Dev

All train and dev overall metrics in Section 2 of this audit match `output/train_correction_v2_metrics.csv` and `output/dev_correction_v2_metrics.csv` exactly (4 decimal places).

**Note:** Train CSV labels system as `correction_v2` (not `correction_v2.1`) and lacks matched/unmatched columns. Numeric values still match documented final train/dev results.

### Per-Karaka strict F1 (Test, Table V)

All six Karakas match `output/test_correction_v2_metrics.csv` strict per_karaka rows exactly.

**Important nuance:** Under strict scoring, **Neural Karma strict F1 = 0.6736** is correct per script definition (F1 computed with strict single-label predictions only). This is **not** the same as overall strict accuracy. Paper Section V.B should not call this "strict accuracy."

---

## E. Paper Issue List

| Location | Current wording / issue | Problem | Suggested correction |
|----------|-------------------------|---------|-------------------|
| Abstract / Intro (~line 83) | `texthindi____` corruption | Hindi postposition में not rendered | Fix LaTeX/text encoding for में |
| Section IV.B | "Strict evaluation… measuring the system's **precision**" | Strict mode measures **accuracy** (correct/total gold rows with exact single label) | Replace "precision" with "strict accuracy" or "exact-match accuracy" |
| Section IV.B | Evaluation protocol (lines 330–334) | **Correct in current PDF** | Keep: N=5946, unmatched counted incorrect |
| Section V.B | "slight decrease in **strict accuracy**" for Karma | Table V is **strict F1**, not accuracy | Say "strict F1 fell from 0.6736 to 0.5104" |
| Section V.B | Kartā "mapper baseline performs strongly" | All three systems identical at 0.8790 strict F1 | Say "Kartā strict F1 remained unchanged at 0.8790 across all systems" |
| Section V.B | Adhikarana gains | **Correct in current PDF** (+0.0524 strict, +0.0424 candidate, verifier→correction) | No +0.0894 in current PDF (good) |
| Section V.C | Only mentions nmod+में=80 | Dev also has nmod+पर=21 for same gold Karaka | Optionally add "and 21 cases with पर" or keep में as primary pattern |
| Section III.C | Rules "designed by analysing … UD Hindi-HDTB … along with Paninian … analysis" | Rules are **dataset-statistics motivated** with Paninian inspiration, not literature-only | Say "motivated by postposition statistics on Hindi-HDTB train/dev and Paninian linguistic expectations" |
| Section IV.A | "dev was used for … iterative system refining" | True but risks implying test leakage | Add explicit sentence: "Test was not used during rule design; H1 was validated on train/dev only before one frozen test run." |
| Table I | Sentence counts only | Gold row counts absent | Add row or separate table: gold Karaka rows 47378/5902/5946 |
| Table II | Kartā, Adhikaraṇa with diacritics | Gold CSV uses Karta, Adhikarana | Add footnote: evaluation normalizes label variants |
| Table IV header | "Cand. F1" | Column is **macro F1** over Karakas | Rename to "Cand. Macro F1" for precision |
| Throughout | Diacritics vs ASCII labels | Pipeline outputs Kartā; gold uses Karta | Harmless for metrics due to normalization; be consistent in paper text |

### Claims checked and NOT found in current PDF

| Potentially problematic claim | Status in PDF |
|------------------------------|---------------|
| "improves dependency parsing" as main claim | **Not found** (framing is Karaka extraction) |
| "proves" | **Not found** |
| "all unmatched rows were excluded" | **Not found** (protocol correctly states inclusion) |
| "+0.0894" Adhikarana strict gain | **Not found** in current PDF |
| "neural parser takes care of Karta" | **Not found verbatim** (weaker "mapper performs strongly" issue remains) |

---

## F. Final Safe Claims for Paper

Use these formulations with high confidence:

1. We evaluate **Karaka extraction from Stanza UD parses**, not UD parsing accuracy improvement.
2. Gold Karaka labels come from **aligned original HDTB** with mapping k1→Karta, k2→Karma, k3→Karana, k4→Sampradana, k5→Apadana, k7/k7p→Adhikarana.
3. Sentence alignment coverage matches Table I (13302/1659/1684 aligned sentences).
4. Evaluation uses **5946 test gold Karaka rows**; **5924 matched** to pipeline tokens; **22 unmatched** rows receive empty predictions and count as incorrect.
5. **Strict accuracy** (primary metric) on test improves from **48.50%** (neural-only) to **57.85%** (verifier) to **59.80%** (correction v2.1).
6. Verifier contributes most strict gain (**+9.35** pp); H1 correction adds **+1.95** pp over verifier on test strict accuracy.
7. H1 (`nmod + में/पर → Adhikarana`) is the **only accepted automatic correction rule**; it fired **130 times** on test.
8. H1 improves **Adhikarana only** on test: strict F1 **0.7713 → 0.8237** (+0.0524); candidate F1 **0.8815 → 0.9239** (+0.0424); other Karakas unchanged from verifier to correction.
9. Dev error analysis (not test): **1553** neural errors, **524** actionable, top locative pattern **Adhikarana | nmod | में = 80**.
10. DR1 dependency repair on dev **reduced** gold UD deprel accuracy **95.16% → 94.85%** (121 repairs; 113 worsened); DR1 is **rejected** and excluded from the final Karaka system.
11. Passive correction rules were **investigated but not accepted**.
12. "Cand. F1" in tables should be labeled **candidate macro F1** to match implementation.

---

## G. Unresolved Questions

1. **Train/dev token matching audit for paper:** Dev (5880/5902) and test (5924/5946) are documented; train matched/unmatched counts were not exported in metrics CSV. If the paper needs train matching statistics, rerun `audit_dev_token_matching.py` generalized for train or add to evaluation script output.

2. **Stale output risk:** `output/train_correction_v2_metrics.csv` uses system name `correction_v2` and omits match-count columns, suggesting an older evaluator variant. Numbers match final documentation, but schema differs from dev/test files.

3. **Label harmonization transparency:** Paper does not mention that pipeline outputs use diacritic variants (Kartā) normalized to gold labels (Karta) at evaluation time via `LABEL_NORMALIZATION` in `evaluate_pipeline_against_gold.py`.

4. **Verifier rule firing counts:** No consolidated CSV of R1–R5 fire counts on test was found in `output/`. Paper does not claim these counts; add only if computed from baseline CSVs.

5. **Original HDTB file inventory:** Sentence counts verified by summing `.dat` files under Training/Development/Testing folders; paper does not need file-level listing but replication should reference `data/raw/news_articles_and_heritage/`.

6. **LaTeX source not audited:** This audit used PDF text extraction. Corrupted `texthindi` fragment should be fixed in source, not only checked in PDF.

---

## Appendix: Evaluation Protocol (Implementation Truth)

For paper Methods section, the implementation truth is:

```text
gold_rows = all rows in gold_karaka_labels.csv for split with non-empty gold_karaka
for each gold_row:
    pipeline_row = match(split, sent_id, normalized_token, occurrence_order) or None
    candidates = parse_candidates(pipeline_row[system_column]) if pipeline_row else {}
    candidate_set correct if gold in candidates
    strict correct if len(candidates)==1 and gold in candidates
overall accuracy = correct / len(gold_rows)   # denominator includes unmatched
```

**Therefore:** denominator = **5946** on test, **not** 5924.

---

## Appendix: Citation Audit

| Topic | Cited in paper? | Bib entry present? | Notes |
|-------|-----------------|-------------------|-------|
| Stanza parser | Yes [15] | Yes (`qi_stanza_2020`) | Required and present |
| HDTB project | Yes [8][9] | Yes | Required and present |
| UD Hindi-HDTB conversion | Yes [10] | Yes (`tandon_conversion_2016`) | Required and present |
| Paninian / Karaka theory | Yes [2][3] | Yes | Required and present |
| Rule-based Karaka analyzer | Yes [4] | Yes (`katyayan_development_2022`) | Required and present |
| Neuro-symbolic NLP | Yes [5][6] | Yes | Required and present |
| UAS/LAS parsing eval context | Yes [11] | Yes | Used as contrast, not as project metric |

**Do not cite as prior work (project contributions):**
- UD–HDTB sentence alignment pipeline for this project
- Gold Karaka recovery for evaluation subset
- Mapper/Verifier/Correction v2.1 architecture as implemented here
- H1 rule discovery and validation
- DR1 negative result
- Final train/dev/test Karaka metrics
- Token matching protocol with occurrence order

**Bib file note:** `references (3).bib` contains many entries not used in the 15-reference paper (e.g., Ghosh, Fantechi, Das). Unused entries are fine but should not be cited unless referenced in text.

---

## Appendix: Key File Index for Reproduction

| Task | Script / file |
|------|---------------|
| Sentence alignment | `scripts/build_aligned_hdtb_ud.py` → `output/aligned_ud_hdtb_sentences.csv` |
| Gold Karaka extraction | `scripts/extract_gold_karaka_labels.py` → `output/gold_karaka_labels.csv` |
| Stanza baseline | `src/pipeline/run_stanza_baseline.py --split {train,dev,test}` |
| Apply H1 correction | `scripts/apply_correction_v2.py --split {split}` |
| Final metrics | `scripts/evaluate_correction_v2.py --split {split}` |
| Per-Karaka comparison | `scripts/compare_correction_v2_per_karaka.py --split {split}` |
| Dev error mining | `scripts/analyze_dev_neural_errors.py`, `scripts/analyze_dev_actionable_errors.py` |
| DR1 evaluation | `scripts/evaluate_dependency_repair_v1_dev.py` → `output/dependency_repair_v1_dev_eval.csv` |

**Do not rerun test** for paper submission unless intentionally reproducing frozen evaluation from scratch.
