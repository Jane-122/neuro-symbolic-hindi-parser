# Paper Outline

> Canonical copy: `docs/paper/paper_assets/paper_outline.md` (kept in sync).

## Tentative Title

**Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses**

Alternative subtitle (optional): *A Conservative Rule-Based Layer over Stanza UD Output*

## Abstract Bullet Points

- Hindi semantic role labeling can be framed as Paninian Karaka extraction over neural dependency parses rather than as direct UD parsing repair.
- We align Hindi-HDTB UD sentences with original HDTB annotations and extract a restricted gold Karaka label set for evaluation.
- A frozen neuro-symbolic pipeline combines Stanza parsing, Mapper v1, Verifier v1, and Correction Layer v2.1.
- Verifier v1 provides the largest strict accuracy gain by applying postposition-based disambiguation over Stanza output.
- Correction v2.1 adds one accepted rule, H1, for locative `nmod + में/पर` cases mapped to Adhikarana.
- On held-out test, strict Karaka accuracy improves from 0.4850 (neural only) to 0.5980 (correction v2.1).
- A dependency-label repair experiment (DR1) is reported as a negative result: Karaka-oriented label changes can harm UD deprel accuracy.
- Passive-voice and `से` ambiguity diagnostics were investigated but not promoted to automatic correction rules.

## Section Outline

### 1. Introduction

- Motivate Karaka extraction as a semantic interpretation task over syntactic parses.
- State the gap between UD dependency labels and Paninian semantic roles in Hindi.
- Introduce the neuro-symbolic design: neural parser for structure, symbolic rules for Karaka hypotheses and verification.
- Clarify project scope: improve Karaka extraction, not UD dependency parsing accuracy.
- Summarize contributions:
  - HDTB to UD alignment and gold Karaka extraction pipeline.
  - Frozen Mapper v1, Verifier v1, and Correction v2.1 system.
  - Train/dev development with single held-out test evaluation.
  - Conservative correction rule H1 with localized Adhikarana gains.
  - Cross-parser robustness validation on UDPipe (same frozen rules).
  - Negative result on dependency repair DR1.
- Preview main result: strict test accuracy 0.4850 to 0.5980.

### 2. Related Work

- Universal Dependencies and Hindi treebanks (Hindi-HDTB).
- Paninian grammar and Karaka theory in computational linguistics.
- Hindi semantic role labeling and dependency-based role mapping.
- Neuro-symbolic NLP: combining neural parsers with symbolic post-processing.
- Rule-based verification and correction over parser output.
- Position this work as Karaka extraction over neural parses, distinct from parser retraining or UD label repair.

### 3. Dataset and Alignment

- Describe Hindi-HDTB UD splits (train, dev, test) and original HDTB `.dat` files.
- Explain why alignment between UD and HDTB is required for gold Karaka labels.
- Document normalization steps: Unicode NFC, nukta handling, punctuation cleanup, `NULL` token removal.
- Describe exact match and high-confidence fuzzy alignment (`SequenceMatcher`).
- Report alignment statistics by split.
- Explain gold Karaka label extraction and restricted label mapping (`k1` to `Karta`, `k2` to `Karma`, etc.).
- Note excluded HDTB labels and evaluation scope limitation.
- Report gold row counts per split and token-matching protocol for evaluation.

### 4. Methodology

- Present pipeline stages:
  - Neural Hindi parser (Stanza primary; UDPipe for robustness validation).
  - Case marker extraction from dependency structure.
  - Mapper v1: UD deprel to Karaka candidate mapping.
  - Verifier v1: postposition-based candidate refinement.
  - Correction Layer v2.1: conservative override layer.
- Define frozen systems evaluated:
  - Neural only (`mapper_candidates`).
  - Verifier v1 (`final_candidates`).
  - Correction v2.1 (`corrected_candidates`).
- Specify accepted rule H1:
  - `deprel == "nmod"` and `case_marker in {"में", "पर"}` implies `Adhikarana`.
- Mention diagnostic flags that were not activated as corrections:
  - `possible_passive_karta`
  - `possible_passive_karma`
  - `se_ambiguous_requires_verb_context`
- Briefly note rejected DR1 dependency repair for contrast in later sections.

### 5. Experimental Setup

- Describe evaluation splits and frozen test policy (test run once after rule freeze).
- Define token matching key: split, sentence id, normalized token, occurrence order.
- Define scoring modes:
  - Candidate-set (secondary).
  - Strict (primary): exactly one predicted Karaka matching gold.
- List metrics: accuracy, macro precision/recall/F1, per-Karaka F1.
- Identify baselines and ablation stages: neural only, verifier v1, correction v2.1.
- State that no parser retraining, threshold tuning, or post-test rule changes were performed.
- Reference output artifacts and reproducibility scripts without overclaiming full reproducibility of large result files.

### 6. Results

- Report overall train, dev, and test results for all three systems.
- Emphasize strict accuracy progression across splits.
- Highlight Verifier v1 as the main strict disambiguation gain.
- Report Correction v2.1 incremental gains over Verifier v1.
- Present held-out test summary: strict accuracy 0.4850 to 0.5980.
- Report H1 firing counts and Adhikarana-specific F1 improvements on train, dev, and test.
- Include per-Karaka results, noting unchanged classes under H1 and persistent weaknesses (Karana, Apadana, strict Karma/Sampradana).
- Report token matching coverage (matched vs unmatched gold rows).

#### 6.1 Cross-Parser Robustness

- Report UDPipe dev/test evaluation under the **same frozen symbolic stack** (no rule changes).
- Compare Stanza vs UDPipe on: token matching, strict/candidate accuracy, Adhikarana F1, H1 firing counts.
- Emphasize purpose: parser robustness validation, not UDPipe-specific tuning.
- Key finding: Adhikarana/H1 behavior stable across parsers; overall strict accuracy lower for UDPipe.

### 7. Error Analysis and Negative Results

- Present compact six-row error summary table (`paper_error_analysis_table_v2.md`).
- Failure taxonomy: strict correct, candidate-correct strict fail, no prediction, unmatched gold.
- Top recurring categories: unsupported UD deprels, `को` ambiguity, `से` ambiguity, residual Adhikarana, Karta recall gaps.
- Note: hard wrong-label cases more frequent for UDPipe but not treated as a separate linguistic category.
- Summarize dev error mining patterns that motivated H1 (`Adhikarana | nmod | में`).
- Explain why passive diagnostics were not accepted as correction rules.
- Report DR1 negative result:
  - Rule: `nmod + में/पर -> obl`.
  - Dev deprel accuracy decreased from 95.16% to 94.85%.
  - 121 repairs: 5 improved, 113 worsened relative to gold UD deprel.
- Argue that Karaka correction and UD deprel repair are distinct objectives.
- Discuss unresolved `से` ambiguity and passive constructions as open error classes.
- Note classes with low or zero strict F1 despite nonzero candidate-set performance.

### 8. Limitations

- Restricted gold Karaka label set excludes many HDTB Paninian labels.
- Token matching misses a small fraction of gold rows (~0.37%).
- Mapper and Verifier v1 are rule-based and coverage-limited.
- Stanza parse errors propagate to Karaka predictions.
- Single accepted correction rule; no learned reranker or context model.
- Class imbalance affects macro F1 interpretation.
- Results are specific to news/heritage HDTB domain and evaluated parsers (Stanza primary, UDPipe robustness).
- Strict scoring penalizes legitimate ambiguity in mapper output.

### 9. Conclusion

- Restate problem framing: neuro-symbolic Karaka extraction over neural dependency parses.
- Summarize empirical finding: symbolic verification plus one conservative correction improves strict Karaka accuracy on held-out test.
- Emphasize localized Adhikarana gains from H1 and generalization to test.
- Acknowledge negative DR1 result and uninvestigated passive/`से` cases as boundaries of current system.
- Suggest future work: richer Karaka inventory, context-sensitive rules, learned disambiguation, without conflating Karaka correction with UD repair.

## Suggested Paper Emphasis

- Primary claim: Karaka extraction improvement over Stanza parses.
- Primary metric: strict accuracy and strict macro F1.
- Secondary metric: candidate-set scores for ambiguity-aware analysis.
- Essential negative result: DR1 dependency repair failure.
- Essential ablation path: neural only, verifier v1, correction v2.1.
- Cross-parser robustness: UDPipe branch with frozen rules (Section 6.1).
- Expanded error analysis: failure taxonomy and paper table (Section 7).
