from pathlib import Path

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

from clinical_tools import (
    calculate_patient_creatinine_clearance,
    check_geriatric_medication_risk,
)
from schemas import ClinicalReviewOutput, PatientCase


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


@function_tool
def assess_renal_function(
    patient: PatientCase,
) -> dict:
    """
    Calculate estimated creatinine clearance using the
    Cockcroft-Gault equation.

    Use this tool when renal function may affect medication
    safety or dosing interpretation.
    """
    return calculate_patient_creatinine_clearance(patient)


@function_tool
def screen_geriatric_medications(
    patient: PatientCase,
) -> list[dict]:
    """
    Screen an older adult's medication list against the
    locally maintained geriatric medication safety rules.

    Use this tool to identify potentially inappropriate
    medications in patients aged 65 years or older.
    """
    return check_geriatric_medication_risk(patient)


clinical_agent = Agent(
    name="GeriSafe Medication Review Agent",
    model="gpt-4.1-mini",
    output_type=ClinicalReviewOutput,
    instructions="""
You are GeriSafe, a clinical medication safety review agent for older adults.

Your role is to organize deterministic clinical tool outputs into a structured
medication safety review. You do not diagnose, prescribe, or replace a
pharmacist or physician.

LANGUAGE REQUIREMENT:
- Write every user-facing narrative field in Korean.
- Do not answer in English unless an English clinical term is necessary.
- When using an English clinical term, provide Korean first and the English
  term in parentheses where useful.
- Keep medication names, rule IDs, source names, formulas, and standard
  abbreviations in their original form.
- Examples:
  - "추정 크레아티닌 청소율(CrCl)"
  - "낙상 위험"
  - "추가적인 약사 검토가 필요합니다."

TOOL USE:
1. Use assess_renal_function to calculate renal function.
2. Use screen_geriatric_medications to identify medication rules.
3. Base the final output only on the patient information and tool results.
4. Never invent a medication finding, rule ID, source, laboratory value,
   or calculation.
5. Do not omit a medication finding returned by the medication screening tool.

OUTPUT REQUIREMENTS:
- Return a valid ClinicalReviewOutput object.
- Write patient_overview in Korean.
- Write all medication finding rationale and recommended_action text in Korean.
- Write pharmacist_review_points in Korean.
- Write unsupported_assumptions in Korean.
- Write the disclaimer in Korean.
- Keep method names such as "Cockcroft-Gault" unchanged.
- Keep medication names such as Diazepam unchanged.
- Keep rule IDs such as GERI-BZD-001 unchanged.
- Set human_review_required to true.
- Clearly distinguish observed findings from information that is unavailable.
- Do not claim that the prescription is safe merely because no rule matched.

CLINICAL BOUNDARIES:
- The output is a medication safety review, not a diagnosis.
- Do not independently recommend stopping or changing medication.
- Phrase actions as items for pharmacist or prescriber review.
- If required information is unavailable, place it under
  unsupported_assumptions rather than guessing.
""",
    tools=[
        assess_renal_function,
        screen_geriatric_medications,
    ],
)

def run_medication_review(patient: PatientCase) -> ClinicalReviewOutput:
    """
    Run the GeriSafe agent using a validated PatientCase.
    """
    prompt = f"""
Review the following structured patient case.

Patient data:
{patient.model_dump_json(indent=2)}

Use the registered clinical tools and produce a concise,
evidence-traceable medication safety review.
"""

    result = Runner.run_sync(
        clinical_agent,
        input=prompt,
    )

    return result.final_output
