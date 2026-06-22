# Final Results Tables

Consolidated from:

- `docs/final_train_dev_results.md`
- `docs/final_test_results.md`

**Project framing:** Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses

## Scoring Note

Two evaluation modes are used:

| Mode | Definition | Reporting priority |
|------|------------|-------------------|
| **Strict** | Correct only if the system predicts exactly one Karaka and it matches gold | **Primary** |
| Candidate-set | Correct if gold Karaka appears anywhere in the predicted candidate set | Secondary |

Systems:

| Label | Prediction column |
|-------|-------------------|
| Neural Only | `mapper_candidates` |
| Verifier v1 | `final_candidates` |
| Correction v2.1 | `corrected_candidates` |

Correction v2.1 is frozen with one accepted rule: **H1_NMOD_LOCATIVE_ADHIKARANA** (`nmod + में/पर -> Adhikarana`). No passive correction. No dependency repair DR1.

---

## Table 1: Overall Train Results

Gold Karaka rows: **47,378**

| System | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|--------|--------------------:|-------------------:|----------------:|----------------:|
| Neural Only | 0.7865 | 0.6023 | 0.5310 | 0.4234 |
| Verifier v1 | 0.7864 | 0.6023 | 0.6259 | 0.4451 |
| Correction v2.1 | 0.8004 | 0.6073 | 0.6400 | 0.4513 |

---

## Table 2: Overall Dev Results

Gold Karaka rows: **5,902**

| System | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|--------|--------------------:|-------------------:|----------------:|----------------:|
| Neural Only | 0.7369 | 0.5599 | 0.4909 | 0.3877 |
| Verifier v1 | 0.7403 | 0.5724 | 0.5947 | 0.4153 |
| Correction v2.1 | 0.7574 | 0.5784 | 0.6118 | 0.4226 |

---

## Table 3: Overall Test Results (Held-Out)

Gold Karaka rows: **5,946**

| System | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|--------|--------------------:|-------------------:|----------------:|----------------:|
| Neural Only | 0.7356 | 0.5621 | 0.4850 | 0.3876 |
| Verifier v1 | 0.7373 | 0.5716 | 0.5785 | 0.4220 |
| Correction v2.1 | 0.7568 | 0.5786 | 0.5980 | 0.4308 |

Test was run once after Mapper v1, Verifier v1, and Correction v2.1 were frozen.

---

## Table 4: Strict Accuracy Progression (Train / Dev / Test)

Primary metric comparison across splits and pipeline stages.

| Split | Neural Only | Verifier v1 | Correction v2.1 | Verifier v1 gain | Correction v2.1 gain (over Verifier v1) | Total gain (Correction v2.1 over Neural Only) |
|-------|------------:|------------:|----------------:|-----------------:|----------------------------------------:|----------------------------------------------:|
| Train | 0.5310 | 0.6259 | 0.6400 | +0.0949 | +0.0141 | +0.1090 |
| Dev | 0.4909 | 0.5947 | 0.6118 | +0.1038 | +0.0171 | +0.1209 |
| Test | 0.4850 | 0.5785 | 0.5980 | +0.0935 | +0.0195 | +0.1130 |

Strict macro F1 progression:

| Split | Neural Only | Verifier v1 | Correction v2.1 |
|-------|------------:|------------:|----------------:|
| Train | 0.4234 | 0.4451 | 0.4513 |
| Dev | 0.3877 | 0.4153 | 0.4226 |
| Test | 0.3876 | 0.4220 | 0.4308 |

---

## Table 5: H1 Adhikarana Impact (Train / Dev / Test)

Rule: `nmod + में/पर -> Adhikarana`

### Adhikarana F1 by System

| Split | Support | Neural Only Cand. F1 | Verifier v1 Cand. F1 | Correction v2.1 Cand. F1 | Neural Only Strict F1 | Verifier v1 Strict F1 | Correction v2.1 Strict F1 |
|-------|--------:|---------------------:|---------------------:|-------------------------:|----------------------:|-----------------------:|--------------------------:|
| Train | 12,436 | 0.8621 | 0.9026 | 0.9325 | 0.0000 | 0.7890 | 0.8265 |
| Dev | 1,567 | 0.8491 | 0.8881 | 0.9241 | 0.0000 | 0.7897 | 0.8335 |
| Test | 1,584 | 0.8345 | 0.8815 | 0.9239 | 0.0000 | 0.7713 | 0.8237 |

### H1 Firing Count and Verifier v1 to Correction v2.1 Gains

| Split | H1 fires | Candidate F1 gain | Strict F1 gain |
|-------|--------:|------------------:|---------------:|
| Train | 830 | +0.0299 (0.9026 to 0.9325) | +0.0375 (0.7890 to 0.8265) |
| Dev | 121 | +0.0360 (0.8881 to 0.9241) | +0.0438 (0.7897 to 0.8335) |
| Test | 130 | +0.0424 (0.8815 to 0.9239) | +0.0524 (0.7713 to 0.8237) |

H1 did not change F1 for Karakas other than Adhikarana on dev and test.

---

## Table 6: Final Test Absolute Improvements

Held-out test only.

| Comparison | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|------------|-------------------:|-------------------:|----------------:|----------------:|
| Verifier v1 - Neural Only | +0.0017 | +0.0095 | +0.0935 | +0.0344 |
| Correction v2.1 - Verifier v1 | +0.0195 | +0.0070 | +0.0195 | +0.0088 |
| Correction v2.1 - Neural Only | +0.0212 | +0.0165 | +0.1130 | +0.0432 |

Headline held-out result:

| Metric | Neural Only | Correction v2.1 | Absolute gain |
|--------|------------:|----------------:|--------------:|
| Strict Accuracy | 0.4850 | 0.5980 | +0.1130 |

---

## Table 7: Test Per-Karaka F1 (Strict and Candidate)

### Candidate F1 (Test)

| Karaka | Neural Only | Verifier v1 | Correction v2.1 |
|--------|------------:|------------:|----------------:|
| Karta | 0.8790 | 0.8790 | 0.8790 |
| Karma | 0.6736 | 0.6529 | 0.6529 |
| Karana | 0.0643 | 0.1694 | 0.1694 |
| Sampradana | 0.7730 | 0.4988 | 0.4988 |
| Apadana | 0.1484 | 0.3479 | 0.3479 |
| Adhikarana | 0.8345 | 0.8815 | 0.9239 |

### Strict F1 (Test)

| Karaka | Neural Only | Verifier v1 | Correction v2.1 |
|--------|------------:|------------:|----------------:|
| Karta | 0.8790 | 0.8790 | 0.8790 |
| Karma | 0.6736 | 0.5104 | 0.5104 |
| Karana | 0.0000 | 0.0000 | 0.0000 |
| Sampradana | 0.7730 | 0.3716 | 0.3716 |
| Apadana | 0.0000 | 0.0000 | 0.0000 |
| Adhikarana | 0.0000 | 0.7713 | 0.8237 |

---

## Table 8: Token Matching Counts (Test)

Matching key: `split + sent_id + normalized token text + occurrence order`

| Metric | Test |
|--------|-----:|
| Total gold rows | 5946 |
| Matched rows | 5924 |
| Unmatched rows | 22 |
| Match percentage | 99.63% |

Unmatched gold rows receive empty predictions during evaluation.

---

## Table 9: Train and Dev Absolute Improvements (Reference)

### Train

| Comparison | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|------------|-------------------:|-------------------:|----------------:|----------------:|
| Verifier v1 - Neural Only | -0.0001 | +0.0000 | +0.0949 | +0.0217 |
| Correction v2.1 - Verifier v1 | +0.0140 | +0.0050 | +0.0141 | +0.0062 |
| Correction v2.1 - Neural Only | +0.0139 | +0.0050 | +0.1090 | +0.0279 |

### Dev

| Comparison | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|------------|-------------------:|-------------------:|----------------:|----------------:|
| Verifier v1 - Neural Only | +0.0034 | +0.0125 | +0.1038 | +0.0276 |
| Correction v2.1 - Verifier v1 | +0.0171 | +0.0060 | +0.0171 | +0.0073 |
| Correction v2.1 - Neural Only | +0.0205 | +0.0185 | +0.1209 | +0.0349 |

---

## Reporting Guidance for the Paper

- Lead with **strict accuracy** and **strict macro F1** in abstract and results.
- Present candidate-set metrics as supplementary analysis for ambiguous mapper outputs.
- Present Verifier v1 and Correction v2.1 as sequential stages, not independent systems trained on test.
- Describe H1 as a localized Adhikarana correction, not a general Karaka parser.
- Do not claim UD dependency parsing improvement; cite DR1 separately as a negative result (see `final_figures.md`).
