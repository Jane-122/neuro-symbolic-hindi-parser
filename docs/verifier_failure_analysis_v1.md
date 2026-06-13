# Verifier Failure Analysis (Version 1)

**Status:** Analysis notes from manual inspection of verifier batch outputs  
**Source notebook:** `notebooks/06_verifier_failure_analysis.ipynb`  
**Input data:** `results/verifier_batch_meaningful.csv` (36 rows), `results/verifier_batch_all.csv` (779 rows)  
**Rule reference:** `docs/rule_specification_v1.md` (unchanged)

This document records failure-mode and gap analysis for v1 verifier outputs. It is analysis only. No verifier rules, mapper, Stanza integration, or HTDB integration is modified here.

Assessments below are based on sentence context visible in the batch CSV. They are not validated against gold Karaka annotations.

---

## 1. Scope of This Analysis

| Source | Rows / tokens | Role in this document |
|--------|---------------|----------------------|
| Meaningful CSV | 36 rows | Manual strength and ambiguity classification |
| Full batch CSV | 779 tokens | Uncovered `(deprel, case_marker)` patterns |
| Bare `nsubj` in batch | 37 tokens | Coverage gap (no `ने` case child) |

Batch configuration: first 50 sentences from `hi_hdtb-ud-train.conllu` via `run_verifier_batch.py`.

---

## 2. Strongest Confirmed Examples

**Observation:** 19 confirmed rows total. Manual strength labels: **10 strong**, **2 moderate**, **7 weak**.

### Strong confirmed (10 rows)

These rows show clear agent or spatial/surface locus readings in context.

| sent_id | Token | Rule | Reading in context |
|---------|-------|------|-------------------|
| train-s2 | शाहजेहन | R1 | Agent of बनवाया (built) |
| train-s11 | कोरिया | R1 | Agent of डिजाइन किया (designed) |
| train-s50 | राजाओं | R1 | Agent of बनवाकर (had built) |
| train-s4 | हॉल | R2 | Location: prayer hall |
| train-s12 | क्षेत्र | R2 | Location: large area |
| train-s19 | संग्रहालय | R2 | Location: museum venue |
| train-s32 | चौक | R2 | Location: square |
| train-s33 | गलियों | R2 | Location: narrow lanes |
| train-s36 | झील | R2 | Location: lake (boating) |
| train-s15 | हिल्स | R3 | Surface location: on hills |

**Example (R1, strong):** *इसे नवाब शाहजेहन ने बनवाया था ।* (token: शाहजेहन)

**Hypothesis:** R1 and clear spatial R2/R3 hits are the strongest current verifier behavior in this batch.

### Moderate confirmed (2 rows)

| sent_id | Token | Rule | Note |
|---------|-------|------|------|
| train-s46 | शहर | R2 | Locative frame, but temporal/narrative context |
| train-s46 | पत्थरों | R2 | Metaphorical " trapped in stone" reading |

### Weak confirmed (7 rows, all R2)

These rows receive `confirmed` Adhikaraṇa, but the में reading is extent, time, manner, or abstract rather than core spatial location.

| sent_id | Token | Subtype suggested by context |
|---------|-------|------------------------------|
| train-s15 | एकड़ | Spatial extent (200 acres) |
| train-s26 | हैक्टेयर | Spatial extent (445 hectares) |
| train-s45 | वर्ष | Temporal frame |
| train-s48 | शताब्दी | Temporal frame |
| train-s49 | शताब्दी | Temporal frame |
| train-s34 | अंदाज | Manner (अंदाज में) |
| train-s50 | शान | Abstract locus (शान में) |

**Conclusion:** R1 strong hits are uniformly plausible. R2 contributes most confirmed output but also most questionable confirmations.

---

## 3. Genuinely Ambiguous Examples

**Observation:** 6 of 17 ambiguous rows appear genuinely ambiguous even with light sentence context.

| sent_id | Token | Rule | Reason |
|---------|-------|------|--------|
| train-s10 | रूप | R4 | Manner adverbial (मुख्य रूप से); Karaṇa vs Apādāna is not the right frame |
| train-s17 | तरह | R4 | Manner adverbial (इस तरह से) |
| train-s17 | रूप | R4 | Manner adverbial (जीवंत रूप से) |
| train-s29 | रूप | R4 | Manner adverbial (मूल रूप से) |
| train-s6 | लोगों | R5 | आमंत्रित करता: recipient vs theme remains open |
| train-s47 | चमक | R5 | Abstract object; Karma vs Sampradāna unclear |

**Example (R4, genuine):** *मुख्य रूप से यह प्रदर्शन कला और दृश्य कला का केंद्र है ।* (token: रूप)

**Conclusion:** Four R4 manner hits should not be forced into Karaṇa|Apādāna without a separate manner handling strategy. Two R5 hits remain appropriately unresolved in v1.

---

## 4. Potentially Resolvable Ambiguous Examples

**Observation:** 11 of 17 ambiguous rows may support a single Karaka if verb frame or construction context is added in a later rule version.

### R4: potentially resolvable (7 rows)

| sent_id | Token | Likely direction | Context cue in sentence |
|---------|-------|------------------|-------------------------|
| train-s16 | चित्रकला | Karaṇa (material/instrument) | सज्जित (decorated with) |
| train-s20 | हिस्सों | Apādāna (source) | एकत्रित (collected from regions) |
| train-s23 | जिलों | Apādāna (source) | एकत्रित (collected from districts) |
| train-s25 | झील | Apādāna (adjacency/source) | से लगी (attached to lake) |
| train-s35 | झील | Apādāna (separation) | अलग (separated from lake) |
| train-s35 | ओवरब्रिज | Apādāna (separation) | अलग (separated by overbridge) |
| train-s41 | मुंबई | Apādāna (route origin) | … से … जाने वाली (trains from Mumbai) |

**Example (R4, resolvable):** *यहाँ मध्य प्रदेश के विभिन्न हिस्सों से कला के खूबसूरत नमूने एकत्रित करके रखे गए हैं ।* (token: हिस्सों)

### R5: potentially resolvable (4 rows)

| sent_id | Token | Likely direction | Context cue in sentence |
|---------|-------|------------------|-------------------------|
| train-s19 | पुस्तकालय | Karma (patient) | देखा जाता है (passive viewing frame) |
| train-s23 | नमूनों | Karma (patient) | रखा गया (placed/stored) |
| train-s27 | प्राणियों | Karma (patient) | देखने (seeing animals) |
| train-s48 | वैभव | Karma (direct object) | बयाँ करती (express glory) |

**Hypothesis:** Verb-lemma or frame rules could confirm some R4/R5 rows without forcing all ambiguous cases.

---

## 5. Rules That Appear Overly Broad

| Rule | Issue | Evidence from batch |
|------|-------|---------------------|
| **R2** | Every `obl`+`में` → confirmed Adhikaraṇa | 7 of 15 R2 hits are weak (extent, time, manner, abstract) |
| **R4** | One rule for manner, source, separation, material | 4 manner hits labeled genuine; 7 resolvable with frame cues |
| **R5** | All `obj`/`iobj`+`को` stay ambiguous | 4 of 6 hits look patient-like with verb context |

**Observation:** R2 is overly broad if Adhikaraṇa is interpreted as physical location only. R4 is overly broad because manner adverbials share the same rule as source/instrument readings. R5 is conservatively narrow (always ambiguous) even when frames suggest Karma.

**Conclusion:** R2 produces false-confidence `confirmed` labels. R4 and R5 need subtype or frame logic rather than a single blanket outcome.

---

## 6. Constructions Not Covered by Current Rules

**Observation:** In the 779-token batch, **73 tokens** had a case marker but received `no_decision` because no R1–R5 condition matched.

### Top uncovered `(deprel, case_marker)` pairs

| Deprel | Case | Count | Example token | sent_id |
|--------|------|------:|---------------|---------|
| nmod | के | 20 | देश | train-s6 |
| nmod | का | 11 | दिन | train-s6 |
| nmod | से | 7 | बजे | train-s14 |
| nmod | की | 6 | एशिया | train-s1 |
| obl | के | 4 | सोमवार | train-s14 |
| obl | को | 4 | सोमवार | train-s21 |
| nmod | में | 3 | मस्जिदों | train-s1 |
| nmod | पर | 3 | यहीं | train-s13 |
| obl | तक | 3 | बजे | train-s14 |
| root | पर | 2 | स्थल | train-s16 |

**Example (uncovered, nmod+में):** *यह एशिया की सबसे बड़ी मस्जिदों में से एक है ।* (token: मस्जिदों; partitive construction, not obl+में)

**Example (uncovered, obl+को):** *संग्रहालय सोमवार को बंद रहता है ।* (token: सोमवार; temporal dative)

### Other coverage gaps

| Pattern | Count in batch | v1 behavior |
|---------|----------------:|-------------|
| Bare `nsubj` (no case child) | 37 | `no_decision` (no rule for nsubj without ने) |
| `nsubj`+`ने` | 3 | R1 (all matched) |
| Genitive `nmod`+के/का/की | 37 combined | `no_decision` (excluded by design) |
| Passive `nsubj:pass`+`द्वारा` | 1 | `no_decision` |
| `obl`+`तक` (endpoint) | 3 | `no_decision` |

**Conclusion:** v1 rules cover only five postposition patterns on specific parent deprels. Genitive linkers, partitive constructions, temporal dative obliques, and bare subjects are common but uncovered.

---

## 7. Potential Future Rule Refinements

These are hypotheses for a later version. None are implemented.

| Target | Motivation | Proposed direction |
|--------|------------|-------------------|
| R2 subtypes | 7 weak R2 confirmations | Separate spatial, temporal, extent, and manner में frames |
| R4 manner filter | 4 manner R4 hits | Return `no_decision` or a non-Karaka manner label for रूप/तरह से |
| R4 verb-frame rules | 7 resolvable R4 hits | Use lemmas (एकत्रित, अलग, सज्जित, जाने वाली) for Apādāna vs Karaṇa |
| R5 verb-frame rules | 4 resolvable R5 hits | Confirm Karma for perception/placement/expression; keep invitation ambiguous |
| Genitive handling | 37 nmod genitive hits | Explicit `no_decision` with reason (NP-linking, per rule spec) |
| obl+को / obl+तक | 7 hits in batch | Dedicated temporal/locative rules or documented exclusions |
| Bare nsubj | 37 hits in batch | `no_decision` until mapper supports `corrected` decisions |
| `corrected` decision type | Not observed in batch | Compare mapper hypothesis vs verifier when mapper exists |

---

## 8. Summary Counts

| Category | Count |
|----------|------:|
| Meaningful verifier rows analyzed | 36 |
| Confirmed: strong | 10 |
| Confirmed: moderate | 2 |
| Confirmed: weak | 7 |
| Ambiguous: genuinely ambiguous | 6 |
| Ambiguous: potentially resolvable | 11 |
| Uncovered tokens with case marker | 73 |
| Bare nsubj (no case child) | 37 |

---

## 9. Status

**Observation:** This analysis identifies where v1 rules work well, where they over-confirm, where ambiguity is appropriate, and where future context rules may help.

**Future work:** Implement refinements only after explicit approval. Prior candidates: R2 subtype split, R4 manner exclusion, verb-frame disambiguation for R4/R5.

**No changes made to:** `src/verifier/`, mapper, Stanza, HTDB, or `docs/rule_specification_v1.md`.

Regenerate inputs:

```bash
python src/verifier/run_verifier_batch.py
```

Re-run analysis: `notebooks/06_verifier_failure_analysis.ipynb`
