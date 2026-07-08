# Sanity Check: Unsupported / Unmapped UD Relations Row

**Table row under review:** Unsupported UD dependency relations (818 Stanza / 800 UDPipe)

**Bucket definition:** Gold rows with `failure_type = no_prediction` and `(gold_karaka, deprel, case_marker)` in:
- `Karma + mark`
- `Karma + compound`
- `Karta + root`
- `Adhikarana + cc`
- `Karta + cc`
- `Karma + cc`

**Sampling:** 10 random examples per parser (`random.seed(42)`) from `*_test_final_error_rows.csv`.

**Count verification:** Bucket sizes match merged counts from `*_test_error_patterns.csv` exactly (818 / 800).

---

## Stanza samples (10)

| # | sent_id | gold_token | gold_karaka | deprel | failure_type | corrected_candidates |
|---|---------|------------|-------------|--------|--------------|----------------------|
| 1 | test-s1290 | कि | Karma | mark | no_prediction | (empty) |
| 2 | test-s282 | कि | Karma | mark | no_prediction | (empty) |
| 3 | test-s113 | उम्मीद | Karta | root | no_prediction | (empty) |
| 4 | test-s1511 | कि | Karma | mark | no_prediction | (empty) |
| 5 | test-s624 | और | Karma | cc | no_prediction | (empty) |
| 6 | test-s556 | और | Karta | cc | no_prediction | (empty) |
| 7 | test-s515 | संभावना | Karta | root | no_prediction | (empty) |
| 8 | test-s322 | कि | Karma | mark | no_prediction | (empty) |
| 9 | test-s1489 | मनाही | Karta | root | no_prediction | (empty) |
| 10 | test-s271 | माँग | Karta | root | no_prediction | (empty) |

**Sample breakdown:** mark 4, root 4, cc 2 (no compound in this draw; compound cases exist elsewhere in bucket).

---

## UDPipe samples (10)

| # | sent_id | gold_token | gold_karaka | deprel | failure_type | corrected_candidates |
|---|---------|------------|-------------|--------|--------------|----------------------|
| 1 | test-s1412 | कि | Karma | mark | no_prediction | (empty) |
| 2 | test-s1569 | और | Adhikarana | cc | no_prediction | (empty) |
| 3 | test-s1140 | व | Adhikarana | cc | no_prediction | (empty) |
| 4 | test-s242 | और | Karma | cc | no_prediction | (empty) |
| 5 | test-s1234 | योजना | Karma | compound | no_prediction | (empty) |
| 6 | test-s883 | कि | Karma | mark | no_prediction | (empty) |
| 7 | test-s129 | दायित्व | Karma | compound | no_prediction | (empty) |
| 8 | test-s125 | कि | Karma | mark | no_prediction | (empty) |
| 9 | test-s251 | और | Adhikarana | cc | no_prediction | (empty) |
| 10 | test-s530 | कि | Karma | mark | no_prediction | (empty) |

**Sample breakdown:** mark 5, cc 4, compound 2.

---

## Conclusion

**The row is valid** for the paper table as defined: all 20 sampled cases are genuine `no_prediction` errors on structural UD relations (`mark`, `compound`, `cc`, `root`) with empty candidate sets at every pipeline stage.

No adjustment to the row counts is required based on this check.

---

## Caveats

1. **Dominance of `Karma + mark`:** 447 of 818 Stanza cases (and 447 of 800 UDPipe) are complementizer `कि` tagged as `mark` with gold Karma. These reflect both unmapped UD relations and annotation of clausal/complement structure not covered by current rules—not purely “unsupported deprel” in a narrow sense.
2. **`cc` and `root` cases are heterogeneous:** Coordinators (`और`, `व`) and nominal roots (`उम्मीद`, `माँग`) carry diverse gold Karaka labels; some may eventually need semantic or discourse-level treatment rather than simple deprel-to-Karaka expansion.
3. **Gold vs. mapper perspective:** The row describes gaps in current rule coverage, not necessarily incorrect gold labels.
4. **Strict bucket filter:** Only `no_prediction` rows are included; ambiguous multi-candidate cases on related deprels appear in other table rows.
5. **Parser parity:** Stanza and UDPipe counts are nearly identical for this bucket (818 vs. 800), consistent with a mapper-coverage limitation rather than parser-specific noise.
