# Neuro-Symbolic Karaka Extraction for Hindi

Extracting and correcting Paninian Karaka roles from neural dependency parses.

## Overview

This repository implements **Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses**.

Stanza provides Universal Dependencies-style parses. The symbolic layer does not claim to improve UD dependency parsing directly. It uses dependency labels, case markers, and Paninian linguistic rules to improve Karaka extraction over those neural parses.

**Pipeline:** Sentence → Stanza → Mapper v1 → Verifier v1 → Correction Layer v2.1 → Karaka prediction

**Status:** Final held-out test evaluation is complete. Mapper v1, Verifier v1, and Correction Layer v2.1 are frozen.

## Final Test Results (Held-Out)

Evaluation over 5,946 gold Karaka rows (5,924 matched; 22 unmatched counted as incorrect).

| System | Candidate Accuracy | Strict Accuracy |
|--------|-------------------:|----------------:|
| Neural Only | 0.7356 | 0.4850 |
| Verifier v1 | 0.7373 | 0.5785 |
| Correction v2.1 | 0.7568 | 0.5980 |

Strict accuracy improves from **0.4850** (neural only) to **0.5980** (correction v2.1) on held-out test.

## Frozen Correction Layer v2.1

Correction Layer v2.1 is frozen and contains **one accepted automatic rule only**:

**Rule ID:** `H1_NMOD_LOCATIVE_ADHIKARANA`

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

Passive correction rules and dependency repair (DR1) were investigated but are **not** part of the final system.

## Evaluated Systems

| System | Output column |
|--------|---------------|
| Neural Only | `mapper_candidates` |
| Verifier v1 | `final_candidates` |
| Correction v2.1 | `corrected_candidates` |

## Project Structure

```
data/raw/       # UD CoNLL-U splits (HDTB raw .dat files are local-only, gitignored)
src/
  parser/       # Stanza wrapper
  mapper/       # Mapper v1
  verifier/     # Verifier v1
  pipeline/     # Baseline runners and correction layer
scripts/        # Alignment, extraction, evaluation, error analysis
output/         # Metrics, gold labels, alignment artifacts (small CSVs)
docs/           # Final results and project reference
notebooks/      # Exploratory analysis
results/        # Large pipeline CSVs (gitignored)
```

## Reproducing Evaluation

```bash
pip install -r requirements.txt
python -m stanza.download hi tokenize pos lemma depparse

python src/pipeline/run_stanza_baseline.py --split test
python scripts/apply_correction_v2.py --split test
python scripts/evaluate_correction_v2.py --split test
```

Use `train` or `dev` instead of `test` for non-held-out splits. Large baseline outputs are written locally under `results/` and are not tracked in git.

## Documentation

- [Final Test Results](docs/final_test_results.md)
- [Final Train/Dev Results](docs/final_train_dev_results.md)
- [Final Project Reference](docs/final_project_reference.md)
- [Paper Implementation Audit](docs/paper_implementation_audit.md)
- [Correction Layer Log](docs/correction_layer_log.md)
- [Project Context](docs/project_context.md)

## Setup

Install dependencies from `requirements.txt`. Stanza requires a one-time Hindi model download (see command above). Original HDTB `.dat` files and large generated CSVs are excluded from the repository; place HDTB raw data under `data/raw/news_articles_and_heritage/` locally to regenerate gold labels.
