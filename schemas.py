from typing import Literal

from pydantic import BaseModel, Field


class Medication(BaseModel):
    name: str = Field(..., min_length=1)
    dose: str | None = None
    frequency: str | None = None


class Labs(BaseModel):
    potassium: float | None = None
    sodium: float | None = None


class PatientCase(BaseModel):
    age: int = Field(..., ge=18, le=120)
    sex: Literal["male", "female"]
    weight_kg: float = Field(..., gt=0)
    serum_creatinine: float = Field(..., gt=0)

    conditions: list[str] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    labs: Labs = Field(default_factory=Labs)


class MedicationSafetyFinding(BaseModel):
    medication_name: str
    rule_id: str
    category: str
    severity: str
    rationale: str
    recommended_action: str
    source_name: str
    source_year: int


class RenalAssessmentOutput(BaseModel):
    method: str
    creatinine_clearance_ml_min: float
    category: str
    limitations: list[str]


class ClinicalReviewOutput(BaseModel):
    patient_overview: str
    renal_assessment: RenalAssessmentOutput
    medication_findings: list[MedicationSafetyFinding]
    pharmacist_review_points: list[str]
    unsupported_assumptions: list[str]
    human_review_required: Literal[True]
    disclaimer: str