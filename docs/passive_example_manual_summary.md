# Passive Diagnostic Manual Example Summary

Input reviewed:

- `output/passive_diagnostic_examples.csv`
- First 50 examples for `possible_passive_karta`
- First 50 examples for `possible_passive_karma`

No correction rule was implemented in this review.

## Summary Judgment

Overall recommendation: **NEEDS REFINEMENT**

The passive diagnostics do surface some real passive-related dependency/Karaka correction opportunities, but the current definitions are too broad. They mostly identify syntactic configurations (`obj` without Karta, `nsubj` without Karma), not passive constructions.

## possible_passive_karta

Definition currently captures:

`deprel == obj` and `final_candidates` does not contain Karta.

### Manual observations from first 50 examples

Approximate genuinely passive examples: **about 18 of 50**, or **36%**.

Approximate examples with explicit passive auxiliaries from the requested list: **about 14 of 50**, or **28%**.

Common passive indicators observed:

- `गया`
- `गई`
- `गए`
- `जाता`
- `किया गया`
- `की गई`

### Recurring patterns

1. Genuine passive where Stanza marks a passive participant as `obj`.

Examples include:

- `यह मंदिर ... बनाया गया है`
- `यह मूर्ति निकाली गई थी`
- `यह ... जाना जाता है`
- `कमी नहीं देखी गई`

These are plausible correction opportunities because gold Karaka is sometimes `Karta` while the pipeline predicts `Karma`.

2. Ordinary active `obj` cases.

Many examples are normal objects with gold `Karma`, and the current prediction is already correct or contains the correct label.

Examples include:

- `कुशावती को ... चुना`
- `पर्यटकों को ... खींचता है`
- `फोटो खींचना चाहते हैं`
- `आरोप लगाया`
- `संसाधन जुटा सकेगा`

These are not passive correction opportunities.

3. Passive sentence, but flagged token is still gold `Karma`.

Some sentences contain passive morphology, but converting the flagged token to Karta would be wrong.

Examples include:

- `स्तूप बनाए गए`
- `स्तूप ... कहा जाता है`
- `परत लगाई गई`
- `समारोह आयोजित किया जाता है`

### Likely error source

For true positives:

- parser error: likely, when Stanza marks a passive Karta-like participant as `obj`
- mapper limitation: yes, because `obj -> Karma` is too shallow for passive contexts
- verifier limitation: yes, because verifier v1 has no passive voice handling
- correction-layer limitation: yes, because v2.1 only handles locative `nmod`

For false positives:

- the diagnostic itself is too broad
- many `obj` rows are simply correct Karma cases

### Recommendation

`possible_passive_karta`: **NEEDS REFINEMENT**

Do not convert all flagged `obj` rows to Karta. A future rule should require stronger passive evidence, such as passive auxiliary evidence near the predicate and preferably a dependency/verb context check.

## possible_passive_karma

Definition currently captures:

`deprel == nsubj` and `final_candidates` does not contain Karma.

### Manual observations from first 50 examples

Approximate genuinely passive examples: **about 2 to 4 of 50**, or **4% to 8%**.

Approximate examples with explicit passive auxiliaries from the requested list: **about 1 of 50**, or **2%**.

Most examples are ordinary `nsubj` cases where gold is `Karta` and the current `Kartā` prediction is already correct.

### Recurring patterns

1. Ordinary subjects correctly predicted as Karta.

Examples include:

- `बुद्ध ने ... चुना`
- `राजधानी ... थी`
- `महत्व था`
- `प्रवेशद्वार ... स्वागत करता है`
- `लोग ... चाहते हैं`
- `होटल मौजूद हैं`

These are not passive correction opportunities.

2. Stative or adjectival constructions.

Examples include:

- `मूर्ति ... बनी है`
- `मंदिर ... स्थित है`
- `सुविधा उपलब्ध है`

These may be non-active or stative, but they do not by themselves justify converting Karta to Karma.

3. Rare non-Karta gold case.

One early example is:

- `देखना बहुत अच्छा लगता है`

Here gold is `Karma`, but the construction is more like an experiencer/stative predicate issue than a clear passive auxiliary pattern.

### Likely error source

For most examples:

- parser error: no
- mapper limitation: no, because `nsubj -> Kartā` is usually correct here
- verifier limitation: no, because the current final candidate is usually already correct
- correction-layer limitation: no

For the few non-Karta examples:

- mapper limitation or construction-specific limitation may be involved
- passive voice is not the main explanation

### Recommendation

`possible_passive_karma`: **FALSE LEAD** as currently defined for passive correction.

It mostly flags ordinary `nsubj` rows that are already correct as Karta. It should not become an automatic correction rule. If retained, it should be renamed or narrowed substantially.

## Cross-Diagnostic Conclusion

The current passive diagnostics are useful as broad probes, but not yet as correction-rule definitions.

Most promising future direction:

1. Start from `possible_passive_karta`, not `possible_passive_karma`.
2. Require explicit passive morphology in the sentence or predicate context.
3. Check whether the flagged token is attached to the passive predicate, not merely in a sentence that contains a passive auxiliary.
4. Separate true passive from ordinary active `obj -> Karma` cases.
5. Evaluate candidate rules on train/dev only before touching test.

Final recommendation: **NEEDS REFINEMENT**

Passive correction is worth investigating, but the next rule should not be based only on `deprel == obj` or `deprel == nsubj`. The diagnostic should become a narrower rule candidate only after adding voice-sensitive evidence.
