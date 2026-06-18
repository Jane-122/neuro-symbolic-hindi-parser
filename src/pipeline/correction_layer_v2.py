"""
Small conservative correction layer applied after verifier v1.

This module is intentionally independent: it accepts one existing pipeline row
dictionary and returns a copy with correction and diagnostic columns appended.
"""


LOCATIVE_CASE_MARKERS = {"में", "पर"}
CORRECTION_RULE_ID = "H1_NMOD_LOCATIVE_ADHIKARANA"

KARTA_LABELS = {"Karta", "Kartā"}
KARMA_LABELS = {"Karma"}


def split_candidates(candidate_text):
    """Split a pipe-separated candidate string into a set of labels."""
    if not candidate_text:
        return set()
    return {candidate for candidate in candidate_text.split("|") if candidate}


def contains_any_label(candidate_text, labels):
    """Return true if any label appears in a pipe-separated candidate string."""
    candidates = split_candidates(candidate_text)
    return any(label in candidates for label in labels)


def diagnostic_flag(row):
    """Return the diagnostic-only flag for one pipeline row."""
    deprel = row.get("deprel", "")
    case_marker = row.get("case_marker", "")
    final_candidates = row.get("final_candidates", "")

    if deprel == "obj" and not contains_any_label(final_candidates, KARTA_LABELS):
        return "possible_passive_karta"

    if deprel == "nsubj" and not contains_any_label(final_candidates, KARMA_LABELS):
        return "possible_passive_karma"

    if deprel == "obl" and case_marker == "से":
        return "se_ambiguous_requires_verb_context"

    return ""


def apply_correction(row):
    """
    Apply H1 correction and diagnostic flags to one pipeline row.

    Returns a copy with:
    corrected_candidates, correction_applied, correction_rule_id,
    correction_type, diagnostic_flag.
    """
    corrected_row = row.copy()
    final_candidates = row.get("final_candidates", "")

    if row.get("deprel", "") == "nmod" and row.get("case_marker", "") in LOCATIVE_CASE_MARKERS:
        corrected_row["corrected_candidates"] = "Adhikarana"
        corrected_row["correction_applied"] = True
        corrected_row["correction_rule_id"] = CORRECTION_RULE_ID
        corrected_row["correction_type"] = "safe_override"
    else:
        corrected_row["corrected_candidates"] = final_candidates
        corrected_row["correction_applied"] = False
        corrected_row["correction_rule_id"] = ""
        corrected_row["correction_type"] = "none"

    corrected_row["diagnostic_flag"] = diagnostic_flag(row)
    return corrected_row
