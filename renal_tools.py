from typing import Any

from schemas import PatientCase


def calculate_creatinine_clearance(
    age: int,
    sex: str,
    weight_kg: float,
    serum_creatinine: float,
) -> dict[str, Any]:
    """
    Estimate creatinine clearance using the Cockcroft-Gault equation.
    """
    if not 18 <= age <= 120:
        raise ValueError("age must be between 18 and 120")

    if sex not in {"male", "female"}:
        raise ValueError("sex must be 'male' or 'female'")

    if weight_kg <= 0:
        raise ValueError("weight_kg must be greater than 0")

    if serum_creatinine <= 0:
        raise ValueError(
            "serum_creatinine must be greater than 0"
        )

    creatinine_clearance = (
        (140 - age) * weight_kg
    ) / (72 * serum_creatinine)

    if sex == "female":
        creatinine_clearance *= 0.85

    creatinine_clearance = round(
        creatinine_clearance,
        1,
    )

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
        "creatinine_clearance_ml_min": (
            creatinine_clearance
        ),
        "category": category,
        "inputs": {
            "age": age,
            "sex": sex,
            "weight_kg": weight_kg,
            "serum_creatinine_mg_dl": (
                serum_creatinine
            ),
        },
        "assumptions": [
            "Serum creatinine is measured in mg/dL.",
            "Body weight is measured in kilograms.",
            "Renal function is stable.",
        ],
        "limitations": [
            (
                "Cockcroft-Gault creatinine clearance "
                "is not interchangeable with eGFR."
            ),
            (
                "Weight selection may require clinical "
                "adjustment in underweight or obese patients."
            ),
            (
                "The estimate may be unreliable in acute "
                "kidney injury or rapidly changing renal function."
            ),
        ],
    }


def calculate_patient_creatinine_clearance(
    patient: PatientCase,
) -> dict[str, Any]:
    """
    Calculate Cockcroft-Gault CrCl from a PatientCase.
    """
    return calculate_creatinine_clearance(
        age=patient.age,
        sex=patient.sex,
        weight_kg=patient.weight_kg,
        serum_creatinine=patient.serum_creatinine,
    )