"""
Simple UD-to-Karaka mapper — Version 1.

Implements conservative deprel-only mappings from docs/ud_to_karaka_mapping_v1.md.
Postposition evidence and verifier integration are handled elsewhere.
"""


def _result(
    karaka_candidates: list[str],
    confidence: str,
    mapping_status: str,
    reason: str,
) -> dict:
    """Build a standard mapper result dictionary."""
    return {
        "karaka_candidates": karaka_candidates,
        "confidence": confidence,
        "mapping_status": mapping_status,
        "reason": reason,
    }


def _unsupported(deprel: str) -> dict:
    """Return when the deprel has no v1 mapping."""
    return _result(
        karaka_candidates=[],
        confidence="none",
        mapping_status="unsupported",
        reason=f"No v1 mapping defined for deprel={deprel!r}.",
    )


def map_ud_to_karaka(deprel: str) -> dict:
    """
    Map a UD dependency label to an initial Karaka hypothesis.

    This is a conservative, deprel-only mapping. It does not use postpositions
    and does not call the verifier.

    Args:
        deprel: The UD dependency label (e.g. "nsubj", "obj", "obl").

    Returns:
        Dictionary with keys:
            karaka_candidates, confidence, mapping_status, reason
    """
    if deprel == "nsubj":
        return _result(
            karaka_candidates=["Kartā"],
            confidence="low-medium",
            mapping_status="mapped",
            reason=(
                "nsubj is a grammatical subject; it may correspond to Kartā "
                "but is not always a semantic agent."
            ),
        )

    if deprel == "obj":
        return _result(
            karaka_candidates=["Karma"],
            confidence="medium",
            mapping_status="mapped",
            reason="obj typically marks the direct object (patient) of the action.",
        )

    if deprel == "iobj":
        return _result(
            karaka_candidates=["Sampradāna"],
            confidence="medium",
            mapping_status="mapped",
            reason="iobj often marks a recipient or beneficiary of the action.",
        )

    if deprel == "obl":
        return _result(
            karaka_candidates=["Adhikaraṇa", "Apādāna", "Karaṇa"],
            confidence="low",
            mapping_status="context_dependent",
            reason=(
                "obl is context-dependent; the Karaka role depends on "
                "postposition and verb semantics, not deprel alone."
            ),
        )

    if deprel == "root":
        return _result(
            karaka_candidates=[],
            confidence="high",
            mapping_status="no_karaka",
            reason=(
                "root is the predicate anchor; Karakas apply to dependents, "
                "not to the verb itself."
            ),
        )

    if deprel == "case":
        return _result(
            karaka_candidates=[],
            confidence="high",
            mapping_status="evidence_only",
            reason=(
                "case marks postpositions; it is evidence for the parent's "
                "Karaka, not a Karaka role itself."
            ),
        )

    return _unsupported(deprel)


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    examples = [
        "nsubj",
        "obj",
        "iobj",
        "obl",
        "root",
        "case",
        "det",      # unsupported
        "amod",     # unsupported
    ]

    for deprel in examples:
        result = map_ud_to_karaka(deprel)
        print(f"map_ud_to_karaka({deprel!r})")
        print(f"  candidates: {result['karaka_candidates']}")
        print(f"  confidence:  {result['confidence']}")
        print(f"  status:      {result['mapping_status']}")
        print(f"  reason:      {result['reason']}")
        print()
