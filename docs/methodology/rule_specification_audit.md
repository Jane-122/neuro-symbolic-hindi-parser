# Rule Specification v1 — Statistical Audit Report

**Audited document:** `docs/methodology/rule_specification_v1.md`  
**Evidence source:** `notebooks/exploration/02_postposition_analysis.ipynb`  
**Dataset:** `data/raw/hi_hdtb-ud-train.conllu`  
**Audit date:** June 8, 2026  
**Rule logic:** Not modified (audit only)

---

## Audit Method

For each percentage cited in `rule_specification_v1.md`, this audit:

1. Traced the computation pipeline in notebook 02.
2. Re-ran the same logic independently against `hi_hdtb-ud-train.conllu`.
3. Marked each figure **verified**, **derived** (computed from verified components but not printed directly in the notebook), or **unverified** (no traced computation).

### Shared computation pipeline (all rules)

| Step | What is computed | Notebook location |
|------|------------------|-------------------|
| 1 | Load CONLL-U sentences from training file | **Cell 3** (code) — `load_conllu("../data/raw/hi_hdtb-ud-train.conllu")` |
| 2 | Build `(postposition_form, parent_deprel)` records for every token with `deprel = case` | **Cell 5** (code) — `extract_case_records()` |
| 3 | Group records by postposition form | **Cell 11** (code) — `parent_labels_by_postposition` |
| 4 | Count parent labels per postposition; compute percent | **Cell 11** — `show_parent_label_distribution()` using `percent = 100 * count / total` |

**Percent formula (all rules):**

```
percent = 100 × count(parent_deprel = X for postposition P) / total_tokens(case form = P)
```

Where:
- **Numerator:** number of `case` tokens with `form = P` whose head token has `deprel = X`
- **Denominator:** total number of `case` tokens with `form = P`

**Corpus totals (Cell 5 output):** 53,121 case tokens; 139 unique postposition forms; 13,306 sentences.

---

## Rule-by-Rule Audit

### R1 — `nsubj` + `ने` → Kartā

| Claim in rule spec | Value | Status | Evidence cells |
|--------------------|------:|--------|----------------|
| `ने` attaches to `nsubj` parents | **98.4%** | **Verified** | Cell 11 (ने block), Cell 13, Cell 15 |
| Strongest postposition–label association | qualitative | **Verified** | Independent recomputation: `ने`+`nsubj` = 98.4% is the highest top-parent rate among postpositions with ≥100 tokens in the training set |

**Exact computation:**

```
count = 4785   (case=ने tokens whose head has deprel=nsubj)
total = 4862   (all case=ने tokens)
percent = 100 × 4785 / 4862 = 98.4163% → rounds to 98.4%
```

**Notebook cells that produced the evidence:**
- **Cell 11** — `show_parent_label_distribution("ने")` prints `nsubj 4785 98.4%`
- **Cell 13** — `summarize_focus_postposition("ने")` repeats full distribution
- **Cell 15** — summary row: `ने 4862 nsubj 98.4%`

**Non-statistical claims (unverified by computation):**
- "Ergative/agent marking" — linguistic interpretation, not a counted metric
- "reliable evidence for Kartā" — research judgment, not statistically tested against gold Karaka labels

---

### R2 — `obl` + `में` → Adhikaraṇa

| Claim in rule spec | Value | Status | Evidence cells |
|--------------------|------:|--------|----------------|
| `में` attaches to `obl` parents | **87.6%** | **Verified** | Cell 11 (में block), Cell 13, Cell 15 |
| `में` on `nmod` parents (fallback note) | **9.5%** | **Verified** | Cell 11 (में block), Cell 13 |

**Exact computation (primary statistic):**

```
count = 7108   (case=में, head deprel=obl)
total = 8115   (all case=में tokens)
percent = 100 × 7108 / 8115 = 87.5909% → rounds to 87.6%
```

**Exact computation (fallback statistic):**

```
count = 769    (case=में, head deprel=nmod)
total = 8115
percent = 100 × 769 / 8115 = 9.4763% → rounds to 9.5%
```

**Notebook cells:** Cell 11, Cell 13, Cell 15 (`में … obl 87.6%`)

**Non-statistical claims (unverified):**
- "Locative and locus readings" — linguistic interpretation
- "location/container Adhikaraṇa candidates" — Karaka assignment hypothesis, no gold Karaka evaluation

---

### R3 — `obl` + `पर` → Adhikaraṇa

| Claim in rule spec | Value | Status | Evidence cells |
|--------------------|------:|--------|----------------|
| `पर` attaches to `obl` parents | **89.8%** | **Verified** | Cell 11 (पर block), Cell 13, Cell 15 |
| `पर` on `nmod` parents (fallback note) | **6.4%** | **Verified** | Cell 11 (पर block), Cell 13 |

**Exact computation (primary statistic):**

```
count = 2654   (case=पर, head deprel=obl)
total = 2956   (all case=पर tokens)
percent = 100 × 2654 / 2956 = 89.7835% → rounds to 89.8%
```

**Exact computation (fallback statistic):**

```
count = 190    (case=पर, head deprel=nmod)
total = 2956
percent = 100 × 190 / 2956 = 6.4276% → rounds to 6.4%
```

**Notebook cells:** Cell 11, Cell 13, Cell 15 (`पर … obl 89.8%`)

**Non-statistical claims (unverified):**
- "Surface/location readings (on, upon)" — linguistic interpretation

---

### R4 — `obl` + `से` → Karaṇa or Apādāna (ambiguous)

| Claim in rule spec | Value | Status | Evidence cells |
|--------------------|------:|--------|----------------|
| `से` attaches to `obl` parents | **69.5%** | **Verified** | Cell 11 (से block), Cell 13, Cell 15 |
| `से` on `obj` parents (fallback note) | **9.4%** | **Verified** | Cell 11 (से block), Cell 13 |
| `से` on `iobj` parents (fallback note) | **6.3%** | **Verified** | Cell 11 (से block), Cell 13 |
| `से` on `obj`/`iobj` parents combined | **~15.7%** | **Derived (verified)** | Not printed as a single row; sum of Cell 11/13 components |

**Exact computation (primary statistic):**

```
count = 3006   (case=से, head deprel=obl)
total = 4324   (all case=से tokens)
percent = 100 × 3006 / 4324 = 69.5190% → rounds to 69.5%
```

**Exact computation (combined fallback):**

```
obj count  = 408  → 100 × 408 / 4324 = 9.4366% → 9.4%
iobj count = 273  → 100 × 273 / 4324 = 6.3136% → 6.3%
combined   = 681  → 100 × 681 / 4324 = 15.7493% → 15.7%
```

**Note on ~15.7%:** The rule spec reports a **combined** `obj`+`iobj` percentage. The notebook prints the two components separately (Cell 11, Cell 13) but never prints the combined 15.7% line. The value is **arithmetically correct** and traceable to those cells.

**Notebook cells:** Cell 11, Cell 13, Cell 15 (`से … obl 69.5%`)

**Non-statistical claims (unverified):**
- "से can mark instrument (Karaṇa) or source/separation (Apādāna)" — Paninian linguistic claim; no Karaṇa/Apādāna gold-standard counts in the repository

---

### R5 — `obj`/`iobj` + `को` → Karma or Sampradāna (ambiguous)

| Claim in rule spec | Value | Status | Evidence cells |
|--------------------|------:|--------|----------------|
| `को` on `obj` parents | **45.2%** | **Verified** | Cell 11 (को block), Cell 13, Cell 15 |
| `को` on `iobj` parents | **24.0%** | **Verified** | Cell 11, Cell 13 |
| `को` on `obl` parents | **17.6%** | **Verified** | Cell 11, Cell 13 |
| `को` on `nsubj` parents | **9.7%** | **Verified** | Cell 11, Cell 13 |

**Exact computation:**

```
total = 5799   (all case=को tokens)

obj:   2624 → 100 × 2624 / 5799 = 45.2492% → 45.2%
iobj:  1389 → 100 × 1389 / 5799 = 23.9524% → 24.0%
obl:   1021 → 100 × 1021 / 5799 = 17.6065% → 17.6%
nsubj:  560 → 100 × 560  / 5799 =  9.6568% →  9.7%
```

**Notebook cells:** Cell 11, Cell 13, Cell 15 (`को … obj 45.2%`)

**Non-statistical claims (unverified):**
- "को signals dative/accusative marking" — linguistic interpretation
- Karma vs Sampradāna disambiguation need — research judgment; no Karaka-labeled evaluation set exists

---

## Summary Table

| Rule | Cited % | Recomputed | Match? | Primary evidence cell(s) |
|------|--------:|-----------:|:------:|--------------------------|
| R1 | 98.4% (`ने`+`nsubj`) | 98.4163% | Yes | Cell 11, 13, 15 |
| R2 | 87.6% (`में`+`obl`) | 87.5909% | Yes | Cell 11, 13, 15 |
| R2 fallback | 9.5% (`में`+`nmod`) | 9.4763% | Yes | Cell 11, 13 |
| R3 | 89.8% (`पर`+`obl`) | 89.7835% | Yes | Cell 11, 13, 15 |
| R3 fallback | 6.4% (`पर`+`nmod`) | 6.4276% | Yes | Cell 11, 13 |
| R4 | 69.5% (`से`+`obl`) | 69.5190% | Yes | Cell 11, 13, 15 |
| R4 fallback | ~15.7% (`से`+`obj`/`iobj`) | 15.7493% | Yes (derived) | Cell 11, 13 (components) |
| R5 | 45.2% (`को`+`obj`) | 45.2492% | Yes | Cell 11, 13, 15 |
| R5 | 24.0% (`को`+`iobj`) | 23.9524% | Yes | Cell 11, 13 |
| R5 | 17.6% (`को`+`obl`) | 17.6065% | Yes | Cell 11, 13 |
| R5 | 9.7% (`को`+`nsubj`) | 9.6568% | Yes | Cell 11, 13 |

**Result:** All numeric percentages in `rule_specification_v1.md` are **verified** against the training set. None are marked unverified.

---

## Claims Without Statistical Trace

The following statements in `rule_specification_v1.md` are **not percentages** and cannot be verified by the notebook pipeline. They are linguistic or design judgments:

| Claim | Location | Status |
|-------|----------|--------|
| "Strongest postposition–label association found so far" | R1 reasoning | **Verified qualitatively** — `ने`+`nsubj` at 98.4% exceeds all other focus-postposition top-parent rates (next highest: `में`+`obl` 87.6%) |
| Ergative/agent reading of `ने` | R1 reasoning | **Unverified** — no Karaka gold standard |
| Locative/locus readings of `में` | R2 reasoning | **Unverified** — syntactic co-occurrence only |
| Surface/location readings of `पर` | R3 reasoning | **Unverified** |
| Karaṇa vs Apādāna for `से` | R4 reasoning | **Unverified** |
| Karma vs Sampradāna for `को` | R5 reasoning | **Unverified** |
| Mapping hypothesis confidences in "Expected Verifier Behaviour" table | Illustrative section | **Unverified here** — sourced from `ud_to_karaka_mapping_v1.md`, not from notebook 02 |

---

## Coverage Gaps

| Gap | Impact |
|-----|--------|
| Statistics are **training-set only** | Dev/test splits (`hi_hdtb-ud-dev.conllu`, `hi_hdtb-ud-test.conllu`) not audited |
| No gold Karaka annotations | Percentages measure UD syntax co-occurrence, not Karaka correctness |
| R4 combined 15.7% not printed in notebook | Correct but **derived**; future notebooks should print combined rates explicitly |
| Cell 11 truncates `पर` output in saved notebook | Full stats still in Cell 13; recomputation confirms 89.8% and 6.4% |

---

## Conclusion

All **numeric percentages** cited in `docs/methodology/rule_specification_v1.md` are **correct** and traceable to `notebooks/exploration/02_postposition_analysis.ipynb` (Cells 5, 11, 13, 15) with denominator = all `case` tokens of that postposition form in `hi_hdtb-ud-train.conllu`.

**No percentage requires correction.** Rule logic was not modified per audit instructions.

**Linguistic and Karaka-role claims** remain hypotheses — supported by syntactic co-occurrence patterns but not validated against Paninian gold annotations.

---

## References

- Rule specification: `docs/methodology/rule_specification_v1.md`
- Postposition analysis: `notebooks/exploration/02_postposition_analysis.ipynb`
- Mapping hypotheses: `docs/methodology/ud_to_karaka_mapping_v1.md`
