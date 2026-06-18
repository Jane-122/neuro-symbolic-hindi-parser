# Neuro-Symbolic Karaka Extraction for Hindi

Extracting and correcting Paninian Karaka roles from neural dependency parses.

## Overview

This research project explores **Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses**.

Neural parsers such as Stanza provide Universal Dependencies style parses. The symbolic layer does not claim to improve UD dependency parsing directly. Instead, it uses dependency labels, case markers, and Paninian linguistic rules to improve Karaka extraction and interpretation over those neural parses.

The current accepted correction layer is Correction Layer v2.1, which contains only one automatic rule:

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

Rule ID: `H1_NMOD_LOCATIVE_ADHIKARANA`

The test split is intentionally frozen and should not be used for further rule design.

## Project Structure

```
data/
  raw/          # Original corpora and annotations
  processed/    # Cleaned and transformed datasets
notebooks/      # Exploratory analysis and experiments
src/
  parser/       # Neural dependency parsing interface
  mapper/       # UD to Karaka role mapping
  verifier/     # Paninian rule verification
  pipeline/     # Pipeline, correction, and repair experiments
scripts/        # Alignment, extraction, evaluation, and error analysis scripts
output/         # Generated alignment, gold labels, metrics, and audits
results/        # Experiment outputs and reports
logs/           # Run logs
docs/           # Research documentation
```

## Research Goals

- Use neural dependency parses as input evidence.
- Extract Paninian Karaka candidates from UD-style dependency output.
- Verify and correct Karaka candidates using symbolic Paninian rules.
- Evaluate Karaka extraction against HDTB-derived gold Karaka labels.
- Report both positive and negative correction-layer findings without claiming direct UD parsing improvement.

## Current Findings

- HDTB to UD sentence alignment is complete for dev and test, with four unmatched train sentences.
- Core gold Karaka labels are extracted from raw HDTB `.dat` files.
- Correction Layer v2.1 improves Karaka extraction on train and dev through H1.
- A direct dependency-label repair experiment, DR1 (`nmod + में/पर -> obl`), was rejected because it reduced dev UD deprel accuracy from `95.16%` to `94.85%`.
- Therefore, the project is framed as Karaka extraction and interpretation over neural parses, not as direct improvement of dependency parsing.

## Documentation

- [Project Context](docs/project_context.md)
- [Correction Layer Log](docs/correction_layer_log.md)
- [Project Status Checkpoint 3](docs/project_status_checkpoint_3.md)
- [Research Notes](docs/research_notes.md)

## Setup

Dependencies are listed in `requirements.txt`, with additional parser setup required for Stanza if running parser baselines.

## Status

Active research prototype. Mapper v1, Verifier v1, HDTB alignment, gold Karaka extraction, Stanza baselines, Correction Layer v2.1, and train/dev evaluations are implemented. Test remains frozen for final held-out evaluation.
