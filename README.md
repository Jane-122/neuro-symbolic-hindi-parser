# Neuro-Symbolic Dependency Parsing for Hindi

Integrating Paninian Karaka rules with neural dependency parsers.

## Overview

This research project explores a neuro-symbolic approach to Hindi dependency parsing. Neural parsers produce Universal Dependencies (UD) analyses; a symbolic layer maps those analyses to Paninian Karaka roles and verifies them against grammatical constraints.

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
  evaluation/   # Metrics and evaluation utilities
results/        # Experiment outputs and reports
logs/           # Run logs
docs/           # Research documentation
```

## Research Goals

- Parse Hindi sentences using neural UD parsers
- Map UD dependency relations to Paninian Karaka roles
- Verify Karaka assignments against Paninian grammatical rules
- Evaluate parser output and neuro-symbolic integration

## Documentation

- [Project Scope](docs/project_scope.md)
- [UD to Karaka Mapping](docs/ud_to_karaka_mapping.md)
- [Research Notes](docs/research_notes.md)

## Setup

Dependencies will be listed in `requirements.txt` as the project develops.

## Status

Early-stage research. Project structure and documentation are in place; implementation has not yet begun.
