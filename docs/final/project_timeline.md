# Project Timeline

One-page chronological overview of the neuro-symbolic Hindi Karaka extraction project.

---

## Week 1 — Dataset exploration and rule design

- Explored Hindi-HDTB UD structure, dependency distributions, and postposition patterns.
- Drafted Mapper v1 hypotheses and Verifier v1 rule specifications (R1–R5).
- Notebooks: `notebooks/exploration/01–03`.

## Week 2 — Mapper v1 and Verifier v1

- Implemented conservative UD-to-Karaka mapping (`src/mapper/simple_mapper.py`).
- Implemented postposition-based verifier (`src/verifier/simple_verifier.py`).
- Built gold-UD pipeline runner and case-marker extraction.
- Evaluated verifier behavior on gold UD dev trees.

## Week 3 — HDTB alignment and gold Karaka labels

- Aligned Hindi-HDTB UD sentences with original HDTB `.dat` files.
- Extracted restricted gold Karaka label set for evaluation.
- Established token-matching protocol for pipeline vs gold comparison.

## Week 4 — Stanza baseline and correction layer development

- Replaced gold-UD input with Stanza neural parses.
- Ran train/dev Stanza baselines; mined dev errors for actionable patterns.
- Implemented Correction Layer v2; accepted **H1** (`nmod + में/पर → Adhikarana`).
- Investigated passive diagnostics and **rejected DR1** dependency repair.

## Week 5 — Evaluation freeze and held-out test

- Froze Mapper v1, Verifier v1, and Correction Layer v2.1 (H1 only).
- Ran final held-out **test evaluation once** (Stanza).
- Documented final train/dev/test results and project reference handbook.
- **Freeze point:** symbolic system and primary metrics locked.

---

## Post-freeze work

### Repository reorganization

- Restructured `outputs/`, `experiments/`, `scripts/`, `docs/`, `notebooks/`.
- Added `src/paths.py` and `scripts/_bootstrap.py`.
- Moved artifacts without regenerating Stanza results (`MIGRATION_LOG.md`).

### UDPipe parser extension

- Added UDPipe Hindi-HDTB model and parser wrapper.
- Ran parallel dev/test baselines and correction evaluation under frozen rules.
- Confirmed cross-parser robustness; no symbolic rule changes.

### Final error analysis

- Implemented `scripts/analysis/analyze_final_error_patterns.py`.
- Produced row-level error outputs, failure taxonomy, and paper-ready summary table.
- Sanity-checked major error categories against sampled test cases.

### Paper polishing

- Updated project documentation to reflect post-freeze state.
- Prepared cross-parser comparison tables and expanded error-analysis outline for paper writing.

---

## Current state

The repository contains a **frozen Stanza-evaluated neuro-symbolic system**, a **parallel UDPipe robustness branch**, **final error-analysis artifacts**, and **paper-ready documentation** — ready for paper writing without further system changes.
