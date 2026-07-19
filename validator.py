from schemas import ClinicalReviewOutput
from clinical_tools import (
    calculate_patient_creatinine_clearance,
    check_geriatric_medication_risk,
)
from schemas import PatientCase


def validate_review(
    patient: PatientCase,
    review: ClinicalReviewOutput,
) -> list[str]:
    """
    Compare the LLM-generated structured review against the
    deterministic clinical engines.
    """

    errors = []

    renal = calculate_patient_creatinine_clearance(patient)

    if (
        abs(
            review.renal_assessment.creatinine_clearance_ml_min
            - renal["creatinine_clearance_ml_min"]
        )
        > 0.1
    ):
        errors.append(
            "Creatinine clearance does not match deterministic calculation."
        )

    findings = check_geriatric_medication_risk(patient)

    expected_rule_ids = {
        f["rule_id"] for f in findings
    }

    returned_rule_ids = {
        f.rule_id for f in review.medication_findings
    }

    if expected_rule_ids != returned_rule_ids:
        errors.append(
            "Medication findings do not match rule engine."
        )

    return errors