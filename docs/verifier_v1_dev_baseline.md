# Verifier v1 Dev Baseline (Pipeline v1)

**Status:** Baseline evaluation report  
**Dataset:** `data/raw/hi_hdtb-ud-dev.conllu` (full dev split)  
**Pipeline:** `src/pipeline/run_dev_baseline.py`  
**Components:** `simple_mapper.py`, `simple_verifier.py`, `run_gold_ud_pipeline.py` (shared logic)

This report records dev-split baseline statistics for Pipeline v1. No rules, mapper logic, or verifier logic were changed for this run.

---

## 1. Dataset and Run Configuration

| Item | Value |
|------|------:|
| Dataset file | `hi_hdtb-ud-dev.conllu` |
| Sentences processed | 1,659 |
| Tokens processed | 35,217 |
| Meaningful outputs (`final_decision` ≠ `no_decision`) | 7,019 |

**Outputs saved:**

- `results/dev_baseline_all.csv` (35,217 rows)
- `results/dev_baseline_meaningful.csv` (7,019 rows)

**Analysis notebook:** `notebooks/09_dev_baseline_analysis.ipynb`

---

## 2. Final Decision Distribution

**Observation (all tokens, n = 35,217)**

| final_decision | Count | % of all tokens |
|----------------|------:|----------------:|
| `no_decision` | 28,198 | 80.07% |
| `mapping_hypothesis` | 4,464 | 12.68% |
| `confirmed` | 1,715 | 4.87% |
| `ambiguous` | 840 | 2.39% |

**Observation (meaningful tokens only, n = 7,019)**

| final_decision | Count | % of meaningful |
|----------------|------:|----------------:|
| `mapping_hypothesis` | 4,464 | 63.60% |
| `confirmed` | 1,715 | 24.44% |
| `ambiguous` | 840 | 11.97% |

**Interpretation:**

- About one in five dev tokens receives a non-`no_decision` label.
- Among meaningful rows, most are `mapping_hypothesis` (mapper-only guesses).
- Verifier-backed rows (`confirmed` + `ambiguous`) account for 2,555 tokens (7.26% of all tokens, 36.40% of meaningful rows).

---

## 3. Verifier Rule Distribution

**Observation (tokens where a verifier rule fired, n = 2,555)**

| Rule | Count | % of all tokens | % of rule hits |
|------|------:|----------------:|---------------:|
| R2 (`obl` + `में`) | 847 | 2.41% | 33.1% |
| R1 (`nsubj` + `ने`) | 556 | 1.58% | 21.8% |
| R5 (`obj`/`iobj` + `को`) | 499 | 1.42% | 19.5% |
| R4 (`obl` + `से`) | 341 | 0.97% | 13.3% |
| R3 (`obl` + `पर`) | 312 | 0.89% | 12.2% |

**Hypothesis:** R2 and R1 dominate verifier activity on dev, consistent with train postposition statistics. R3 appears more often on dev (312 hits) than in the 50-sentence train batch (1 hit), likely due to larger sample size.

---

## 4. Mapper Status Distribution

**Observation (all tokens)**

| mapper_status | Count | % of all tokens |
|---------------|------:|----------------:|
| `unsupported` | 19,865 | 56.41% |
| `evidence_only` | 6,674 | 18.95% |
| `mapped` | 3,983 | 11.31% |
| `context_dependent` | 3,036 | 8.62% |
| `no_karaka` | 1,659 | 4.71% |

**Interpretation:** Most tokens are `unsupported` (no v1 deprel mapping) or `evidence_only` (`case` tokens). Meaningful pipeline output comes mainly from `mapped` and `context_dependent` parents when the verifier does not override.

---

## 5. Top Dependency Labels (dev tokens)

| deprel | Count | % of all tokens |
|--------|------:|----------------:|
| case | 6,674 | 18.95% |
| compound | 4,038 | 11.47% |
| nmod | 3,508 | 9.96% |
| obl | 3,036 | 8.62% |
| punct | 2,367 | 6.72% |
| nsubj | 2,063 | 5.86% |
| obj | 1,661 | 4.72% |
| root | 1,659 | 4.71% |
| amod | 1,501 | 4.26% |
| mark | 1,308 | 3.71% |

---

## 6. Observations

**Observation:** The dev baseline confirms that Pipeline v1 produces structured output at scale (7,019 meaningful rows from 1,659 sentences).

**Observation:** Verifier-backed decisions remain a minority of all tokens (7.26%), but are more common among meaningful rows (36.40%).

**Observation:** `mapping_hypothesis` is the largest meaningful category (63.60% of meaningful rows). These rows should be treated as hypotheses, not verified Karaka assignments.

**Observation:** Rule hit counts scale with dev size: R1 (556), R2 (847), R3 (312), R4 (341), R5 (499). Relative ordering (R2 most frequent, R3 least among the five) is stable with train batch patterns.

**Hypothesis:** Dev postposition patterns validated in notebook 03 should align with these rule frequencies, but this baseline does not evaluate Karaka correctness against gold labels.

---

## 7. Limitations

1. **No Karaka gold standard:** Counts describe pipeline behavior, not linguistic accuracy.
2. **Gold UD input:** Parses come from the treebank, not a separate parser; this is an upper bound for syntactic input quality.
3. **Pipeline v1 merge logic only:** `confirmed` and `ambiguous` override mapper; otherwise `mapping_hypothesis` or `no_decision`.
4. **No `corrected` decision type:** Mapper-verifier conflicts (e.g. copular `nsubj` mapped to Kartā) are not flagged explicitly.
5. **Train-derived rules on dev:** Rules were designed from train statistics; dev baseline measures firing rates, not rule validity against annotated Karakas.
6. **Single split:** Test split and cross-split error analysis are not included here.

---

## 8. Future Work (not in this baseline)

- Compare dev baseline counts with the 50-sentence train batch (`gold_ud_pipeline_*` CSVs).
- Manual inspection samples from `dev_baseline_meaningful.csv`.
- `corrected` decision logic when mapper and verifier disagree.
- Test-split baseline using the same script pattern.

Regenerate dev baseline:

```bash
python src/pipeline/run_dev_baseline.py
```
