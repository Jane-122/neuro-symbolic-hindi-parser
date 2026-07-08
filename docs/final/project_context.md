# Project Context — Current Status

**Last updated:** Post-freeze documentation pass (2026)

**Primary reference:** `docs/final/final_project_reference.md`  
**Post-freeze additions:** `docs/final/project_update_after_freeze.md`

For original motivation, research questions, and verifier design principles, see `docs/methodology/project_context.md`.

---

## Project Title

**Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses**

---

## Current Repository Contents

The repository now reflects a **completed frozen system** plus **post-freeze validation and analysis**:

| Branch / artifact | Location | Status |
|-------------------|----------|--------|
| **Stanza pipeline** | `experiments/stanza/`, `src/parser/stanza_parser.py` | Primary evaluated system; frozen metrics |
| **UDPipe pipeline** | `experiments/udpipe/`, `src/parser/udpipe_parser.py` | Robustness branch; same frozen symbolic rules |
| **Final error analysis** | `outputs/error_analysis/`, `scripts/analysis/analyze_final_error_patterns.py` | Test/dev failure taxonomy and row-level outputs |
| **Paper-ready tables** | `outputs/error_analysis/paper_error_analysis_table_v2.md` | Compact six-row error summary for publication |
| **Reorganized structure** | `outputs/`, `experiments/`, `scripts/{data_prep,evaluation,analysis,experiments,legacy}/` | Central paths in `src/paths.py` |

---

## Frozen System (unchanged)

```text
Sentence → Parser (Stanza or UDPipe) → Mapper v1 → Verifier v1 → Correction v2.1 (H1 only) → Evaluation
```

- **Single accepted correction:** H1 (`nmod + में/पर → Adhikarana`)
- **Rejected:** DR1 dependency repair; passive auto-correction rules
- **Primary metric:** strict Karaka accuracy
- **Stanza test result:** 0.4850 (neural) → 0.5980 (correction v2.1)

---

## Post-Freeze Validation Summary

| Experiment | Purpose | Key finding |
|------------|---------|-------------|
| UDPipe dev/test | Parser robustness | Same rules; Adhikarana F1 stable; UDPipe strict accuracy slightly lower |
| Final error analysis | Explain remaining failures | Unsupported deprels and `को`/`से` ambiguity dominate |
| Repository cleanup | Maintainability | No regeneration of Stanza results |

---

## Documentation Map

| Document | Use when |
|----------|----------|
| `docs/final/final_project_reference.md` | Full implementation handbook |
| `docs/final/final_train_dev_results.md` | Train/dev metrics |
| `docs/final/final_test_results.md` | Held-out test + cross-parser comparison |
| `docs/final/project_update_after_freeze.md` | Everything added after freeze |
| `docs/final/project_timeline.md` | One-page chronology |
| `docs/paper/paper_outline.md` | Paper section plan |
| `docs/final/correction_layer_log.md` | H1 acceptance and DR1 rejection |

---

## What This Project Is Not

- Not a Hindi dependency parser improvement project.
- Not a UDPipe-tuned second symbolic system.
- Not an open-ended rule-mining pipeline after test freeze.

The contribution is **auditable Karaka extraction over neural parses**, with documented limits and evidence-based error analysis for future work.
