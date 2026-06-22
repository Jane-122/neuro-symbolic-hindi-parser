# Final Held-Out Test Results

This report documents the final held-out test evaluation for:

**Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses**

## Evaluation Context

- This is the **final held-out test evaluation**.
- Test was run **once** after Mapper v1, Verifier v1, and Correction Layer v2.1 were frozen.
- Correction v2.1 contains only **H1_NMOD_LOCATIVE_ADHIKARANA**:

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

- No passive correction rules were used.
- No dependency repair (DR1) was used.

## Evaluation Modes

Two scoring modes are reported:

- **Candidate-set**: a prediction is correct if the gold Karaka appears anywhere in the predicted candidate set.
- **Strict**: a prediction is correct only if the system predicts exactly one Karaka and that label matches the gold Karaka.

Systems:

- **Neural Only**: `mapper_candidates`
- **Verifier v1**: `final_candidates`
- **Correction v2.1**: `corrected_candidates`

Source: `output/test_correction_v2_metrics.csv`, `output/test_correction_v2_per_karaka_comparison.csv`

## 1. Overall Test Metrics

| System | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|--------|--------------------|--------------------|-----------------|-----------------|
| Neural Only | 0.7356 | 0.5621 | 0.4850 | 0.3876 |
| Verifier v1 | 0.7373 | 0.5716 | 0.5785 | 0.4220 |
| Correction v2.1 | 0.7568 | 0.5786 | 0.5980 | 0.4308 |

Test support: `5,946` gold Karaka rows.

## 2. Absolute Improvements

| Comparison | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|------------|--------------------|--------------------|-----------------|-----------------|
| Verifier v1 - Neural Only | +0.0017 | +0.0095 | +0.0935 | +0.0344 |
| Correction v2.1 - Verifier v1 | +0.0195 | +0.0070 | +0.0195 | +0.0088 |
| Correction v2.1 - Neural Only | +0.0212 | +0.0165 | +0.1130 | +0.0432 |

## 3. Matched / Unmatched Counts

| Metric | Count |
|--------|------:|
| Total gold rows | 5946 |
| Matched rows | 5924 |
| Unmatched rows | 22 |
| Match percentage | 99.63% |

Token matching key: `split + sent_id + normalized token text + occurrence order`.

## 4. Per-Karaka Comparison

### Candidate F1

| Karaka | Neural Only | Verifier v1 | Correction v2.1 |
|--------|-------------|-------------|-------------------|
| Karta | 0.8790 | 0.8790 | 0.8790 |
| Karma | 0.6736 | 0.6529 | 0.6529 |
| Karana | 0.0643 | 0.1694 | 0.1694 |
| Sampradana | 0.7730 | 0.4988 | 0.4988 |
| Apadana | 0.1484 | 0.3479 | 0.3479 |
| Adhikarana | 0.8345 | 0.8815 | 0.9239 |

### Strict F1

| Karaka | Neural Only | Verifier v1 | Correction v2.1 |
|--------|-------------|-------------|-------------------|
| Karta | 0.8790 | 0.8790 | 0.8790 |
| Karma | 0.6736 | 0.5104 | 0.5104 |
| Karana | 0.0000 | 0.0000 | 0.0000 |
| Sampradana | 0.7730 | 0.3716 | 0.3716 |
| Apadana | 0.0000 | 0.0000 | 0.0000 |
| Adhikarana | 0.0000 | 0.7713 | 0.8237 |

## 5. H1 Impact Summary

| Metric | Value |
|--------|------:|
| H1 firing count on test | 130 |
| Adhikarana Candidate F1 (Verifier v1 → Correction v2.1) | 0.8815 → 0.9239 (+0.0424) |
| Adhikarana Strict F1 (Verifier v1 → Correction v2.1) | 0.7713 → 0.8237 (+0.0524) |

H1 did not change F1 for any Karaka other than Adhikarana on test.

## 6. Interpretation

### What Improved

**Verifier v1 provides the largest strict accuracy gain.**

On test, Verifier v1 over Neural Only improves:

- Strict accuracy by **+0.0935** (0.4850 → 0.5785)
- Strict macro F1 by **+0.0344** (0.3876 → 0.4220)

This shows that postposition-based verification over Stanza dependency parses is the main source of strict disambiguation gain.

**Correction v2.1 gives an additional smaller but consistent improvement.**

Correction v2.1 over Verifier v1 improves:

- Candidate accuracy by **+0.0195**
- Strict accuracy by **+0.0195**
- Candidate macro F1 by **+0.0070**
- Strict macro F1 by **+0.0088**

**H1 generalizes to test and improves Adhikarana specifically.**

On held-out test, H1 fired 130 times and improved Adhikarana:

- Candidate F1: 0.8815 → 0.9239
- Strict F1: 0.7713 → 0.8237

This matches the train/dev pattern and supports retaining H1 as a conservative, localized correction rule.

### What Did Not Improve

Some Karakas do not improve under the frozen pipeline, especially under strict scoring:

- **Karma**: strict F1 drops from 0.6736 (Neural Only) to 0.5104 (Verifier v1 / Correction v2.1)
- **Sampradana**: strict F1 drops from 0.7730 (Neural Only) to 0.3716 (Verifier v1 / Correction v2.1)
- **Karana** and **Apadana** remain at 0.0000 strict F1 after Verifier v1

Correction v2.1 does not change these classes because H1 targets only locative `nmod + में/पर` cases.

**Karana and Apadana remain difficult** because the system keeps ambiguous `से` cases unresolved. These were flagged diagnostically during development but were not converted into automatic correction rules.

### Project Framing

The result supports **Karaka extraction improvement over neural dependency parses**, not UD dependency parsing improvement.

The accepted correction layer improves semantic role interpretation from Stanza output. It does not claim to repair UD dependency labels themselves.

## 7. Final Conclusion

The frozen neuro-symbolic pipeline improves strict Karaka extraction accuracy from **0.4850** to **0.5980** on held-out test, with the strongest localized correction effect on **Adhikarana**.

Overall test progression:

| Stage | Strict Accuracy |
|-------|----------------:|
| Neural Only | 0.4850 |
| Verifier v1 | 0.5785 |
| Correction v2.1 | 0.5980 |

This held-out result completes the final evaluation for the project’s frozen Mapper v1, Verifier v1, and Correction Layer v2.1 system.
