import pytest
from pydantic import ValidationError

from schemas import RuleMatch


def test_rule_match_accepts_valid_age_rule():
    rule_match = RuleMatch(
        rule_id="GERI-BZD-001",
        rule_type="drug_age",
        severity="high",
        medication_names=["Diazepam"],
        matched_conditions=["age >= 65"],
        category="Potentially inappropriate medication",
        rationale=(
            "Older adults have increased sensitivity to "
            "benzodiazepines."
        ),
        recommended_action=(
            "Review continued need and consider safer alternatives."
        ),
        monitoring="Monitor sedation, cognition, and fall risk.",
        source_name="AGS Beers Criteria",
        source_year=2023,
    )

    assert rule_match.rule_id == "GERI-BZD-001"
    assert rule_match.rule_type == "drug_age"
    assert rule_match.severity == "high"
    assert rule_match.medication_names == ["Diazepam"]
    assert rule_match.human_review_required is True


def test_rule_match_supports_multiple_medications():
    rule_match = RuleMatch(
        rule_id="DDI-CNS-001",
        rule_type="drug_drug",
        severity="critical",
        medication_names=[
            "Diazepam",
            "Oxycodone",
        ],
        matched_conditions=[
            "benzodiazepine present",
            "opioid present",
        ],
        category="CNS depressant interaction",
        rationale=(
            "Concurrent use may increase sedation and "
            "respiratory depression risk."
        ),
        recommended_action=(
            "Request pharmacist or prescriber review."
        ),
        source_name="Example Evidence Source",
        source_year=2024,
    )

    assert len(rule_match.medication_names) == 2
    assert rule_match.rule_type == "drug_drug"


def test_rule_match_rejects_unknown_rule_type():
    with pytest.raises(ValidationError):
        RuleMatch(
            rule_id="INVALID-001",
            rule_type="unknown_rule",
            severity="high",
            medication_names=["Diazepam"],
            category="Invalid rule",
            rationale="Invalid rule type.",
            recommended_action="Review.",
            source_name="Example Source",
            source_year=2024,
        )


def test_rule_match_requires_at_least_one_medication():
    with pytest.raises(ValidationError):
        RuleMatch(
            rule_id="GERI-BZD-001",
            rule_type="drug_age",
            severity="high",
            medication_names=[],
            category="Potentially inappropriate medication",
            rationale="Example rationale.",
            recommended_action="Review medication.",
            source_name="AGS Beers Criteria",
            source_year=2023,
        )