# Project Context

## Project Title

Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses

---

## Project Type

Research Internship Project

Duration: Approximately 5–6 weeks

Domain:
- Natural Language Processing (NLP)
- Dependency Parsing as input evidence
- Computational Linguistics
- Neuro-Symbolic AI
- Paninian Grammar

---

## Project Motivation

Modern neural dependency parsers perform well on many syntactic tasks but often struggle with linguistically meaningful semantic roles, especially in morphologically rich and free word order languages such as Hindi.

Paninian grammar provides a well-established framework of Karaka relations that capture semantic roles such as agent, object, instrument, recipient, source, and location.

This project investigates whether simple symbolic Paninian rules can be used alongside neural dependency parser outputs to improve **Karaka extraction and interpretation**. The project is not framed as direct improvement of UD dependency parsing.

---

## Research Question

Can Paninian Karaka-based symbolic rules improve Karaka extraction from neural Hindi dependency parses?

---

## Main Contribution

This project should **not** become only a UD-to-Karaka mapping project.

The main contribution is a **Paninian rule-based verifier and Karaka correction layer** operating over UD-style dependency outputs. The system inspects syntactic analyses, applies symbolic evidence, and returns structured Karaka decisions, including cases where no confident Karaka assignment is possible.

The UD-to-Karaka mapping (`docs/methodology/ud_to_karaka_mapping_v1.md`) is a **starting hypothesis only**. It supplies default guesses for the verifier to test, confirm, correct, or reject. Mapping alone is not the research output.

---

## Project Objective

Build a small neuro-symbolic pipeline that:

1. Uses dependency parses from a Hindi UD-based parser or dataset.
2. Applies a conservative UD-to-Karaka mapping as an initial hypothesis (not as final truth).
3. Runs a Paninian rule-based verifier/corrector over those Karaka hypotheses.
4. Produces hybrid outputs with explicit verifier decisions (`confirmed`, `corrected`, `ambiguous`, `no_decision`).
5. Evaluates where symbolic reasoning helps Karaka extraction, where it fails, and where it correctly withholds judgment.

---

## Verifier Decision Types

Every verifier judgment must use one of four decision types:

| Decision Type | Meaning |
|---------------|---------|
| `confirmed` | Symbolic evidence supports the current Karaka hypothesis with sufficient confidence. |
| `corrected` | Symbolic evidence suggests a different Karaka than the initial mapping hypothesis. |
| `ambiguous` | Multiple Karakas remain plausible; the verifier must not force a single label. |
| `no_decision` | Insufficient evidence to confirm, correct, or disambiguate. |

The verifier should prefer `ambiguous` or `no_decision` over incorrect forced assignments.

---

## Verifier Implementation Principles

- Keep the UD-to-Karaka mapping **conservative**.
- Do **not** force ambiguous cases into one Karaka.
- Treat `case` markers as **evidence**, not Karaka labels.
- Treat **`obl` + postposition** as the main focus area for rule design.
- Use **`ने`**, **`को`**, **`से`**, **`में`**, and **`पर`** as primary evidence signals (validated in `notebooks/exploration/02_postposition_analysis.ipynb`).
- Do **not** implement neural model training.
- Do **not** expand beyond a **small verifier prototype** yet.

Rule definitions for Version 1 are in `docs/methodology/rule_specification_v1.md`.

---

## Current Correction-Layer Framing

Correction Layer v2.1 is frozen with only one accepted automatic correction rule:

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

Rule ID: `H1_NMOD_LOCATIVE_ADHIKARANA`

This is a Karaka interpretation correction, not a UD dependency parsing repair. A direct dependency-label repair experiment, DR1 (`nmod + में/पर -> obl`), reduced dev deprel accuracy from `95.16%` to `94.85%` and is therefore not accepted.

The test split must remain frozen until final held-out evaluation.

---

## Scope

### Included

- Universal Dependencies (UD)
- Hindi-HDTB treebank
- Conservative UD-to-Karaka mapping (as verifier input only)
- Paninian rule-based verifier and Karaka correction layer (main contribution)
- Hybrid neuro-symbolic pipeline with explicit decision types
- Evaluation and error analysis

### Not Included

- Building a dependency parser from scratch
- Claiming direct improvement of UD dependency parsing
- Training large language models
- Training large transformer models
- Creating a new annotation scheme
- Full treebank conversion research

The project focuses on Karaka verification and correction rather than parser construction or dependency-tree repair.

---

## Linguistic Background

### Universal Dependencies

Important dependency labels:

- root
- nsubj
- obj
- iobj
- obl
- case
- amod
- advmod
- compound
- punct

### Paninian Karaka Roles

Important Karakas:

- Kartā
- Karma
- Karaṇa
- Sampradāna
- Apādāna
- Adhikaraṇa

---

## Initial Mapping Assumptions

The following mappings are only starting hypotheses and may change after analysis.

| UD Label | Possible Karaka |
|-----------|----------------|
| nsubj | Kartā |
| obj | Karma |
| iobj | Sampradāna |
| obl | Context Dependent |
| case | Linguistic clue, not a Karaka |

---

## Important Hindi Postpositions

Symbolic rules will likely use these signals:

| Postposition | Possible Karaka Signal |
|--------------|-----------------------|
| ने | Kartā |
| को | Karma / Sampradāna |
| से | Karaṇa / Apādāna |
| में | Adhikaraṇa |
| पर | Adhikaraṇa |

These rules are hypotheses and should be validated against data.

---

## Expected System Pipeline

Input Hindi Sentence

↓

Universal Dependencies Parse

↓

UD Label Analysis

↓

Conservative UD → Karaka Mapping *(starting hypothesis)*

↓

Paninian Rule-Based Karaka Verifier / Corrector

↓

Verifier Decisions (`confirmed` / `corrected` / `ambiguous` / `no_decision`)

↓

Hybrid Neuro-Symbolic Karaka Output

↓

Evaluation

↓

Error Analysis

---

## Research Philosophy

The goal is not to maximize complexity.

The goal is to create a small, understandable, reproducible, and well-documented research prototype.

Priorities:

1. Correctness
2. Interpretability
3. Reproducibility
4. Simplicity
5. Performance

---

## Engineering Principles

### Version Control

Use Git and GitHub throughout the project.

Commit frequently.

Document meaningful changes.

---

### Reproducibility

Save intermediate outputs.

Avoid hidden state.

Keep experiments reproducible.

---

### Modular Design

Keep the following stages separate:

- Data loading
- Data processing
- Mapping
- Verification
- Evaluation
- Visualization

---

### Experiment Tracking

Important experiments should record:

- Date
- Configuration
- Rules enabled
- Dataset subset
- Metrics

---

## Expected Deliverables

1. Dataset exploration and analysis.
2. Conservative UD-to-Karaka mapping (hypothesis document, not final ontology).
3. Rule specification and rule-based Karaka verifier/corrector (**primary deliverable**).
4. Hybrid neuro-symbolic pipeline with explicit verifier decisions.
5. Evaluation results (including ambiguous and no-decision cases).
6. Error analysis.
7. Final report and presentation.

---

## Documentation Style Rules

The following conventions apply to project documentation, notes, reports, markdown files, README files, prompts, and research summaries:

1. Do not use em dashes.
2. Do not use double-hyphen stylistic breaks.
3. Prefer normal sentence structure.
4. Use commas, parentheses, colons, semicolons, or separate sentences instead.
5. Keep writing academic, professional, and natural.
6. Avoid AI-style phrasing and overly dramatic transitions.
7. Keep explanations clear, direct, and concise.
8. When documenting research findings, distinguish clearly between observations, hypotheses, conclusions, and future work.
9. Do not overstate results. Use cautious scientific language when appropriate.

---

## Working Style Instructions

When helping with this repository:

- Work incrementally.
- Do not jump ahead to future phases.
- Do not introduce unnecessary complexity.
- Explain reasoning before major changes.
- Prefer simple and readable code.
- Focus on research goals rather than software engineering abstractions.
- Assume the user is learning both NLP and research workflows while implementing the project.

At any stage, prioritize understanding and correctness over optimization.