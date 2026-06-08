# Rule Specification — Version 1

**Status:** Initial hypothesis (not implemented)  
**Purpose:** Define the first symbolic verifier rules for the Paninian rule-based corrector  
**Inputs:** UD dependency parse + conservative mapping from `docs/ud_to_karaka_mapping_v1.md`  
**Evidence base:** `notebooks/02_postposition_analysis.ipynb`, `docs/project_context.md`

This document specifies **Version 1** verifier rules only. These are cautious, research-oriented hypotheses — not a complete Paninian grammar. The verifier must support four decision types: `confirmed`, `corrected`, `ambiguous`, and `no_decision`.

---

## How to Read This Specification

- **Condition** — what must hold in the UD tree for the rule to fire.
- **Possible Karaka** — Karaka role(s) the rule considers; may be a single role or a disjunction.
- **Decision Type** — what the verifier should output when the rule applies.
- **Ambiguity / Fallback** — what to do when evidence is insufficient or multiple Karakas remain plausible.

Rules evaluate **token + UD label + postposition evidence**. Postpositions appear as child tokens with `deprel = case`.

---

## Verifier Rules (v1)

| Rule ID | Condition | Possible Karaka | Confidence | Decision Type | Reasoning | Ambiguity / Fallback |
|---------|-----------|-----------------|------------|---------------|-----------|----------------------|
| **R1** | Parent token has `deprel = nsubj` and a child `case` token with form `ने` | Kartā | High | `confirmed` | In Hindi-HDTB, `ने` attaches to `nsubj` parents in ~98.4% of cases. This is the strongest postposition–label association found so far. Ergative/agent marking with `ने` provides reliable evidence for Kartā when the syntactic subject is the marked noun. | If `nsubj` lacks `ने`, do not apply R1 — return `no_decision` or rely on mapping hypothesis only. If `ने` appears on a non-`nsubj` parent (rare), return `no_decision`. |
| **R2** | Parent token has `deprel = obl` and a child `case` token with form `में` | Adhikaraṇa | Medium–High | `confirmed` | `में` attaches to `obl` parents in ~87.6% of cases. Locative and locus readings are the dominant pattern. This rule targets location/container Adhikaraṇa candidates. | If parent is not `obl`, return `no_decision`. If `में` appears on `nmod` or other parents (~9.5%), return `no_decision` unless additional frame evidence is added in a later rule version. |
| **R3** | Parent token has `deprel = obl` and a child `case` token with form `पर` | Adhikaraṇa | Medium–High | `confirmed` | `पर` attaches to `obl` parents in ~89.8% of cases. Surface/location readings (on, upon) align with Adhikaraṇa. | If parent is not `obl`, return `no_decision`. Do not apply to `nmod` parents (~6.4%) without further evidence. |
| **R4** | Parent token has `deprel = obl` and a child `case` token with form `से` | Karaṇa **or** Apādāna | Low–Medium | `ambiguous` | `से` attaches to `obl` parents in ~69.5% of cases, but `से` can mark instrument (Karaṇa) or source/separation (Apādāna). UD `obl` alone does not disambiguate. Forcing one Karaka would violate verifier principles. | Return `ambiguous` with candidates {Karaṇa, Apādāna}. Use verb-frame or world-knowledge checks in a later rule version. If `से` appears on `obj`/`iobj` parents (~15.7% combined), return `no_decision` in v1. |
| **R5** | Parent token has `deprel = obj` **or** `deprel = iobj` and a child `case` token with form `को` | Karma **or** Sampradāna | Low–Medium | `ambiguous` | `को` is highly mixed: `obj` parents ~45.2%, `iobj` ~24.0%, `obl` ~17.6%, `nsubj` ~9.7%. `को` signals dative/accusative marking but does not uniquely identify Karma vs Sampradāna. Recipient and patient readings require verb-frame context. | Return `ambiguous` with candidates {Karma, Sampradāna}. If parent is `obl` or `nsubj`, return `no_decision` in v1 (outside R5 scope). Do not auto-pick Karma for `obj` or Sampradāna for `iobj` — that would overfit UD syntax to Paninian semantics. |

---

## Decision Type Usage (v1)

| Decision Type | When to use in v1 |
|---------------|-------------------|
| `confirmed` | R1, R2, R3 — postposition evidence strongly supports one Karaka for the stated UD configuration. |
| `corrected` | Not used in v1 initial rules. Reserved for when a rule overrides a mapping hypothesis (e.g. mapping guessed Kartā for bare `nsubj`, verifier rejects). |
| `ambiguous` | R4, R5 — multiple Karakas remain plausible; verifier must surface both candidates. |
| `no_decision` | Rule conditions not met, parent label outside rule scope, or evidence too weak to judge. |

---

## What v1 Rules Deliberately Exclude

- No rules for bare `nsubj` without `ने` (mapping stays Low–Medium; verifier withholds).
- No rules for genitive markers (`के`, `की`, `का`) — NP-linking, not Karaka assignment.
- No rules for `root`, `xcomp`, `ccomp`, `nsubj:pass`, or passive auxiliaries.
- No neural parser integration or model-based disambiguation.
- No automatic resolution of R4/R5 ambiguities.

---

## Expected Verifier Behaviour (Illustrative)

| UD pattern | Mapping hypothesis | v1 rule | Expected output |
|------------|-------------------|---------|-----------------|
| `nsubj` + `ने` | Kartā (Low–Medium) | R1 | `confirmed` → Kartā |
| `nsubj` without `ने` | Kartā (Low–Medium) | — | `no_decision` |
| `obl` + `में` | Adhikaraṇa (Low) | R2 | `confirmed` → Adhikaraṇa |
| `obl` + `पर` | Adhikaraṇa (Low) | R3 | `confirmed` → Adhikaraṇa |
| `obl` + `से` | Karaṇa or Apādāna | R4 | `ambiguous` → {Karaṇa, Apādāna} |
| `obj`/`iobj` + `को` | Karma / Sampradāna | R5 | `ambiguous` → {Karma, Sampradāna} |

---

## Known Limitations

- Rules are derived from Hindi-HDTB **training-set statistics** and manual examples — not validated on dev/test yet.
- `confirmed` in v1 means "supported by stated symbolic evidence," not linguistically proven.
- R2/R3 may over-generate Adhikaraṇa for temporal or abstract `में`/`पर` uses.
- R4/R5 require future verb-frame rules or human review for disambiguation.

---

## Next Steps (not in v1)

1. Implement these rules in `src/verifier/` with explicit decision-type outputs.
2. Run on a small sentence subset; log `confirmed`, `ambiguous`, and `no_decision` counts.
3. Add `corrected` rules where mapping and postposition evidence conflict.
4. Extend R4/R5 only after verb-frame analysis — not by forcing a single Karaka.

---

## References

- Project context: `docs/project_context.md`
- Mapping hypothesis: `docs/ud_to_karaka_mapping_v1.md`
- Postposition evidence: `notebooks/02_postposition_analysis.ipynb`
