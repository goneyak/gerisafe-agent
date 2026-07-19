from typing import Literal

from pydantic import BaseModel, Field


RuleType = Literal[
    "drug_age",
    "drug_renal",
    "drug_condition",
    "drug_drug",
    "duplicate_therapy",
]

SeverityLevel = Literal[
    "low",
    "moderate",
    "high",
    "critical",
]


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


class RuleMatch(BaseModel):
    """
    Standardized output produced by the deterministic rule engine.

    RuleMatch represents a matched clinical safety rule before the
    result is transformed into the final user-facing review.
    """

    rule_id: str = Field(..., min_length=1)
    rule_type: RuleType
    severity: SeverityLevel

    medication_names: list[str] = Field(
        ...,
        min_length=1,
    )

    matched_conditions: list[str] = Field(
        default_factory=list,
    )

    category: str = Field(..., min_length=1)
    rationale: str = Field(..., min_length=1)
    recommended_action: str = Field(..., min_length=1)

    monitoring: str | None = None

    source_name: str = Field(..., min_length=1)
    source_year: int = Field(..., ge=1900, le=2100)

    human_review_required: Literal[True] = True


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