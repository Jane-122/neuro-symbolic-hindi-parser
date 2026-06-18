"""
Prototype dependency-label repair layer.

This module does not modify heads, token order, or the original deprel field.
It only appends diagnostic repair columns to a copy of the input row.
"""


LOCATIVE_CASE_MARKERS = {"में", "पर"}
REPAIR_RULE_ID = "DR1_NMOD_LOCATIVE_TO_OBL"


def apply_dependency_repair(row):
    """
    Apply dependency-label repair v1 to one pipeline row.

    Returns a copy with:
    corrected_deprel, dependency_repair_applied,
    dependency_repair_rule_id, dependency_repair_type.
    """
    repaired_row = row.copy()
    deprel = row.get("deprel", "")
    case_marker = row.get("case_marker", "")

    if deprel == "nmod" and case_marker in LOCATIVE_CASE_MARKERS:
        repaired_row["corrected_deprel"] = "obl"
        repaired_row["dependency_repair_applied"] = True
        repaired_row["dependency_repair_rule_id"] = REPAIR_RULE_ID
        repaired_row["dependency_repair_type"] = "label_repair"
    else:
        repaired_row["corrected_deprel"] = deprel
        repaired_row["dependency_repair_applied"] = False
        repaired_row["dependency_repair_rule_id"] = ""
        repaired_row["dependency_repair_type"] = "none"

    return repaired_row
