import pytest

from clinical_tools import calculate_creatinine_clearance


def test_calculates_creatinine_clearance_for_female():
    result = calculate_creatinine_clearance(
        age=78,
        sex="female",
        weight_kg=52,
        serum_creatinine=1.2,
    )

    assert result["method"] == "Cockcroft-Gault"
    assert result["creatinine_clearance_ml_min"] == pytest.approx(
        31.7,
        abs=0.1,
    )
    assert result["category"] == "moderately reduced"


def test_calculates_creatinine_clearance_for_male():
    result = calculate_creatinine_clearance(
        age=70,
        sex="male",
        weight_kg=70,
        serum_creatinine=1.0,
    )

    assert result["creatinine_clearance_ml_min"] == pytest.approx(
        68.1,
        abs=0.1,
    )
    assert result["category"] == "mildly reduced"


def test_rejects_nonpositive_serum_creatinine():
    with pytest.raises(
        ValueError,
        match="serum_creatinine must be greater than 0",
    ):
        calculate_creatinine_clearance(
            age=78,
            sex="female",
            weight_kg=52,
            serum_creatinine=0,
        )


def test_rejects_invalid_sex():
    with pytest.raises(
        ValueError,
        match="sex must be 'male' or 'female'",
    ):
        calculate_creatinine_clearance(
            age=78,
            sex="unknown",
            weight_kg=52,
            serum_creatinine=1.2,
        )


from schemas import Labs, Medication, PatientCase
from clinical_tools import check_geriatric_medication_risk


def test_flags_listed_medication_for_older_adult():
    patient = PatientCase(
        age=78,
        sex="female",
        weight_kg=52,
        serum_creatinine=1.2,
        conditions=["insomnia"],
        medications=[
            Medication(
                name="Diazepam",
                dose="5 mg",
                frequency="once daily",
            ),
            Medication(
                name="lisinopril",
                dose="10 mg",
                frequency="once daily",
            ),
        ],
        labs=Labs(
            potassium=4.5,
            sodium=138,
        ),
    )

    findings = check_geriatric_medication_risk(patient)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "BEERS001"
    assert findings[0]["medication"]["name"] == "Diazepam"
    assert findings[0]["severity"] == "High"
    assert findings[0]["human_review_required"] is True


def test_does_not_apply_rule_below_minimum_age():
    patient = PatientCase(
        age=50,
        sex="male",
        weight_kg=75,
        serum_creatinine=1.0,
        conditions=["insomnia"],
        medications=[
            Medication(
                name="zolpidem",
                dose="5 mg",
                frequency="at bedtime",
            )
        ],
        labs=Labs(),
    )

    findings = check_geriatric_medication_risk(patient)

    assert findings == []


def test_does_not_flag_unlisted_medication():
    patient = PatientCase(
        age=80,
        sex="female",
        weight_kg=55,
        serum_creatinine=1.1,
        conditions=["hypertension"],
        medications=[
            Medication(
                name="amlodipine",
                dose="5 mg",
                frequency="once daily",
            )
        ],
        labs=Labs(),
    )

    findings = check_geriatric_medication_risk(patient)

    assert findings == []


from schemas import Labs, Medication, PatientCase
from clinical_tools import check_geriatric_medication_risk


def test_flags_listed_medication_for_older_adult():
    patient = PatientCase(
        age=78,
        sex="female",
        weight_kg=52,
        serum_creatinine=1.2,
        conditions=["insomnia"],
        medications=[
            Medication(
                name="Diazepam",
                dose="5 mg",
                frequency="once daily",
            ),
            Medication(
                name="lisinopril",
                dose="10 mg",
                frequency="once daily",
            ),
        ],
        labs=Labs(
            potassium=4.5,
            sodium=138,
        ),
    )

    findings = check_geriatric_medication_risk(patient)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "BEERS001"
    assert findings[0]["medication"]["name"] == "Diazepam"
    assert findings[0]["severity"] == "High"
    assert findings[0]["human_review_required"] is True


def test_does_not_apply_rule_below_minimum_age():
    patient = PatientCase(
        age=50,
        sex="male",
        weight_kg=75,
        serum_creatinine=1.0,
        conditions=["insomnia"],
        medications=[
            Medication(
                name="zolpidem",
                dose="5 mg",
                frequency="at bedtime",
            )
        ],
        labs=Labs(),
    )

    findings = check_geriatric_medication_risk(patient)

    assert findings == []


def test_does_not_flag_unlisted_medication():
    patient = PatientCase(
        age=80,
        sex="female",
        weight_kg=55,
        serum_creatinine=1.1,
        conditions=["hypertension"],
        medications=[
            Medication(
                name="amlodipine",
                dose="5 mg",
                frequency="once daily",
            )
        ],
        labs=Labs(),
    )

    findings = check_geriatric_medication_risk(patient)

    assert findings == []


from clinical_tools import review_patient_case


def test_review_patient_case():
    patient = PatientCase(
        age=78,
        sex="female",
        weight_kg=52,
        serum_creatinine=1.2,
        conditions=["hypertension", "insomnia"],
        medications=[
            Medication(
                name="Diazepam",
                dose="5 mg",
                frequency="once daily",
            )
        ],
        labs=Labs(
            potassium=4.5,
            sodium=138,
        ),
    )

    result = review_patient_case(patient)

    assert result["finding_count"] == 1
    assert result["human_review_required"] is True
    assert result["renal_assessment"]["method"] == "Cockcroft-Gault"
