# Project Status Checkpoint 3

## Scope of This Checkpoint

This checkpoint summarizes implementation and research progress after the HDTB alignment phase. The finalized framing is **Neuro-Symbolic Karaka Extraction for Hindi from Neural Dependency Parses**.

The project uses neural dependency parses as input evidence, but it is not framed as direct improvement of UD dependency parsing. It focuses on extracting, verifying, and conservatively correcting Paninian Karaka labels using symbolic linguistic evidence.

The report uses generated artifacts from `outputs/`, `experiments/stanza/` (and subfolders), `src/`, and `scripts/`. It deliberately includes negative results and failed hypotheses. Test split results are not reported as final evaluation because test is being kept frozen.

## 1. Current Pipeline Architecture

The current pipeline has four conceptual stages:

1. **Stanza parser output**
   - Stanza produces token-level UD-style parses.
   - Current pipeline rows store `sent_id`, `sentence_text`, `token_form`, `deprel`, and `case_marker`.

2. **Mapper v1**
   - Implemented in `src/mapper/simple_mapper.py`.
   - Produces `mapper_candidates`.
   - This is the neural-only Karaka baseline used in evaluation.

3. **Verifier v1**
   - Implemented in `src/verifier/simple_verifier.py`.
   - Applies symbolic postposition rules over Stanza or gold UD rows.
   - Produces `final_candidates`.
   - Main rules include `nsubj + ने -> Kartā`, `obl + में/पर -> Adhikaraṇa`, `obl + से -> Karaṇa|Apādāna`, and `obj/iobj + को -> Karma|Sampradāna`.

4. **Correction Layer v2.1**
   - Implemented in `src/pipeline/correction_layer_v2.py`.
   - Produces `corrected_candidates`.
   - Frozen with only one accepted automatic correction rule, H1.

The important evaluation columns are:

| System | Candidate column |
|--------|------------------|
| neural_only | `mapper_candidates` |
| verifier_v1 | `final_candidates` |
| correction_v2 | `corrected_candidates` |

## 2. HDTB to UD Alignment

The project aligned UD Hindi-HDTB sentences to original HDTB `.dat` sentences under `data/raw/news_articles_and_heritage/`.

Alignment uses:

- Unicode NFC normalization.
- Nukta normalization.
- `NULL` token removal.
- Punctuation and quote-spacing cleanup.
- Exact normalized match first.
- Fuzzy `SequenceMatcher` matching only for high-confidence fallback.

Final v2 alignment summary:

| UD split | HDTB split | UD sentences | HDTB sentences | Exact match | High confidence >= 0.95 | High confidence >= 0.98 |
|----------|------------|--------------|----------------|-------------|--------------------------|--------------------------|
| train | Training | 13,306 | 14,089 | 13,302 | 13,303 | 13,302 |
| dev | Development | 1,659 | 1,743 | 1,659 | 1,659 | 1,659 |
| test | Testing | 1,684 | 1,804 | 1,684 | 1,684 | 1,684 |

Final accepted aligned corpus:

- Train has 4 unmatched UD sentences.
- Dev has full alignment.
- Test has full alignment.

The 4 unmatched train sentences are segmentation or text-mismatch cases, not evidence that the alignment method broadly failed. One near miss, `train-s852B`, had a best similarity score of `0.9592`, below the accepted `0.98` threshold.

## 3. Gold Karaka Extraction

Gold Karaka labels are extracted from aligned raw HDTB `.dat` files using:

- `hdtb_split`
- `hdtb_file`
- `hdtb_sentence_index`
- raw HDTB token rows

The extracted columns are:

`split, ud_sent_id, hdtb_file, hdtb_sentence_index, token_id, token, head, paninian_label, gold_karaka`

Core Paninian label mapping:

| HDTB label | Gold Karaka |
|------------|-------------|
| k1 | Karta |
| k2 | Karma |
| k3 | Karana |
| k4 | Sampradana |
| k5 | Apadana |
| k7 | Adhikarana |
| k7p | Adhikarana |

Gold Karaka rows:

| Split | Gold Karaka rows |
|-------|------------------|
| train | 47,378 |
| dev | 5,902 |
| test | 5,946 |

Important limitation: this is a restricted gold label set. HDTB contains many additional labels and variants, including `k1s`, `k2p`, `k7t`, `ras-k1`, `nmod__k1inv`, and others. These are not yet mapped into the gold Karaka evaluation.

## 4. Token Matching Audit

Evaluation matches HDTB gold tokens to Stanza pipeline rows using:

`split + sent_id + normalized token text + occurrence order`

Dev token-matching audit:

| Quantity | Count |
|----------|-------|
| Total gold rows | 5,902 |
| Matched gold rows | 5,880 |
| Unmatched gold rows | 22 |
| Match percentage | 99.63% |
| Extra pipeline rows with meaningful candidates | 2,393 |

The high match rate supports the dev evaluation, but the extra meaningful pipeline rows are methodologically important. Many Stanza predictions occur on tokens outside the restricted gold Karaka set, so precision should be interpreted with care.

## 5. Evaluation Methodology Evolution

The project now reports two evaluation modes.

### Candidate-Set Metrics

Candidate-set scoring counts a prediction as correct if:

`gold_karaka` is anywhere in the predicted candidate set.

This is appropriate when the system is allowed to return ambiguity, but it is generous.

Example:

`Karma|Sampradana` is correct if the gold label is `Karma`.

### Strict Metrics

Strict scoring counts a prediction as correct only if:

- the candidate set contains exactly one label, and
- that label equals the gold Karaka.

Empty predictions and multi-label predictions are counted incorrect.

Strict scoring is harsher but more appropriate for measuring whether the system has resolved ambiguity.

Both metrics are now reported because they answer different research questions.

## 6. Neural-Only vs Verifier v1 Results

Dev results before Correction Layer v2.1:

| System | Mode | Accuracy | Macro F1 |
|--------|------|----------|----------|
| neural_only | candidate_set | 0.7369 | 0.5599 |
| verifier_v1 | candidate_set | 0.7403 | 0.5724 |
| neural_only | strict | 0.4909 | 0.3877 |
| verifier_v1 | strict | 0.5947 | 0.4153 |

Interpretation:

- Verifier v1 gives only a small candidate-set accuracy gain over neural-only.
- Strict accuracy improves more strongly because verifier v1 turns some broad mapper hypotheses into single confirmed labels.
- The result is useful, but it is not enough to claim a strong overall performance improvement from verifier v1 alone.

## 7. Error Analysis Findings

Before H1, actionable dev error analysis showed repeated patterns such as:

- `Adhikarana | nmod | में = 80`
- `Karta | obj | blank = 53`
- `Karma | nsubj | blank = 50`
- `Karma | obl | से = 25`

The most actionable and linguistically conservative pattern was the first one: locative `nmod` with `में/पर`.

This motivated H1.

## 8. Correction Layer v2.1

Correction Layer v2.1 is frozen with one accepted automatic rule.

Rule H1:

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_candidates = "Adhikarana"
```

Rule ID:

`H1_NMOD_LOCATIVE_ADHIKARANA`

Correction type:

`safe_override`

### Motivation

Verifier v1 handled:

`obl + में/पर -> Adhikarana`

But Stanza often produced:

`nmod + में/पर`

for tokens whose HDTB gold Karaka was `Adhikarana`. H1 applies the same locative postposition evidence to a narrow Stanza `nmod` pattern.

### H1 Firing Counts

| Split | H1 firings |
|-------|------------|
| dev | 121 |
| train | 830 |

### Train and Dev Validation

Dev:

| System | Mode | Accuracy | Macro F1 |
|--------|------|----------|----------|
| verifier_v1 | candidate_set | 0.7403 | 0.5724 |
| correction_v2 | candidate_set | 0.7574 | 0.5784 |
| verifier_v1 | strict | 0.5947 | 0.4153 |
| correction_v2 | strict | 0.6118 | 0.4226 |

Train:

| System | Mode | Accuracy | Macro F1 |
|--------|------|----------|----------|
| verifier_v1 | candidate_set | 0.7864 | 0.6023 |
| correction_v2 | candidate_set | 0.8004 | 0.6073 |
| verifier_v1 | strict | 0.6259 | 0.4451 |
| correction_v2 | strict | 0.6400 | 0.4513 |

Interpretation:

- H1 improves both train and dev.
- The effect is consistent across candidate-set and strict scoring.
- Because the rule was motivated from dev error analysis, it must not be treated as final evidence of generalization until evaluated on frozen test.

## 9. Per-Karaka Impact Analysis

H1 affects only `Adhikarana`, which is expected and methodologically useful.

Dev Adhikarana F1:

| Mode | neural_only | verifier_v1 | correction_v2 |
|------|-------------|-------------|---------------|
| candidate_set | 0.8491 | 0.8881 | 0.9241 |
| strict | 0.0000 | 0.7897 | 0.8335 |

Dev delta for Adhikarana:

| Mode | correction_v2 - verifier_v1 | correction_v2 - neural_only |
|------|-----------------------------|-----------------------------|
| candidate_set | +0.0360 | +0.0750 |
| strict | +0.0438 | +0.8335 |

Other Karakas are unchanged by H1:

- `Karta`
- `Karma`
- `Karana`
- `Sampradana`
- `Apadana`

This localized effect is a positive result. It suggests H1 is targeted rather than randomly changing unrelated classes.

## 10. Passive Diagnostic Investigation

The project investigated two diagnostic flags:

- `possible_passive_karta`
- `possible_passive_karma`

These are diagnostics only. No passive correction rule has been accepted.

### Statistical Diagnostic Summary

`possible_passive_karta`:

- Total flagged rows: 1,546
- Matched gold rows: 1,004
- Dominant gold label: `Karma = 900`
- Estimated conversion to dominant label would make 900 rows correct and 104 rows incorrect.
- Script-level conclusion: `PROMISING`

`possible_passive_karma`:

- Total flagged rows: 2,109
- Matched gold rows: 1,886
- Dominant gold label: `Karta = 1,812`
- Estimated conversion to dominant label would make 1,812 rows correct and 74 rows incorrect.
- Script-level conclusion: `SAFE`

### Manual Example Review

Manual review changed the interpretation.

First 50 `possible_passive_karta` examples:

- About 18 of 50 appeared genuinely passive.
- About 14 of 50 contained explicit passive auxiliaries.
- Some real opportunities exist, but many rows are ordinary `obj -> Karma` cases already handled correctly.
- Manual conclusion: `NEEDS REFINEMENT`.

First 50 `possible_passive_karma` examples:

- Only about 2 to 4 of 50 appeared plausibly passive.
- About 1 of 50 contained an explicit listed passive auxiliary.
- Most were ordinary `nsubj -> Karta` cases already predicted correctly.
- Manual conclusion: `FALSE LEAD` as currently defined for passive correction.

Interpretation:

The passive diagnostics are too broad. Passive correction remains worth studying, but future rules must require stronger voice-sensitive evidence, not just `obj` or `nsubj`.

## 11. Dependency Repair Experiment

A separate dependency-label repair prototype was tested:

Rule DR1:

```python
if deprel == "nmod" and case_marker in {"में", "पर"}:
    corrected_deprel = "obl"
```

Rule ID:

`DR1_NMOD_LOCATIVE_TO_OBL`

Important constraint:

- heads are not changed
- token order is not changed
- original `deprel` is not overwritten

Dev dependency-label evaluation against gold UD:

| Metric | Value |
|--------|-------|
| Matched tokens | 35,217 |
| Unmatched gold tokens | 0 |
| Original deprel accuracy | 0.9516 |
| Repaired deprel accuracy | 0.9485 |
| DR1 repairs | 121 |
| DR1 improved | 5 |
| DR1 worsened | 113 |
| DR1 unchanged correct | 0 |
| DR1 unchanged wrong | 3 |

Interpretation:

DR1 is a failed dependency-repair hypothesis. It helps Karaka correction because HDTB gold Karaka treats many `nmod + में/पर` rows as Adhikarana, but it worsens UD dependency-label accuracy because most of those tokens are gold `nmod` in UD, not gold `obl`.

This is an important negative result. H1 should be framed as Karaka correction, not dependency-label repair. Direct UD repair is not accepted in the current project framing.

## 12. Remaining Error Analysis After H1

After H1, remaining dev errors using `corrected_candidates`:

Total remaining errors: 1,432

Remaining errors by gold Karaka:

| Gold Karaka | Errors |
|-------------|--------|
| Karma | 758 |
| Karta | 388 |
| Adhikarana | 180 |
| Sampradana | 55 |
| Apadana | 37 |
| Karana | 14 |

Top remaining error patterns:

| Pattern | Count |
|---------|-------|
| Karma \| mark \| blank \| NO_PREDICTION | 446 |
| Karma \| compound \| blank \| NO_PREDICTION | 112 |
| Karta \| cc \| blank \| NO_PREDICTION | 78 |
| Karta \| root \| blank \| NO_PREDICTION | 76 |
| Adhikarana \| cc \| blank \| NO_PREDICTION | 57 |
| Karta \| obj \| blank \| Karma | 53 |
| Karma \| cc \| blank \| NO_PREDICTION | 51 |
| Karma \| nsubj \| blank \| Karta | 50 |
| Karta \| compound \| blank \| NO_PREDICTION | 33 |
| Adhikarana \| nmod \| blank \| NO_PREDICTION | 27 |

Interpretation:

The remaining error mass is dominated by `Karma` and `Karta`, but many high-count patterns involve `mark`, `compound`, `cc`, and `root`. These are not immediately clean Karaka correction rules. They may reflect HDTB-vs-UD tokenization, annotation differences, or gold-label scope differences.

The next clean correction target is not obviously `Karana`, `Apadana`, or `Sampradana`, despite their lower F1 values. Their supports are much smaller.

## 13. Methodological Risks

### Dev Has Been Used for Discovery

H1 was motivated from dev error analysis. This is acceptable for iterative research, but it means dev should no longer be treated as a clean final evaluation split.

### Test Must Remain Frozen

The test split has been aligned and gold Karaka labels exist, but it should not be used for exploratory analysis or rule design. It must remain frozen so the project can later report one honest held-out result after correction rules are fixed.

### Candidate-Set Metrics Are Generous

Candidate-set scoring rewards any prediction set containing the gold label. This is useful for measuring whether the system preserves the correct candidate, but it overstates resolved accuracy.

Strict metrics must be reported alongside candidate-set metrics.

### Gold Label Space Is Partial

Only `k1`, `k2`, `k3`, `k4`, `k5`, `k7`, and `k7p` are currently mapped to gold Karaka labels. Other HDTB relation labels are not yet included.

### Token Matching Is Good but Not Perfect

Dev token matching is 99.63%, but 22 gold rows remain unmatched, and 2,393 meaningful pipeline candidate rows are outside the restricted gold Karaka evaluation.

### Dependency Repair and Karaka Correction Are Different

DR1 showed that improving Karaka labels can conflict with UD deprel label accuracy. The project must not conflate Karaka correction with dependency parsing repair.

## 14. Current Project Interpretation

The project has moved from a simple mapping/verifier prototype to a small evaluated neuro-symbolic Karaka extraction and correction system.

The strongest positive result so far is H1:

- It is linguistically motivated.
- It improves train and dev.
- It has a localized per-Karaka effect.
- It does not affect unrelated Karakas.

The strongest negative result is DR1:

- Recasting `nmod + में/पर` as UD `obl` worsens deprel accuracy.
- Therefore, H1 should be interpreted as semantic/Karaka correction over neural dependency parses, not syntactic dependency repair.

The passive diagnostics are mixed:

- broad statistical summaries looked promising
- manual review showed the definitions are too broad
- no passive correction rule should be accepted yet

## 15. Open Research Questions

1. Can passive correction be narrowed using explicit auxiliary and predicate-context evidence?
2. Are remaining `Karma | mark` and `Karma | compound` errors true Karaka prediction failures or artifacts of token/gold-label mismatch?
3. Should the gold Karaka label set be expanded to include variants such as `k1s`, `k2p`, and `k7t`?
4. Can correction rules be learned or selected using train only, then validated on dev and finally tested once?
5. How should ambiguous predictions be evaluated in the final report: as candidate recall, strict accuracy, or both?
6. Can a future correction layer improve Karaka outputs while keeping dependency parsing claims separate?
7. Should the system explicitly separate semantic-role correction from syntactic dependency repair in architecture diagrams and terminology?

## 16. Recommended Next Steps

1. **Freeze H1 as Correction Layer v2.1.**
   - Reason: it has a clear motivation and consistent train/dev gains.
   - Expected impact: stable baseline for future correction experiments.

2. **Do not accept passive rules yet.**
   - Reason: manual review found broad diagnostics and many false positives.
   - Expected impact: prevents overcorrection.

3. **Refine passive diagnostics using predicate-context evidence.**
   - Reason: passive morphology must be attached to the relevant predicate, not merely present in the sentence.
   - Expected impact: may produce a safer future H2.

4. **Investigate high-count remaining errors involving `mark`, `compound`, and `cc`.**
   - Reason: these dominate remaining errors but may not be real correction targets.
   - Expected impact: distinguishes true model failure from evaluation/artifact issues.

5. **Keep dependency repair separate from Karaka correction.**
   - Reason: DR1 showed negative deprel accuracy impact.
   - Expected impact: improves methodological clarity.

6. **Prepare a final frozen test evaluation protocol.**
   - Reason: test must be used once after rule selection.
   - Expected impact: gives credible final generalization evidence.

7. **Update documentation to reflect the current architecture.**
   - Reason: older docs understate gold Karaka extraction and correction work.
   - Expected impact: improves handover and report readiness.

## What We Know With High Confidence

- UD-HDTB to raw HDTB sentence alignment is strong for dev and test.
- HDTB-derived gold Karaka labels can be extracted reproducibly for core labels.
- Dev token matching is high at 99.63%, though not perfect.
- Candidate-set metrics are more generous than strict metrics.
- Verifier v1 gives only modest improvement over neural-only in candidate-set accuracy.
- Correction Layer v2.1 H1 improves train and dev Karaka evaluation.
- H1 specifically improves Adhikarana and leaves other Karakas unchanged.
- Passive diagnostics are too broad in their current form.
- Dependency-label repair DR1 worsens UD deprel accuracy and should not be claimed as a dependency parsing improvement.
- The symbolic layer improves Karaka extraction and interpretation, not UD dependency parsing itself.
- Test should remain frozen until rules are finalized.

## What Remains Uncertain

- Whether H1 generalizes to frozen test.
- Whether passive correction can be made safe with better voice-sensitive conditions.
- Whether high-count remaining errors on `mark`, `compound`, and `cc` reflect true semantic-role errors or annotation/token-matching artifacts.
- Whether the restricted gold label mapping is sufficient for a final report.
- Whether expanding gold labels to include variants such as `k1s`, `k2p`, and `k7t` will change conclusions.
- Whether future correction layers can improve strict macro F1 without hurting precision on low-support Karakas.
- How best to frame the final contribution within Karaka extraction: correction, neuro-symbolic verification, diagnostic evaluation, or HDTB gold-label recovery.
