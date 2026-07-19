from typing import Any

from rule_engine import check_geriatric_medication_risk
from schemas import PatientCase


def calculate_creatinine_clearance(
    age: int,
    sex: str,
    weight_kg: float,
    serum_creatinine: float,
) -> dict[str, Any]:
    """
    Estimate creatinine clearance using the Cockcroft-Gault equation.

    Assumptions:
    - Serum creatinine is expressed in mg/dL.
    - Weight is expressed in kilograms.
    - Renal function is reasonably stable.
    - The result is an estimate for medication review, not a substitute
      for clinical judgment.
    """
    if not 18 <= age <= 120:
        raise ValueError("age must be between 18 and 120")

    if sex not in {"male", "female"}:
        raise ValueError("sex must be 'male' or 'female'")

    if weight_kg <= 0:
        raise ValueError("weight_kg must be greater than 0")

    if serum_creatinine <= 0:
        raise ValueError("serum_creatinine must be greater than 0")

    creatinine_clearance = (
        (140 - age) * weight_kg
    ) / (72 * serum_creatinine)

    if sex == "female":
        creatinine_clearance *= 0.85

    creatinine_clearance = round(creatinine_clearance, 1)

    if creatinine_clearance < 30:
        category = "severely reduced"
    elif creatinine_clearance < 60:
        category = "moderately reduced"
    elif creatinine_clearance < 90:
        category = "mildly reduced"
    else:
        category = "within expected range"

    return {
        "method": "Cockcroft-Gault",
        "creatinine_clearance_ml_min": creatinine_clearance,
        "category": category,
        "inputs": {
            "age": age,
            "sex": sex,
            "weight_kg": weight_kg,
            "serum_creatinine_mg_dl": serum_creatinine,
        },
        "assumptions": [
            "Serum creatinine is measured in mg/dL.",
            "Body weight is measured in kilograms.",
            "Renal function is stable.",
        ],
        "limitations": [
            "Cockcroft-Gault creatinine clearance is not interchangeable with eGFR.",
            "Weight selection may require clinical adjustment in underweight or obese patients.",
            "The estimate may be unreliable in acute kidney injury or rapidly changing renal function.",
        ],
    }


def calculate_patient_creatinine_clearance(
    patient: PatientCase,
) -> dict[str, Any]:
    """
    Convenience wrapper for PatientCase objects.
    """
    return calculate_creatinine_clearance(
        age=patient.age,
        sex=patient.sex,
        weight_kg=patient.weight_kg,
        serum_creatinine=patient.serum_creatinine,
    )


def review_patient_case(
    patient: PatientCase,
) -> dict[str, Any]:
    """
    Perform a deterministic medication review by combining
    renal assessment and geriatric medication screening.
    """
    renal_assessment = calculate_patient_creatinine_clearance(
        patient
    )

    medication_findings = check_geriatric_medication_risk(
        patient
    )

    return {
        "patient_summary": {
            "age": patient.age,
            "sex": patient.sex,
            "medication_count": len(patient.medications),
            "condition_count": len(patient.conditions),
        },
        "renal_assessment": renal_assessment,
        "medication_findings": medication_findings,
        "finding_count": len(medication_findings),
        "human_review_required": (
            len(medication_findings) > 0
        ),
        "disclaimer": (
            "This tool supports medication review and "
            "does not replace pharmacist or physician judgment."
        ),
    }