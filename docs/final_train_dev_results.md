# Final Train and Dev Results

This report consolidates existing train and dev evaluation outputs for the current project framing:

**Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses**

No test results are included. The test split remains frozen for final held-out evaluation.

## Evaluation Modes

Two scoring modes are reported:

- **Candidate-set**: a prediction is correct if the gold Karaka appears anywhere in the predicted candidate set.
- **Strict**: a prediction is correct only if the system predicts exactly one Karaka and that label matches the gold Karaka.

Systems:

- **Neural Only**: `mapper_candidates`
- **Verifier v1**: `final_candidates`
- **Correction v2.1**: `corrected_candidates`

## 1. Overall Train Results

Source: `output/train_correction_v2_metrics.csv`

| System | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|--------|--------------------|--------------------|-----------------|-----------------|
| Neural Only | 0.7865 | 0.6023 | 0.5310 | 0.4234 |
| Verifier v1 | 0.7864 | 0.6023 | 0.6259 | 0.4451 |
| Correction v2.1 | 0.8004 | 0.6073 | 0.6400 | 0.4513 |

Train support: `47,378` gold Karaka rows.

## 2. Overall Dev Results

Source: `output/dev_correction_v2_metrics.csv`

| System | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|--------|--------------------|--------------------|-----------------|-----------------|
| Neural Only | 0.7369 | 0.5599 | 0.4909 | 0.3877 |
| Verifier v1 | 0.7403 | 0.5724 | 0.5947 | 0.4153 |
| Correction v2.1 | 0.7574 | 0.5784 | 0.6118 | 0.4226 |

Dev support: `5,902` gold Karaka rows.

## 3. Absolute Improvements

### Train

| Comparison | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|------------|--------------------|--------------------|-----------------|-----------------|
| Verifier v1 - Neural Only | -0.0001 | +0.0000 | +0.0949 | +0.0217 |
| Correction v2.1 - Verifier v1 | +0.0140 | +0.0050 | +0.0141 | +0.0062 |
| Correction v2.1 - Neural Only | +0.0139 | +0.0050 | +0.1090 | +0.0279 |

### Dev

| Comparison | Candidate Accuracy | Candidate Macro F1 | Strict Accuracy | Strict Macro F1 |
|------------|--------------------|--------------------|-----------------|-----------------|
| Verifier v1 - Neural Only | +0.0034 | +0.0125 | +0.1038 | +0.0276 |
| Correction v2.1 - Verifier v1 | +0.0171 | +0.0060 | +0.0171 | +0.0073 |
| Correction v2.1 - Neural Only | +0.0205 | +0.0185 | +0.1209 | +0.0349 |

## 4. Adhikarana-Specific Results

H1 in Correction Layer v2.1 targets locative `nmod + में/पर` cases, so the expected direct effect is on `Adhikarana`.

### Train Adhikarana F1

Source: `output/train_correction_v2_metrics.csv`

| System | Candidate F1 | Strict F1 |
|--------|--------------|-----------|
| Neural Only | 0.8621 | 0.0000 |
| Verifier v1 | 0.9026 | 0.7890 |
| Correction v2.1 | 0.9325 | 0.8265 |

Train Adhikarana support: `12,436`.

### Dev Adhikarana F1

Source: `output/dev_correction_v2_per_karaka_comparison.csv`

| System | Candidate F1 | Strict F1 |
|--------|--------------|-----------|
| Neural Only | 0.8491 | 0.0000 |
| Verifier v1 | 0.8881 | 0.7897 |
| Correction v2.1 | 0.9241 | 0.8335 |

Dev Adhikarana support: `1,567`.

### Adhikarana Absolute Improvements

| Split | Comparison | Candidate F1 | Strict F1 |
|-------|------------|--------------|-----------|
| Train | Verifier v1 - Neural Only | +0.0405 | +0.7890 |
| Train | Correction v2.1 - Verifier v1 | +0.0299 | +0.0375 |
| Train | Correction v2.1 - Neural Only | +0.0704 | +0.8265 |
| Dev | Verifier v1 - Neural Only | +0.0390 | +0.7897 |
| Dev | Correction v2.1 - Verifier v1 | +0.0360 | +0.0438 |
| Dev | Correction v2.1 - Neural Only | +0.0750 | +0.8335 |

## 5. Interpretation

### What Improved

Correction v2.1 improves both train and dev overall results.

The strongest and most localized gain is for `Adhikarana`:

- Dev candidate F1 improves from `0.8881` to `0.9241` over Verifier v1.
- Dev strict F1 improves from `0.7897` to `0.8335` over Verifier v1.
- Train candidate F1 improves from `0.9026` to `0.9325`.
- Train strict F1 improves from `0.7890` to `0.8265`.

This matches the intended scope of H1:

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

### What Did Not Improve

H1 does not improve unrelated Karakas. This is expected.

On dev, the following F1 values are unchanged from Verifier v1 to Correction v2.1:

- `Karta`
- `Karma`
- `Karana`
- `Sampradana`
- `Apadana`

Some classes remain weak under strict scoring, especially:

- `Karana`
- `Apadana`

However, H1 was not designed to address these classes. Their low strict scores should not be interpreted as H1 failure.

### Why H1 Is Retained

H1 is retained as Correction Layer v2.1 because:

- It is linguistically motivated by locative postpositions `में` and `पर`.
- It addresses a specific Stanza pattern: `nmod + में/पर` where the gold Karaka is often `Adhikarana`.
- It improves both train and dev.
- It improves both candidate-set and strict metrics.
- Its effect is localized to `Adhikarana`, reducing the risk of broad unintended side effects.

The rule should be described as improving **Karaka extraction and interpretation**, not as repairing UD dependency parses.

## 6. Reporting Note

These are train/dev results only. Test has not been run for final reporting and must remain frozen until all correction decisions are finalized.
