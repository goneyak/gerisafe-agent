from typing import Any

from renal_tools import (
    calculate_creatinine_clearance,
    calculate_patient_creatinine_clearance,
)
from rule_engine import check_geriatric_medication_risk
from schemas import PatientCase


def review_patient_case(
    patient: PatientCase,
) -> dict[str, Any]:
    """
    Perform a deterministic medication review by combining
    renal assessment and medication safety screening.
    """
    renal_assessment = (
        calculate_patient_creatinine_clearance(
            patient
        )
    )

    medication_findings = (
        check_geriatric_medication_risk(
            patient
        )
    )

    return {
        "patient_summary": {
            "age": patient.age,
            "sex": patient.sex,
            "medication_count": len(
                patient.medications
            ),
            "condition_count": len(
                patient.conditions
            ),
        },
        "renal_assessment": renal_assessment,
        "medication_findings": [
            finding.model_dump()
            for finding in medication_findings
        ],
        "finding_count": len(
            medication_findings
        ),
        "human_review_required": (
            len(medication_findings) > 0
        ),
        "disclaimer": (
            "This tool supports medication review and "
            "does not replace pharmacist or physician judgment."
        ),
    }