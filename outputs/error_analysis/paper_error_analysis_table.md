# Error Analysis Summary (Test Split)

Compact table derived from `outputs/error_analysis/*_test_{failure_by_karaka,error_patterns,confusion_summary}.csv`. Counts sum merged recurring error patterns; rows are illustrative rather than a full partition of all errors.

| Error Category | Representative Pattern | Stanza | UDPipe | Interpretation |
|---|---|---:|---:|---|
| Unmapped dependency relations | Karma + mark; compound/cc/root and similar structural deps → no prediction | 818 | 800 | The frozen mapper does not assign Karaka labels for several frequent UD relations under the current rule set. |
| Karma–Sampradana disambiguation | obj/iobj + को → multi-candidate (strict fail) | 480 | 450 | The dative case marker को co-occurs with both Karma and Sampradana contexts and does not alone support strict single-label resolution. |
| Karana–Apadana disambiguation | obl/nmod + से → multi-candidate (strict fail) | 171 | 166 | Instrument and source readings with से remain ambiguous without additional verb-semantic or contextual cues. |
| Residual Adhikarana ambiguity | Adhikarana + obl/nmod without locative marker, or with के → multi-candidate / no prediction | 290 | 284 | Many Adhikarana errors lack the locative evidence targeted by the H1 correction rule. |
| Karta recall gaps | Karta gold → no prediction (diverse deprels) | 278 | 373 | Subject-like tokens often receive empty or non-unique candidate sets; UDPipe shows a higher rate on this subset. |
| Parser-induced label mismatch | candidate_wrong (e.g. Karma nsubj → Karta) | 303 | 404 | Hard label conflicts are relatively infrequent but more common with UDPipe than Stanza under the same frozen stack. |
| Gold–parser alignment | unmatched_gold (token alignment) | 22 | 22 | A small parser-independent subset of gold tokens could not be aligned to pipeline rows. |

## Merged raw patterns

### 1. Unmapped dependency relations (818 / 800)
- `Karma + mark` (447 / 447)
- `Karma + compound` (119 / 113)
- `Karta + root` (92 / 79)
- `Adhikarana + cc` (60 / 59)
- `Karta + cc` (56 / 56)
- `Karma + cc` (44 / 46)

### 2. Karma–Sampradana disambiguation (480 / 450)
- `Karma + obj + को` (316 / 298)
- `Sampradana + iobj + को` (126 / 104)
- `Sampradana + obj + को` (18 / 30)
- `Karma + iobj + को` (20 / 18)

### 3. Karana–Apadana disambiguation (171 / 166)
- `Apadana + obl + से` (116 / 110)
- `Karana + obl + से` (46 / 43)
- `Apadana + nmod + से` (9 / 13)

### 4. Residual Adhikarana ambiguity (290 / 284)
- `Adhikarana + obl + (blank)` (168 / 161)
- `Adhikarana + obl + के` (83 / 81)
- `Adhikarana + nmod + के` (21 / 22)
- `Adhikarana + nmod + (blank)` (18 / 20)

### 5. Karta recall gaps (278 / 373)
- Total `Karta` rows with `failure_type = no_prediction` from `failure_by_karaka.csv` (278 / 373)

### 6. Parser-induced label mismatch (303 / 404)
- Total `candidate_wrong` across all Karaka labels from `failure_by_karaka.csv` (303 / 404)
- Representative confusion: `Karma + nsubj → Karta` (107 / 103) from `error_patterns.csv` / `confusion_summary.csv`

### 7. Gold–parser alignment (22 / 22)
- Total `unmatched_gold` for `Karta` from `failure_by_karaka.csv` (22 / 22; parser-independent)

## Grouping assumptions

- Counts are taken from existing test-split error-analysis CSVs only; no experiments were rerun.
- Pattern merges group rows sharing the same linguistic mechanism (e.g. all `को`-marked obj/iobj ambiguity), not identical failure types.
- Row totals can overlap conceptually with failure-type summaries but do not double-count within a row (each raw pattern appears in at most one row).
- Rows 5–6 use aggregate failure-type totals where a single deprel signature is not dominant.
- Minor patterns (≤10 occurrences) and `candidate_correct_strict_fail` tails outside the merges above are omitted to keep the table compact.
- Interpretations describe observed error tendencies on the test split; they are not claims about upper bounds on correctable errors.
