# Error Analysis Summary (Test Split, v2)

*Counts aggregate recurring test-set error patterns and are illustrative rather than a full partition of all errors.*

| Error Category | Representative Pattern | Stanza | UDPipe | Interpretation | Likely Future Direction |
|---|---|---:|---:|---|---|
| Unsupported UD dependency relations | Karma + mark; Karma + compound; Karta/Adhikarana + cc; Karta + root → no prediction | 818 | 800 | Current rule coverage does not assign Karaka labels to several frequently occurring structural UD dependency relations. | Expand UD-to-Karaka mapping coverage cautiously for high-frequency structural relations. |
| Karma–Sampradana ambiguity with को | obj/iobj + को → multi-candidate (strict fail) | 480 | 450 | The postposition को appears in both object and recipient/beneficiary contexts and does not alone support strict disambiguation. | Incorporate verb semantics and recipient/beneficiary or animacy cues beyond case marking. |
| Karana–Apadana ambiguity with से | obl/nmod + से → multi-candidate (strict fail) | 171 | 166 | Instrument and source readings with से remain unresolved without verb-class or contextual disambiguation. | Add verb-class and source/instrument disambiguation beyond postposition rules. |
| Residual Adhikarana ambiguity | Adhikarana + obl/nmod without locative marker, or with के → multi-candidate / no prediction | 290 | 284 | Many remaining Adhikarana errors lack the locative evidence used by the H1 correction rule. | Improve locative and temporal expression handling beyond में/पर. |
| Karta recall gaps | Karta gold → no prediction (diverse deprels) | 278 | 373 | Subject-like tokens often receive empty or non-unique candidate sets; UDPipe shows a higher rate on this subset. | Inspect parser subject labels and passive/subject diagnostics jointly with mapper coverage. |
| Gold–parser alignment limit | unmatched_gold (token alignment) | 22 | 22 | A small parser-independent subset of gold tokens could not be aligned to pipeline rows. | Improve token normalization and alignment auditing for edge-case token forms. |

Overall, most remaining errors arise from unsupported dependency relations or linguistically ambiguous markers such as को and से, suggesting that future improvements require richer semantic context rather than only additional postposition-based rules.

## Notes

- Hard wrong-label cases (`candidate_wrong`: 303 Stanza, 404 UDPipe) are more frequent for UDPipe than for Stanza, but are not treated as a separate linguistic category in this table.
- Row totals merge raw patterns from `*_test_error_patterns.csv` and `*_test_failure_by_karaka.csv`; see v1 merge notes for pattern-level breakdown.

## Merged raw patterns

### 1. Unsupported UD dependency relations (818 / 800)
- `Karma + mark` (447 / 447)
- `Karma + compound` (119 / 113)
- `Karta + root` (92 / 79)
- `Adhikarana + cc` (60 / 59)
- `Karta + cc` (56 / 56)
- `Karma + cc` (44 / 46)

### 2. Karma–Sampradana ambiguity with को (480 / 450)
- `Karma + obj + को` (316 / 298)
- `Sampradana + iobj + को` (126 / 104)
- `Sampradana + obj + को` (18 / 30)
- `Karma + iobj + को` (20 / 18)

### 3. Karana–Apadana ambiguity with से (171 / 166)
- `Apadana + obl + से` (116 / 110)
- `Karana + obl + से` (46 / 43)
- `Apadana + nmod + से` (9 / 13)

### 4. Residual Adhikarana ambiguity (290 / 284)
- `Adhikarana + obl + (blank)` (168 / 161)
- `Adhikarana + obl + के` (83 / 81)
- `Adhikarana + nmod + के` (21 / 22)
- `Adhikarana + nmod + (blank)` (18 / 20)

### 5. Karta recall gaps (278 / 373)
- Total `Karta` rows with `failure_type = no_prediction` from `failure_by_karaka.csv`

### 6. Gold–parser alignment limit (22 / 22)
- Total `unmatched_gold` from `failure_by_karaka.csv` (parser-independent)
