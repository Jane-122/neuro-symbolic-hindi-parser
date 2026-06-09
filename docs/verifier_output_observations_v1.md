# Verifier Output Observations (Version 1)

**Status:** Initial inspection notes  
**Source:** `notebooks/05_verifier_output_analysis.ipynb`  
**Input data:** `results/verifier_batch_meaningful.csv` (from `src/verifier/run_verifier_batch.py`)  
**Rule reference:** `docs/rule_specification_v1.md` (unchanged)

This document summarizes what the v1 verifier produced on a small batch. It records observations only. **No verifier rule logic is being changed yet**, and `docs/rule_specification_v1.md` is not updated here.

---

## 1. Batch Size and Meaningful Output Counts

**Observation**

| Metric | Count |
|--------|------:|
| Sentences processed | 50 |
| Tokens evaluated (all rows) | 779 |
| Meaningful outputs (`decision_type` ≠ `no_decision`) | 36 |
| No decision | 743 |

Only **4.6%** of tokens in this batch received a non-`no_decision` verdict. That is expected for v1: rules fire only on specific `deprel` + postposition pairs, and most tokens lack matching case markers on the parent.

No `corrected` decisions appeared in this batch.

---

## 2. Rule-wise Counts

**Observation**

| Rule ID | Condition (summary) | Meaningful hits |
|---------|---------------------|----------------:|
| **R1** | `nsubj` + `ने` | 3 |
| **R2** | `obl` + `में` | 15 |
| **R3** | `obl` + `पर` | 1 |
| **R4** | `obl` + `से` | 11 |
| **R5** | `obj`/`iobj` + `को` | 6 |

R2 fired most often in this slice of tourism/architecture text. R3 had only one hit (`हिल्स` in train-s15), so surface-location evidence is underrepresented in this batch.

---

## 3. Decision-type Counts

**Observation**

| Decision type | Count |
|---------------|------:|
| `confirmed` | 19 |
| `ambiguous` | 17 |
| `corrected` | 0 |

Confirmed and ambiguous outputs are nearly balanced among meaningful rows. All `confirmed` rows come from R1, R2, or R3. All `ambiguous` rows come from R4 or R5, matching the v1 specification.

---

## 4. Rules That Look Reliable (from Examples)

The following assessments are based on manual inspection of example rows. They are tentative judgments, not validated against gold Karaka labels.

### R1: `nsubj` + `ने` → Kartā (`confirmed`)

All three hits are plausible agents:

- **शाहजेहन** (*इसे नवाब शाहजेहन ने बनवाया था ।*)
- **कोरिया** (*इसे चार्ल्स कोरिया ने डिजाइन किया है ।*)
- **राजाओं** (*… राजाओं ने शानदार इमारतें और भवन बनवाकर …*)

**Observation:** The `ने` + `nsubj` pattern consistently marks an animate agent in these examples.

**Hypothesis:** R1 is the most reliable rule in this batch, consistent with the ~98.4% train-set association noted in the rule spec.

### R3: `obl` + `पर` → Adhikaraṇa (`confirmed`)

The single example is a clear surface/location reading:

- **हिल्स** (*… 200 एकड़ में श्यामला हिल्स पर बड़ी झील के सामने फैला है ।*)

**Observation:** The example appears semantically appropriate for Adhikaraṇa.

**Hypothesis:** R3 may be reliable for surface/location readings, but the sample size (one hit) is too small to support a firm conclusion.

### R2: `obl` + `में` → Adhikaraṇa (`confirmed`), partly reliable

Several examples are straightforward locatives:

- **हॉल**, prayer hall as location (*हॉल में जाने के लिए …*)
- **संग्रहालय**, museum as venue (*संग्रहालय में पुस्तकालय …*)
- **चौक**, **गलियों**, **झील**, square, lanes, and lake as locus

**Observation:** These examples support R2 for classic "in/at" location readings.

**Hypothesis:** R2 appears useful for spatial containers, but not all `में` hits in this batch are clearly locative (see Section 6).

---

## 5. Rules That Need Caution

### R2: extent, measure, and non-spatial `में`

R2 fires on every `obl` + `में` pair, but examples show readings that are not pure location:

- **एकड़**, **हैक्टेयर**, area/extent (*200 एकड़ में …*, *445 हैक्टेयर में फैला है*)
- **वर्ष**, temporal span (*वर्ष में कभी भी …*)
- **शताब्दी**, time period (*16 से 17वीं शताब्दी में …*)
- **अंदाज**, manner (*… खूबसूरत अंदाज में देख …*)
- **शान**, abstract locus (*… इसकी शान में चार चाँद लगा दिए*)

**Observation:** The verifier labels all of these as Adhikaraṇa with `confirmed`.

**Hypothesis:** Paninian locus, extent, manner, and temporal frame may need finer typing in a later version. R2 outputs should be used with caution outside clear spatial containers.

### R4: `obl` + `से` (`ambiguous`)

All 11 hits correctly avoid forcing Karaṇa or Apādāna, but the examples mix several semantic readings:

- **Manner:** *मुख्य रूप से …*, *… तरह से …*, *… रूप से …*
- **Source/origin:** *… विभिन्न हिस्सों से …*, *… जिलों से एकत्रित …*, *मुंबई से …*
- **Instrument-like / material:** *… चित्रकला से सज्जित …*
- **Separation/adjunction:** *… झील से लगी …*, *… ओवरब्रिज से अलग …*

**Observation:** R4 behaves as specified (ambiguous output).

**Conclusion:** Downstream use should not treat R4 rows as resolved Karaka assignments.

### R5: `obj`/`iobj` + `को` (`ambiguous`)

All six hits look object-like in UD, yet Karma vs. Sampradāna remains unresolved:

- **लोगों**, invite people (*… लोगों को आमंत्रित करता है*)
- **प्राणियों**, see animals (*… प्राणियों को देखने का आनंद …*)
- **नमूनों**, **पुस्तकालय**, displayed/stored items
- **चमक**, **वैभव**, abstract objects of verbs (*… चमक को … धुँधला नहीं सकी*, *… वैभव को बयाँ करती हैं*)

**Observation:** Many examples appear patient-like (Karma), but recipient and experiencer-like readings are possible without verb-frame context.

**Conclusion:** R5 correctly withholds commitment in v1.

### R3: low coverage

**Observation:** Only one token triggered R3 in 50 sentences.

**Conclusion:** Reliability cannot be assessed from this batch alone.

---

## 6. Observed Limitations

### R2: `में` sometimes marks extent/measure, not only location

As noted above, `में` on `obl` parents includes:

- **Spatial extent** (एकड़, हैक्टेयर)
- **Temporal frames** (वर्ष, शताब्दी)
- **Manner** (अंदाज में)
- **Abstract "in"** (शान में)

**Observation:** v1 maps all of these to Adhikaraṇa with `confirmed`.

**Hypothesis:** This is a reasonable first hypothesis for locus-like readings, but it may over-generalize if Adhikaraṇa is interpreted strictly as physical location.

### R4: `से` includes manner, source, and instrument-like readings

The batch shows `से` under a single `obl` parent covering:

- Manner adverbials (*रूप से*, *तरह से*)
- Source/origin (*हिस्सों से*, *मुंबई से*)
- Material/instrument decoration (*चित्रकला से सज्जित*)
- Spatial separation (*झील से अलग*)

**Observation:** UD `obl` + `से` does not separate Karaṇa from Apādāna (or manner).

**Conclusion:** v1's `ambiguous` output is appropriate. Disambiguation will likely need verb semantics or additional cues.

### R5: `को` often looks object-like but remains ambiguous in v1

**Observation:** Tokens such as **लोगों**, **प्राणियों**, and **नमूनों** are strong Karma candidates, yet **को** also marks recipients and other roles in Hindi.

**Conclusion:** Without frame-level constraints, assigning Sampradāna vs. Karma would be speculative. Keeping R5 at `ambiguous` matches project principles.

---

## 7. Status and Future Work

**Status (no rule logic changes yet)**

These observations are documentation only. They do not:

- Modify `src/verifier/simple_verifier.py` or batch scripts
- Change decision types or confidence labels in code
- Update `docs/rule_specification_v1.md`

**Future work (when explicitly requested)**

- Larger batches and dev/test split runs
- Verb-frame features for R4 and R5 disambiguation
- Refined R2 subtypes for extent vs. location

Until then, the v1 verifier remains unchanged.

---

## Reference: Example Rows Inspected

Analysis notebook: `notebooks/05_verifier_output_analysis.ipynb`

Regenerate CSV:

```bash
python src/verifier/run_verifier_batch.py
```
