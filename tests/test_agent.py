from schemas import (
    ClinicalReviewOutput,
    MedicationSafetyFinding,
    RenalAssessmentOutput,
)


def test_clinical_review_output_schema():
    review = ClinicalReviewOutput(
        patient_overview=(
            "78-year-old female with hypertension and insomnia."
        ),
        renal_assessment=RenalAssessmentOutput(
            method="Cockcroft-Gault",
            creatinine_clearance_ml_min=31.7,
            category="moderately reduced",
            limitations=[
                "Assumes stable serum creatinine.",
            ],
        ),
        medication_findings=[
            MedicationSafetyFinding(
                medication_name="Diazepam",
                rule_id="BEERS001",
                category="Avoid",
                severity="High",
                rationale=(
                    "Increased risk of falls and cognitive impairment"
                ),
                recommended_action="Avoid use",
                source_name="AGS Beers Criteria",
                source_year=2023,
            ),
        ],
        pharmacist_review_points=[
            "Review continued diazepam use.",
        ],
        unsupported_assumptions=[],
        human_review_required=True,
        disclaimer=(
            "This clinical decision support does not replace "
            "professional clinical judgment."
        ),
    )

    assert review.renal_assessment.method == "Cockcroft-Gault"
    assert review.renal_assessment.creatinine_clearance_ml_min == 31.7
    assert len(review.medication_findings) == 1
    assert review.medication_findings[0].rule_id == "BEERS001"
    assert review.human_review_required is True


def test_review_serializes_to_json():
    review = ClinicalReviewOutput(
        patient_overview="Older adult medication review.",
        renal_assessment=RenalAssessmentOutput(
            method="Cockcroft-Gault",
            creatinine_clearance_ml_min=31.7,
            category="moderately reduced",
            limitations=[],
        ),
        medication_findings=[],
        pharmacist_review_points=[],
        unsupported_assumptions=[],
        human_review_required=True,
        disclaimer="Clinical judgment is required.",
    )

    serialized = review.model_dump()

    assert serialized["human_review_required"] is True
    assert serialized["renal_assessment"]["method"] == "Cockcroft-Gault"
    assert serialized["medication_findings"] == []
