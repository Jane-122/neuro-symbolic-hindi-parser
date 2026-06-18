# Correction Layer Research Log

## 1. Purpose of the Correction Layer

The correction layer moves the project beyond simple UD-to-Karaka mapping. The goal is to test whether symbolic linguistic rules can correct or refine outputs produced from a neural dependency parser, rather than only restating UD labels as Karaka hypotheses.

This layer is deliberately small and conservative. It is added after mapper v1 and verifier v1 so that correction decisions can be evaluated separately from the earlier pipeline stages.

## 2. Current Correction Architecture

Current prediction flow:

1. Stanza produces neural UD-style dependency output.
2. `mapper_candidates` provides the neural-only UD-to-Karaka baseline.
3. Verifier v1 produces `final_candidates` using rule-based postposition evidence.
4. Correction Layer v2 produces `corrected_candidates` after verifier v1.

This separates three evaluation points:

- `neural_only = mapper_candidates`
- `verifier_v1 = final_candidates`
- `correction_v2 = corrected_candidates`

## 3. Correction Layer v2.1: H1

Rule H1:

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

Rule ID:

`H1_NMOD_LOCATIVE_ADHIKARANA`

Correction type:

`safe_override`

## 4. Motivation

Dev error analysis showed a repeated pattern where gold `Adhikarana` tokens were parsed by Stanza as `nmod` with locative markers, especially `में`.

Verifier v1 already handles `obl + में/पर` as Adhikarana, but it deliberately does not handle `nmod + में/पर`. In Stanza output, this creates missed locative Adhikarana predictions even when the postposition evidence is strong.

H1 extends the same locative evidence to a narrow `nmod` context. It does not attempt broad `nmod` correction.

## 5. Evidence

Observed evidence:

- Dev actionable pattern: `Adhikarana | nmod | में = 80` errors.
- H1 fired `121` times on dev.
- H1 fired `830` times on train.

These counts suggest the pattern is not isolated to a few examples.

## 6. Evaluation Results

Dev:


| System        | Candidate-set Accuracy | Strict Accuracy |
| ------------- | ---------------------- | --------------- |
| verifier_v1   | 0.7403                 | 0.5947          |
| correction_v2 | 0.7574                 | 0.6118          |


Train:


| System        | Candidate-set Accuracy | Strict Accuracy |
| ------------- | ---------------------- | --------------- |
| verifier_v1   | 0.7864                 | 0.6259          |
| correction_v2 | 0.8004                 | 0.6400          |


Correction v2 improves both candidate-set and strict accuracy on train and dev. These results are promising, but they are not final test results.

## 7. Per-Karaka Effect

H1 only improves `Adhikarana`, which is expected and desirable. It indicates that the rule has a localized effect rather than random side effects on unrelated Karakas.

Adhikarana dev F1:


| Mode          | verifier_v1 | correction_v2 |
| ------------- | ----------- | ------------- |
| candidate-set | 0.8881      | 0.9241        |
| strict        | 0.7897      | 0.8335        |


Other Karakas are unchanged by H1.

## 8. Decision

H1 is accepted and frozen as Correction Layer v2.1.

No other automatic correction rule is currently accepted.

Rationale:

- It is linguistically motivated by locative postpositions.
- It is conservative and narrowly scoped.
- It improves both train and dev.
- Its effect is localized to `Adhikarana`.
- It directly addresses a repeated Stanza parser pattern missed by verifier v1.

This is a correction rule, not a broad remapping of all `nmod` tokens.

It should be described as Karaka extraction and interpretation over neural dependency parses, not as direct improvement of UD dependency parsing.

## 9. Dependency Repair Experiment DR1

A direct dependency-label repair hypothesis was tested separately from Karaka correction.

Rule DR1:

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_deprel = "obl"
```

Rule ID:

`DR1_NMOD_LOCATIVE_TO_OBL`

Dev deprel-label evaluation against gold UD:

| Metric | Value |
|--------|-------|
| Original deprel accuracy | 0.9516 |
| After DR1 | 0.9485 |
| Repairs | 121 |
| Improved | 5 |
| Worsened | 113 |
| Unchanged correct | 0 |
| Unchanged wrong | 3 |

Conclusion:

DR1 improves Karaka interpretation indirectly in the H1 setting, but it harms UD dependency-label accuracy. Direct UD dependency-label repair is therefore **not accepted**. The project should not claim dependency parsing improvement from H1 or DR1.

## 10. Rules Not Yet Accepted

The following are diagnostic flags only:

- `possible_passive_karta`
- `possible_passive_karma`
- `se_ambiguous_requires_verb_context`

They are not accepted correction rules yet.

Reason:

Passive-related corrections and `से` disambiguation require more analysis before safe automatic correction. They likely need voice, verb-frame, or predicate-context evidence. Applying them now would risk overcorrecting.

## 11. Methodological Notes

- The test split must remain frozen.
- Current correction decisions are based on train/dev only.
- Candidate-set scoring and strict scoring should both be reported.
- Candidate-set scoring measures whether the gold label appears anywhere in a candidate set.
- Strict scoring requires exactly one predicted label and therefore penalizes ambiguity.
- Macro F1 and per-Karaka F1 are important because the Karaka label distribution is imbalanced.
- H1 should not be presented as final evidence of generalization until evaluated on the untouched test split.

Correction v2.1 currently corrects Karaka interpretation, not dependency tree heads or UD dependency labels.

