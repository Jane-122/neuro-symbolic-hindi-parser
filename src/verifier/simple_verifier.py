"""
Simple Paninian verifier — Version 1.

Implements rules R1–R5 from docs/rule_specification_v1.md.
Evaluates a parent token's UD deprel together with an optional case marker
(postposition form from a child case token).
"""

from typing import Optional


def _result(
    karaka_candidates: list[str],
    decision_type: str,
    confidence: str,
    rule_id: Optional[str],
    reason: str,
) -> dict:
    """Build a standard verifier result dictionary."""
    return {
        "karaka_candidates": karaka_candidates,
        "decision_type": decision_type,
        "confidence": confidence,
        "rule_id": rule_id,
        "reason": reason,
    }


def _no_decision(reason: str) -> dict:
    """Return when no v1 rule applies."""
    return _result(
        karaka_candidates=[],
        decision_type="no_decision",
        confidence="none",
        rule_id=None,
        reason=reason,
    )


def verify_token(deprel: str, case_marker: Optional[str]) -> dict:
    """
    Apply v1 verifier rules to one token.

    Args:
        deprel: The UD dependency label of the parent token (e.g. "nsubj", "obl").
        case_marker: The postposition form from a child case token (e.g. "ने"),
                     or None if no case child is present.

    Returns:
        Dictionary with keys:
            karaka_candidates, decision_type, confidence, rule_id, reason
    """
    # No postposition evidence — no v1 rule can fire.
    if not case_marker:
        return _no_decision("No case marker provided; v1 rules require postposition evidence.")

    # R1: nsubj + ने → Kartā (confirmed)
    if deprel == "nsubj" and case_marker == "ने":
        return _result(
            karaka_candidates=["Kartā"],
            decision_type="confirmed",
            confidence="high",
            rule_id="R1",
            reason="nsubj with ने postposition — strong agent/subject evidence for Kartā.",
        )

    # R2: obl + में → Adhikaraṇa (confirmed)
    if deprel == "obl" and case_marker == "में":
        return _result(
            karaka_candidates=["Adhikaraṇa"],
            decision_type="confirmed",
            confidence="medium-high",
            rule_id="R2",
            reason="obl with में postposition — locative/locus pattern for Adhikaraṇa.",
        )

    # R3: obl + पर → Adhikaraṇa (confirmed)
    if deprel == "obl" and case_marker == "पर":
        return _result(
            karaka_candidates=["Adhikaraṇa"],
            decision_type="confirmed",
            confidence="medium-high",
            rule_id="R3",
            reason="obl with पर postposition — surface/location pattern for Adhikaraṇa.",
        )

    # R4: obl + से → Karaṇa or Apādāna (ambiguous)
    if deprel == "obl" and case_marker == "से":
        return _result(
            karaka_candidates=["Karaṇa", "Apādāna"],
            decision_type="ambiguous",
            confidence="low-medium",
            rule_id="R4",
            reason="obl with से postposition — instrument (Karaṇa) or source (Apādāna); cannot disambiguate in v1.",
        )

    # R5: obj/iobj + को → Karma or Sampradāna (ambiguous)
    if deprel in ("obj", "iobj") and case_marker == "को":
        return _result(
            karaka_candidates=["Karma", "Sampradāna"],
            decision_type="ambiguous",
            confidence="low-medium",
            rule_id="R5",
            reason="obj/iobj with को postposition — patient (Karma) or recipient (Sampradāna); cannot disambiguate in v1.",
        )

    # No matching rule (e.g. nsubj without ने, obl + को, ने on non-nsubj).
    return _no_decision(
        f"No v1 rule applies for deprel={deprel!r} with case_marker={case_marker!r}."
    )


if __name__ == "__main__":
    import sys

    # Allow Hindi postpositions in terminal output on Windows.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # Simple manual tests — one example per rule plus no_decision cases.

    examples = [
        # R1 — confirmed Kartā
        ("nsubj", "ने"),
        # R2 — confirmed Adhikaraṇa
        ("obl", "में"),
        # R3 — confirmed Adhikaraṇa
        ("obl", "पर"),
        # R4 — ambiguous Karaṇa / Apādāna
        ("obl", "से"),
        # R5 — ambiguous Karma / Sampradāna
        ("obj", "को"),
        ("iobj", "को"),
        # no_decision cases
        ("nsubj", None),
        ("nsubj", "को"),
        ("obl", "को"),
        ("obl", "ने"),
    ]

    for deprel, case_marker in examples:
        result = verify_token(deprel, case_marker)
        print(f"verify_token({deprel!r}, {case_marker!r})")
        print(f"  rule_id:     {result['rule_id']}")
        print(f"  decision:    {result['decision_type']}")
        print(f"  confidence:  {result['confidence']}")
        print(f"  candidates:  {result['karaka_candidates']}")
        print(f"  reason:      {result['reason']}")
        print()
