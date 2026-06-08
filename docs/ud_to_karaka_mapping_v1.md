# UD to Karaka Mapping — Version 1

**Status:** Initial hypothesis (not validated)  
**Source:** Hindi-HDTB training set (`data/raw/hi_hdtb-ud-train.conllu`)  
**Based on:** Dataset exploration notebook (`notebooks/01_dataset_exploration.ipynb`)

This document defines **Version 1** of the UD → Karaka mapping. The goal is not linguistic perfection. The goal is a simple, inspectable starting point that can be revised after rule testing and error analysis.

---

## Mapping Table (v1)


| UD Label | Possible Karaka                                             | Confidence | Reasoning                                                                                                                                                                                                                                                            | Example from Dataset                                                                                                                              |
| -------- | ----------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `root`   | None *(predicate anchor)*                                   | High       | The `root` is the main predicate of the sentence. In Paninian terms, Karakas are semantic roles of **participants** linked to the action — not the verb itself. The root anchors the parse; Karaka assignment applies to its dependents.                             | **train-s2:** `बनवाया` (बनवाना) `--root-->` *(sentence head)* in *इसे नवाब शाहजेहन ने बनवाया था ।*                                                |
| `nsubj`  | Kartā *(agent)*                                             | Low–Medium | `nsubj` is a **grammatical subject** (UD syntactic role), not necessarily a Paninian Kartā (semantic agent). E.g. in *द्वार … मंजिला है* (train-s3), `द्वार` is `nsubj` but not a doer. `ने` raises confidence, but UD ≠ Panini by default.                      | **train-s2:** `शाहजेहन` (शाहजेहन) `--nsubj-->` `बनवाया` in *इसे नवाब शाहजेहन ने बनवाया था ।* (agent marked by `ने`)                               |
| `obj`    | Karma *(patient / direct object)*                           | Medium     | `obj` typically marks the direct object — the entity most directly affected by the action. In Hindi, accusative/dative `को` on the object often signals Karma, but `obj` alone is not always sufficient without postposition context.                                | **train-s2:** `इसे` (यह) `--obj-->` `बनवाया` in *इसे नवाब शाहजेहन ने बनवाया था ।* (`इसे` = यह + को)                                               |
| `iobj`   | Sampradāna *(recipient / beneficiary)*                      | Medium     | `iobj` marks the indirect object — often the recipient or beneficiary of the action. In Hindi-HDTB, this frequently co-occurs with `को`, which Paninian analysis associates with Sampradāna (though `को` can also appear with Karma).                                | **train-s111:** `प्रथम` (प्रथम) `--iobj-->` `दिया` in *मुगल शासक शाह आलम ने … महाराजा सवाई माधोसिंह प्रथम को … दिया ।*                            |
| `obl`    | Context-dependent *(Adhikaraṇa, Apādāna, Karaṇa, or other)* | Low        | `obl` is a broad label for oblique dependents: time, location, source, instrument, manner, and more. The Karaka role must be resolved using the attached postposition (`में`, `से`, `पर`, `को`, etc.) and the verb's semantics — not from `obl` alone.               | **train-s4:** `हॉल` (हॉल) `--obl-->` `हैं` in *… मुख्य प्रार्थना हॉल में जाने के लिए 9 प्रवेश द्वार हैं ।* (`में` suggests Adhikaraṇa / location) |
| `case`   | Not a Karaka *(disambiguation clue)*                        | High       | `case` marks postpositions and case markers. These are not Karaka roles themselves, but they provide strong evidence for the Karaka of the **parent noun/pronoun**. Mapping rules should read `case` children to refine labels on `nsubj`, `obj`, `obl`, and `iobj`. | **train-s2:** `ने` (ने) `--case-->` `शाहजेहन` in *इसे नवाब शाहजेहन ने बनवाया था ।* (`ने` → Kartā signal for parent `nsubj`)                       |


---

## Label-by-Label Notes

### `root`

The root token is the syntactic head of the sentence — usually a verb or copular predicate. Version 1 treats it as the **action anchor** around which Karakas are defined.

- **v1 decision:** Do not assign a Karaka to `root`.
- **Why:** Karakas describe who/what participates in the action (agent, object, instrument, etc.). The predicate itself is the locus of the action, not a participant role.
- **Implication for later rules:** All Karaka mapping should look at dependents of `root`, not at `root` itself.

### `nsubj` → Kartā

UD labels describe **syntactic** roles; Paninian Karakas describe **semantic** roles. Those are not always identical — that mismatch is central to this project.

`nsubj` marks the grammatical subject. It may correspond to Kartā when `ने` marks an agent, but many `nsubj` tokens are not doers (e.g. `द्वार` in *द्वार … मंजिला है*, train-s3).


| Signal                        | v1 Karaka guess                        |
| ----------------------------- | -------------------------------------- |
| `nsubj` + child `case` = `ने` | Kartā (High)                           |
| `nsubj` without `ने`          | Kartā or non-agent subject (Low–Medium) |


**Caution:** Do not treat `nsubj` as Kartā by default. Copular and stative predicates routinely assign `nsubj` to non-agents.

### `obj` → Karma

Direct objects are the primary Karma candidates. The notebook example `इसे … बनवाया` shows a pronoun with dative/accusative marking (`को`) functioning as `obj`.


| Signal                     | v1 Karaka guess     |
| -------------------------- | ------------------- |
| `obj` with `को` marking    | Karma (Medium–High) |
| `obj` without postposition | Karma (Medium)      |


**Caution:** Some `obj` tokens may be better analysed as Sampradāna when `को` marks a human recipient rather than a patient — context matters.

### `iobj` → Sampradāna

Indirect objects in the dataset often express who receives something or for whom an action is done. The train-s111 example (*… प्रथम को … दिया*) is a typical gift/giving frame: the recipient is `iobj`.


| Signal                                 | v1 Karaka guess          |
| -------------------------------------- | ------------------------ |
| `iobj` + `को`                          | Sampradāna (Medium–High) |
| `iobj` without clear recipient reading | Sampradāna (Low–Medium)  |


**Caution:** Hindi-HDTB uses `iobj` in a UD-specific way; always verify against the sentence frame.

### `obl` → Context-dependent

`obl` is the most ambiguous label in this set. It is the second most frequent label in the training data (after `case`). The postposition on the oblique phrase is essential.


| Postposition (on `case` child) | v1 Karaka guess                             |
| ------------------------------ | ------------------------------------------- |
| `में`                          | Adhikaraṇa (location/locus)                 |
| `से`                           | Apādāna (source) or Karaṇa (instrument)     |
| `पर`                           | Adhikaraṇa (location/surface)               |
| `को`                           | Sampradāna or Karma (depends on verb frame) |
| `ने`                           | *(rare on obl; usually on nsubj)*           |


**Example contrast from the data:**

- *हॉल **में** …* (train-s4) → location-like `obl` → Adhikaraṇa candidate
- *दिल्ली **से** … भेजी* (train-s1112) → source-like `obl` → Apādāna candidate

### `case` → Not a Karaka

Postpositions are **features for disambiguation**, not standalone Karaka assignments. Version 1 always resolves `case` by looking at its **head** (the noun/pronoun it attaches to) and that head's `deprel`.


| Postposition | Typical role of parent                                                |
| ------------ | --------------------------------------------------------------------- |
| `ने`         | Kartā signal when parent is `nsubj`                                   |
| `को`         | Karma or Sampradāna signal on `obj` / `iobj`                          |
| `से`         | Karaṇa or Apādāna signal on `obl`                                     |
| `में`, `पर`  | Adhikaraṇa signal on `obl`                                            |
| `का/की/के`   | Genitive linker — not a Karaka by itself; helps identify noun phrases |


---

## How v1 Mapping Should Be Used

1. **Start with the UD label** (`nsubj`, `obj`, etc.) to get a default Karaka hypothesis.
2. **Check `case` children** of the same noun phrase to raise or lower confidence.
3. **Skip `root`** for Karaka assignment.
4. **Flag `obl` and ambiguous `को` cases** for manual review or later symbolic rules.

This is a **two-step** process: label mapping first, postposition refinement second. Version 2 should refine this after verifier experiments.

---

## Known Limitations of v1

- Based on a small set of inspected examples, not full-treebank statistics.
- Does not handle `nsubj:pass`, `xcomp`, `ccomp`, or other labels yet.
- `obl` → Karaka mapping is intentionally underspecified.
- `को` ambiguity (Karma vs Sampradāna) is not resolved.
- Copular and existential constructions may violate the default `nsubj` → Kartā assumption.
- No agreement with a gold Karaka-annotated corpus has been performed.

---

## Next Steps (not in v1)

- Quantify how often each postposition co-occurs with each UD label.
- Add symbolic verification rules in `src/verifier/`.
- Document systematic errors in `docs/research_notes.md`.
- Produce Version 2 after error analysis.

---

## References

- Project context: `docs/project_context.md`
- Dataset exploration: `notebooks/01_dataset_exploration.ipynb`
- Working mapping notes: `docs/ud_to_karaka_mapping.md`

