from schemas import Medication, PatientCase
from rule_engine import (
    check_geriatric_medication_risk,
    load_medication_rules,
)


def test_load_medication_rules():
    rules = load_medication_rules()

    assert len(rules) >= 4
    assert rules[0]["rule_id"] == "BEERS001"


def test_age_rule_returns_rule_match():
    patient = PatientCase(
        age=78,
        sex="female",
        weight_kg=52,
        serum_creatinine=1.2,
        medications=[
            Medication(
                name="Diazepam",
                dose="5 mg",
                frequency="once daily",
            )
        ],
    )

    findings = check_geriatric_medication_risk(patient)

    assert len(findings) == 1
    assert findings[0].rule_id == "BEERS001"
    assert findings[0].rule_type == "drug_age"
    assert findings[0].medication_names == ["Diazepam"]


def test_age_rule_is_case_insensitive():
    patient = PatientCase(
        age=78,
        sex="female",
        weight_kg=52,
        serum_creatinine=1.2,
        medications=[
            Medication(name="DIAZEPAM")
        ],
    )

    findings = check_geriatric_medication_risk(patient)

    assert len(findings) == 1
    assert findings[0].rule_id == "BEERS001"


def test_age_rule_does_not_match_below_threshold():
    patient = PatientCase(
        age=64,
        sex="male",
        weight_kg=75,
        serum_creatinine=1.0,
        medications=[
            Medication(name="diazepam")
        ],
    )

    findings = check_geriatric_medication_risk(patient)

    assert findings == []


def test_unlisted_medication_does_not_match():
    patient = PatientCase(
        age=80,
        sex="female",
        weight_kg=55,
        serum_creatinine=1.0,
        medications=[
            Medication(name="lisinopril")
        ],
    )

    findings = check_geriatric_medication_risk(patient)

    assert findings == []


def test_gabapentin_matches_reduced_renal_function_rule():
    patient = PatientCase(
        age=80,
        sex="female",
        weight_kg=50,
        serum_creatinine=1.5,
        medications=[
            Medication(
                name="Gabapentin",
                dose="300 mg",
                frequency="three times daily",
            )
        ],
    )

    findings = check_geriatric_medication_risk(patient)

    assert len(findings) == 1
    assert findings[0].rule_id == "RENAL001"
    assert findings[0].rule_type == "drug_renal"
    assert findings[0].severity == "moderate"
    assert findings[0].medication_names == ["Gabapentin"]
    assert findings[0].human_review_required is True


def test_gabapentin_does_not_match_with_preserved_renal_function():
    patient = PatientCase(
        age=65,
        sex="male",
        weight_kg=80,
        serum_creatinine=0.8,
        medications=[
            Medication(name="Gabapentin")
        ],
    )

    findings = check_geriatric_medication_risk(patient)

    assert findings == []
