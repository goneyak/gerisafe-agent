from __future__ import annotations

import html
import time
from typing import Any

import streamlit as st
from pydantic import ValidationError

from agent import run_medication_review
from schemas import Labs, Medication, PatientCase
from validator import validate_review


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="GeriSafe",
    page_icon="👵",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# Constants
# =========================================================

STEP_HOME = 0
STEP_PATIENT = 1
STEP_CLINICAL = 2
STEP_MEDICATIONS = 3
STEP_ANALYSIS = 4
STEP_RESULTS = 5


EXAMPLE_CASES = {
    "diazepam": {
        "label": "78세 여성 · 불면증",
        "description": "Diazepam 복용 중인 고령 환자",
        "age": 78,
        "sex": "female",
        "weight_kg": 52.0,
        "serum_creatinine": 1.2,
        "potassium": 4.5,
        "sodium": 138.0,
        "conditions": "hypertension, insomnia",
        "medications": [
            {
                "name": "Diazepam",
                "dose": "5 mg",
                "frequency": "once daily",
            },
            {
                "name": "Lisinopril",
                "dose": "10 mg",
                "frequency": "once daily",
            },
        ],
    },
    "zolpidem": {
        "label": "82세 남성 · 수면장애",
        "description": "Zolpidem 복용 중인 고령 환자",
        "age": 82,
        "sex": "male",
        "weight_kg": 64.0,
        "serum_creatinine": 1.4,
        "potassium": 4.3,
        "sodium": 139.0,
        "conditions": "hypertension, sleep disorder",
        "medications": [
            {
                "name": "Zolpidem",
                "dose": "10 mg",
                "frequency": "at bedtime",
            },
            {
                "name": "Amlodipine",
                "dose": "5 mg",
                "frequency": "once daily",
            },
        ],
    },
    "glyburide": {
        "label": "74세 여성 · 당뇨병",
        "description": "Glyburide 복용 중인 고령 환자",
        "age": 74,
        "sex": "female",
        "weight_kg": 57.0,
        "serum_creatinine": 1.1,
        "potassium": 4.6,
        "sodium": 137.0,
        "conditions": "type 2 diabetes, hypertension",
        "medications": [
            {
                "name": "Glyburide",
                "dose": "5 mg",
                "frequency": "once daily",
            },
            {
                "name": "Losartan",
                "dose": "50 mg",
                "frequency": "once daily",
            },
        ],
    },
}


# =========================================================
# CSS
# =========================================================

st.html(
    """
    <style>
    :root {
        --background: #f7f8fa;
        --surface: #ffffff;
        --surface-soft: #f9fafb;
        --text-primary: #191f28;
        --text-secondary: #4e5968;
        --text-tertiary: #8b95a1;
        --border: #e5e8eb;
        --blue: #3182f6;
        --blue-dark: #1b64da;
        --blue-soft: #eaf3ff;
        --green: #00a878;
        --green-soft: #e8faf3;
        --orange: #f59e0b;
        --orange-soft: #fff6e5;
        --red: #e5484d;
        --red-soft: #fff0f0;
    }

    .stApp {
        background: var(--background);
        color: var(--text-primary);
    }

    .block-container {
        max-width: 760px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    html,
    body,
    [class*="css"] {
        font-family:
            Inter,
            Pretendard,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    h1,
    h2,
    h3,
    h4 {
        color: var(--text-primary);
        letter-spacing: -0.035em;
    }

    p {
        color: var(--text-secondary);
    }

    /* Header */

    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.2rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }

    .brand-icon {
        display: flex;
        width: 38px;
        height: 38px;
        align-items: center;
        justify-content: center;
        border-radius: 13px;
        background: var(--blue);
        color: white;
        font-size: 1.15rem;
        box-shadow: 0 7px 18px rgba(49, 130, 246, 0.22);
    }

    .brand-name {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 800;
        letter-spacing: -0.035em;
    }

    .prototype-badge {
        padding: 0.4rem 0.65rem;
        border-radius: 999px;
        background: var(--blue-soft);
        color: var(--blue-dark);
        font-size: 0.72rem;
        font-weight: 800;
    }

    /* Hero */

    .hero {
        padding: 2.3rem 1.8rem;
        margin-bottom: 1.2rem;
        border: 1px solid var(--border);
        border-radius: 28px;
        background:
            radial-gradient(
                circle at 90% 10%,
                rgba(49, 130, 246, 0.15),
                transparent 35%
            ),
            var(--surface);
        box-shadow: 0 16px 44px rgba(25, 31, 40, 0.06);
    }

    .hero-eyebrow {
        margin-bottom: 0.75rem;
        color: var(--blue);
        font-size: 0.78rem;
        font-weight: 800;
    }

    .hero-title {
        max-width: 560px;
        margin: 0;
        color: var(--text-primary);
        font-size: clamp(2rem, 6vw, 3.3rem);
        font-weight: 850;
        line-height: 1.14;
        letter-spacing: -0.06em;
    }

    .hero-description {
        max-width: 560px;
        margin-top: 1rem;
        margin-bottom: 0;
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.7;
    }

    .trust-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1.4rem;
    }

    .trust-chip {
        padding: 0.48rem 0.68rem;
        border: 1px solid var(--border);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.85);
        color: var(--text-secondary);
        font-size: 0.76rem;
        font-weight: 700;
    }

    /* Progress */

    .progress-wrap {
        margin-bottom: 1.2rem;
    }

    .progress-label-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.55rem;
    }

    .progress-label {
        color: var(--text-secondary);
        font-size: 0.76rem;
        font-weight: 700;
    }

    .progress-step {
        color: var(--blue);
        font-size: 0.76rem;
        font-weight: 800;
    }

    .progress-track {
        height: 7px;
        overflow: hidden;
        border-radius: 999px;
        background: #e9edf2;
    }

    .progress-fill {
        height: 100%;
        border-radius: 999px;
        background: var(--blue);
        transition: width 0.3s ease;
    }

    /* Section */

    .page-title {
        margin-top: 0.5rem;
        margin-bottom: 0.45rem;
        color: var(--text-primary);
        font-size: 1.75rem;
        font-weight: 850;
        letter-spacing: -0.045em;
    }

    .page-description {
        margin-bottom: 1.25rem;
        color: var(--text-tertiary);
        font-size: 0.94rem;
        line-height: 1.6;
    }

    /* Cards */

    .info-card,
    .result-card,
    .example-card,
    .finding-card,
    .loading-card {
        border: 1px solid var(--border);
        border-radius: 22px;
        background: var(--surface);
        box-shadow: 0 8px 28px rgba(25, 31, 40, 0.045);
    }

    .info-card {
        padding: 1.25rem;
    }

    .feature-card {
        height: 100%;
        padding: 1.15rem;
        border: 1px solid var(--border);
        border-radius: 20px;
        background: var(--surface);
    }

    .feature-icon {
        display: flex;
        width: 40px;
        height: 40px;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.9rem;
        border-radius: 13px;
        background: var(--blue-soft);
        font-size: 1.1rem;
    }

    .feature-title {
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 800;
    }

    .feature-copy {
        margin-top: 0.35rem;
        color: var(--text-tertiary);
        font-size: 0.8rem;
        line-height: 1.55;
    }

    .section-label {
        margin-bottom: 0.8rem;
        color: var(--text-primary);
        font-size: 1rem;
        font-weight: 800;
    }

    /* Native Streamlit containers */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--border) !important;
        border-radius: 22px !important;
        background: var(--surface);
        box-shadow: 0 8px 28px rgba(25, 31, 40, 0.045);
    }

    /* Inputs */

    label[data-testid="stWidgetLabel"] p {
        color: var(--text-secondary);
        font-size: 0.84rem;
        font-weight: 750;
    }

    /* 모든 primary 버튼: 파란 배경 + 흰색 글씨 */

    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        background-color: var(--blue) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 10px 24px rgba(49, 130, 246, 0.22);
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Streamlit 내부 요소까지 흰색 고정 */

    div[data-testid="stButton"] button *,
    div[data-testid="stFormSubmitButton"] button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* 마우스를 올렸을 때 */

    div[data-testid="stButton"] button:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: var(--blue-dark) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* 버튼을 눌렀을 때도 흰색 유지 */

    div[data-testid="stButton"] button:active,
    div[data-testid="stFormSubmitButton"] button:active {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Example case */

    .example-case {
        padding: 0.25rem 0;
    }

    .example-label {
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 800;
    }

    .example-description {
        margin-top: 0.25rem;
        color: var(--text-tertiary);
        font-size: 0.78rem;
    }

    /* Analysis */

    .analysis-hero {
        padding: 2.1rem 1.5rem;
        text-align: center;
    }

    .analysis-icon {
        display: flex;
        width: 72px;
        height: 72px;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.15rem;
        border-radius: 24px;
        background: var(--blue-soft);
        font-size: 2rem;
    }

    .analysis-title {
        margin: 0;
        color: var(--text-primary);
        font-size: 1.45rem;
        font-weight: 850;
    }

    .analysis-copy {
        margin-top: 0.55rem;
        color: var(--text-tertiary);
        font-size: 0.88rem;
        line-height: 1.55;
    }

    .analysis-item {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        padding: 0.9rem 0;
        border-bottom: 1px solid #f0f2f5;
    }

    .analysis-item:last-child {
        border-bottom: 0;
    }

    .analysis-check {
        display: flex;
        flex: 0 0 30px;
        width: 30px;
        height: 30px;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: var(--green-soft);
        color: var(--green);
        font-size: 0.8rem;
        font-weight: 900;
    }

    .analysis-item-title {
        color: var(--text-primary);
        font-size: 0.88rem;
        font-weight: 750;
    }

    .analysis-item-copy {
        margin-top: 0.12rem;
        color: var(--text-tertiary);
        font-size: 0.75rem;
    }

    /* Metrics */

    div[data-testid="stMetric"] {
        padding: 1.05rem;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: var(--surface);
        box-shadow: 0 8px 24px rgba(25, 31, 40, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--text-tertiary);
        font-size: 0.76rem;
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text-primary);
        font-size: 1.55rem;
        font-weight: 850;
        letter-spacing: -0.04em;
    }

    /* Results */

    .risk-banner {
        padding: 1.3rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border);
        border-radius: 22px;
        background: var(--surface);
        box-shadow: 0 8px 28px rgba(25, 31, 40, 0.045);
    }

    .risk-banner-high {
        border-color: #ffd0d2;
        background: var(--red-soft);
    }

    .risk-banner-medium {
        border-color: #f9ddb0;
        background: var(--orange-soft);
    }

    .risk-banner-low {
        border-color: #b7e4d1;
        background: var(--green-soft);
    }

    .risk-eyebrow {
        color: var(--text-secondary);
        font-size: 0.74rem;
        font-weight: 800;
    }

    .risk-title {
        margin-top: 0.35rem;
        color: var(--text-primary);
        font-size: 1.4rem;
        font-weight: 850;
    }

    .risk-copy {
        margin-top: 0.4rem;
        color: var(--text-secondary);
        font-size: 0.86rem;
        line-height: 1.55;
    }

    .finding-card {
        padding: 1.2rem;
        margin-bottom: 0.85rem;
    }

    .finding-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
    }

    .finding-name {
        color: var(--text-primary);
        font-size: 1.05rem;
        font-weight: 850;
    }

    .finding-rule {
        margin-top: 0.2rem;
        color: var(--text-tertiary);
        font-size: 0.72rem;
        font-weight: 650;
    }

    .severity-badge {
        padding: 0.35rem 0.58rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 850;
        white-space: nowrap;
    }

    .severity-high {
        background: var(--red-soft);
        color: var(--red);
    }

    .severity-medium {
        background: var(--orange-soft);
        color: #d97706;
    }

    .severity-low {
        background: var(--green-soft);
        color: var(--green);
    }

    .finding-section {
        margin-top: 1rem;
    }

    .finding-section-label {
        color: var(--text-tertiary);
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .finding-section-copy {
        margin-top: 0.25rem;
        color: var(--text-secondary);
        font-size: 0.86rem;
        line-height: 1.6;
    }

    .validation-pass {
        padding: 1.15rem;
        border: 1px solid #b7e4d1;
        border-radius: 18px;
        background: var(--green-soft);
    }

    .validation-fail {
        padding: 1.15rem;
        border: 1px solid #ffd0d2;
        border-radius: 18px;
        background: var(--red-soft);
    }

    .validation-title {
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 850;
    }

    .validation-copy {
        margin-top: 0.35rem;
        color: var(--text-secondary);
        font-size: 0.82rem;
        line-height: 1.55;
    }

    /* Tabs */

    button[data-baseweb="tab"] {
        padding: 0.75rem 0.7rem;
        color: var(--text-tertiary);
        font-size: 0.82rem;
        font-weight: 750;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--text-primary);
    }

    /* Mobile */

    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero {
            padding: 1.8rem 1.3rem;
            border-radius: 23px;
        }

        .hero-title {
            font-size: 2.15rem;
        }
    }
    </style>
    """
)


# =========================================================
# Session state
# =========================================================

DEFAULT_STATE = {
    "step": STEP_HOME,
    "age": 78,
    "sex": "female",
    "weight_kg": 52.0,
    "serum_creatinine": 1.2,
    "potassium": 4.5,
    "sodium": 138.0,
    "conditions": "hypertension, insomnia",
    "medication_count": 2,
    "medications": [
        {
            "name": "Diazepam",
            "dose": "5 mg",
            "frequency": "once daily",
        },
        {
            "name": "Lisinopril",
            "dose": "10 mg",
            "frequency": "once daily",
        },
    ],
    "review": None,
    "validation_errors": [],
    "submitted_patient": None,
    "error_message": None,
}


for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# Utility functions
# =========================================================

def escape(value: Any) -> str:
    return html.escape(str(value))


def go_to_step(step: int) -> None:
    st.session_state.step = step
    st.rerun()


def reset_app() -> None:
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value

    st.rerun()


def load_example_case(case_key: str) -> None:
    case = EXAMPLE_CASES[case_key]

    st.session_state.age = case["age"]
    st.session_state.sex = case["sex"]
    st.session_state.weight_kg = case["weight_kg"]
    st.session_state.serum_creatinine = case["serum_creatinine"]
    st.session_state.potassium = case["potassium"]
    st.session_state.sodium = case["sodium"]
    st.session_state.conditions = case["conditions"]
    st.session_state.medications = case["medications"]
    st.session_state.medication_count = len(case["medications"])
    st.session_state.review = None
    st.session_state.validation_errors = []
    st.session_state.error_message = None
    st.session_state.step = STEP_PATIENT

    st.rerun()


def build_medications() -> list[Medication]:
    medications: list[Medication] = []

    for medication in st.session_state.medications:
        name = medication.get("name", "").strip()

        if not name:
            continue

        medications.append(
            Medication(
                name=name,
                dose=medication.get("dose", "").strip(),
                frequency=medication.get("frequency", "").strip(),
            )
        )

    return medications


def build_patient_case() -> PatientCase:
    conditions = [
        item.strip()
        for item in st.session_state.conditions.split(",")
        if item.strip()
    ]

    medications = build_medications()

    if not medications:
        raise ValueError("At least one medication is required.")

    return PatientCase(
        age=int(st.session_state.age),
        sex=st.session_state.sex,
        weight_kg=float(st.session_state.weight_kg),
        serum_creatinine=float(
            st.session_state.serum_creatinine
        ),
        conditions=conditions,
        medications=medications,
        labs=Labs(
            potassium=float(st.session_state.potassium),
            sodium=float(st.session_state.sodium),
        ),
    )


def run_review() -> None:
    try:
        patient = build_patient_case()

        review = run_medication_review(patient)

        validation_errors = validate_review(
            patient=patient,
            review=review,
        )

        st.session_state.review = review
        st.session_state.validation_errors = validation_errors
        st.session_state.submitted_patient = patient
        st.session_state.error_message = None
        st.session_state.step = STEP_RESULTS

    except ValidationError as exc:
        st.session_state.error_message = (
            "입력값을 확인해주세요.\n\n"
            f"{exc}"
        )
        st.session_state.step = STEP_MEDICATIONS

    except Exception as exc:
        st.session_state.error_message = str(exc)
        st.session_state.step = STEP_MEDICATIONS


def get_progress() -> tuple[str, int]:
    step = st.session_state.step

    labels = {
        STEP_PATIENT: "환자 정보",
        STEP_CLINICAL: "건강 정보",
        STEP_MEDICATIONS: "복용 약물",
        STEP_ANALYSIS: "안전 검토",
        STEP_RESULTS: "검토 결과",
    }

    percentages = {
        STEP_PATIENT: 20,
        STEP_CLINICAL: 45,
        STEP_MEDICATIONS: 70,
        STEP_ANALYSIS: 88,
        STEP_RESULTS: 100,
    }

    return (
        labels.get(step, ""),
        percentages.get(step, 0),
    )


def severity_class(severity: str) -> str:
    normalized = severity.strip().lower()

    if normalized == "high":
        return "severity-high"

    if normalized == "medium":
        return "severity-medium"

    return "severity-low"


def get_risk_summary(review: Any) -> tuple[str, str, str]:
    severities = {
        finding.severity.strip().lower()
        for finding in review.medication_findings
    }

    if "high" in severities:
        return (
            "높은 우선순위 검토가 필요해요",
            "고위험 약물 안전 항목이 확인되었습니다.",
            "risk-banner-high",
        )

    if "medium" in severities:
        return (
            "추가 검토가 권장돼요",
            "중간 수준의 약물 안전 항목이 확인되었습니다.",
            "risk-banner-medium",
        )

    if review.medication_findings:
        return (
            "확인할 항목이 있어요",
            "현재 규칙 엔진에서 약물 안전 항목을 확인했습니다.",
            "risk-banner-medium",
        )

    return (
        "현재 규칙에서는 위험 항목이 없어요",
        (
            "현재 적용된 제한적인 규칙 범위에서 "
            "일치하는 항목이 없었습니다."
        ),
        "risk-banner-low",
    )


def render_header() -> None:
    st.html(
        """
        <div class="app-header">
            <div class="brand">
                <div class="brand-icon">+</div>
                <div class="brand-name">GeriSafe</div>
            </div>
            <div class="prototype-badge">
                Clinical AI prototype
            </div>
        </div>
        """
    )


def render_progress() -> None:
    if st.session_state.step in {STEP_HOME, STEP_ANALYSIS}:
        return

    label, percentage = get_progress()

    st.html(
        f"""
        <div class="progress-wrap">
            <div class="progress-label-row">
                <div class="progress-label">{escape(label)}</div>
                <div class="progress-step">{percentage}%</div>
            </div>
            <div class="progress-track">
                <div
                    class="progress-fill"
                    style="width: {percentage}%"
                ></div>
            </div>
        </div>
        """
    )


def render_page_heading(
    title: str,
    description: str,
) -> None:
    st.html(
        f"""
        <div class="page-title">{escape(title)}</div>
        <div class="page-description">
            {escape(description)}
        </div>
        """
    )


def render_finding(finding: Any) -> None:
    badge_class = severity_class(finding.severity)

    st.html(
        f"""
        <div class="finding-card">
            <div class="finding-top">
                <div>
                    <div class="finding-name">
                        {escape(finding.medication_name)}
                    </div>
                    <div class="finding-rule">
                        Rule {escape(finding.rule_id)}
                        · {escape(finding.category)}
                    </div>
                </div>

                <div class="severity-badge {badge_class}">
                    {escape(finding.severity)}
                </div>
            </div>

            <div class="finding-section">
                <div class="finding-section-label">
                    검토 근거
                </div>
                <div class="finding-section-copy">
                    {escape(finding.rationale)}
                </div>
            </div>

            <div class="finding-section">
                <div class="finding-section-label">
                    권장 검토 사항
                </div>
                <div class="finding-section-copy">
                    {escape(finding.recommended_action)}
                </div>
            </div>

            <div class="finding-section">
                <div class="finding-section-label">
                    근거 출처
                </div>
                <div class="finding-section-copy">
                    {escape(finding.source_name)}
                    ({escape(finding.source_year)})
                </div>
            </div>
        </div>
        """
    )


# =========================================================
# Common header
# =========================================================

render_header()
render_progress()


# =========================================================
# Home screen
# =========================================================

if st.session_state.step == STEP_HOME:
    st.html(
        """
        <section class="hero">
            <div class="hero-eyebrow">
                고령 환자 약물 안전 검토
            </div>

            <h1 class="hero-title">
                복잡한 처방에서<br>
                먼저 확인할 위험을 찾습니다.
            </h1>

            <p class="hero-description">
                신장 기능 계산, 고령자 약물 규칙,
                구조화된 AI 요약과 결과 검증을 결합한
                약사 검토 지원 프로토타입입니다.
            </p>

            <div class="trust-row">
                <span class="trust-chip">
                    deterministic tools
                </span>
                <span class="trust-chip">
                    structured output
                </span>
                <span class="trust-chip">
                    human review required
                </span>
            </div>
        </section>
        """
    )

    feature_col1, feature_col2, feature_col3 = st.columns(3)

    with feature_col1:
        st.html(
            """
            <div class="feature-card">
                <div class="feature-icon">🧪</div>
                <div class="feature-title">
                    신장 기능 평가
                </div>
                <div class="feature-copy">
                    Cockcroft–Gault 기반
                    creatinine clearance를 계산합니다.
                </div>
            </div>
            """
        )

    with feature_col2:
        st.html(
            """
            <div class="feature-card">
                <div class="feature-icon">💊</div>
                <div class="feature-title">
                    약물 규칙 검토
                </div>
                <div class="feature-copy">
                    현재 등록된 고령자 약물 위험 규칙과
                    처방을 대조합니다.
                </div>
            </div>
            """
        )

    with feature_col3:
        st.html(
            """
            <div class="feature-card">
                <div class="feature-icon">✓</div>
                <div class="feature-title">
                    결과 검증
                </div>
                <div class="feature-copy">
                    AI 출력이 deterministic tool 결과와
                    일치하는지 확인합니다.
                </div>
            </div>
            """
        )

    st.write("")

    if st.button(
        "새 환자 검토 시작하기",
        type="primary",
        use_container_width=True,
    ):
        go_to_step(STEP_PATIENT)

    st.write("")

    with st.expander(
        "예시 환자로 바로 체험하기",
        expanded=False,
    ):
        for case_key, case in EXAMPLE_CASES.items():
            with st.container(border=True):
                st.html(
                    f"""
                    <div class="example-case">
                        <div class="example-label">
                            {escape(case["label"])}
                        </div>
                        <div class="example-description">
                            {escape(case["description"])}
                        </div>
                    </div>
                    """
                )

                if st.button(
                    "이 사례 사용하기",
                    key=f"example_{case_key}",
                    use_container_width=True,
                ):
                    load_example_case(case_key)


# =========================================================
# Patient information
# =========================================================

elif st.session_state.step == STEP_PATIENT:
    render_page_heading(
        "환자 기본 정보를 입력해주세요",
        (
            "신장 기능 추정과 고령자 약물 검토에 "
            "필요한 최소 정보를 받습니다."
        ),
    )

    with st.form("patient_form"):
        with st.container(border=True):
            col1, col2 = st.columns(2)

            with col1:
                age = st.number_input(
                    "나이",
                    min_value=18,
                    max_value=120,
                    value=int(st.session_state.age),
                    step=1,
                )

                sex = st.selectbox(
                    "성별",
                    options=["female", "male"],
                    index=(
                        0
                        if st.session_state.sex == "female"
                        else 1
                    ),
                    format_func=lambda value: (
                        "여성"
                        if value == "female"
                        else "남성"
                    ),
                )

            with col2:
                weight_kg = st.number_input(
                    "체중 (kg)",
                    min_value=20.0,
                    max_value=300.0,
                    value=float(st.session_state.weight_kg),
                    step=0.5,
                    format="%.1f",
                )

        st.write("")

        back_col, next_col = st.columns([1, 2])

        with back_col:
            back = st.form_submit_button(
                "이전",
                use_container_width=True,
            )

        with next_col:
            next_step = st.form_submit_button(
                "다음",
                type="primary",
                use_container_width=True,
            )

    if back:
        go_to_step(STEP_HOME)

    if next_step:
        st.session_state.age = age
        st.session_state.sex = sex
        st.session_state.weight_kg = weight_kg
        go_to_step(STEP_CLINICAL)


# =========================================================
# Clinical information
# =========================================================

elif st.session_state.step == STEP_CLINICAL:
    render_page_heading(
        "검사값과 건강 상태를 알려주세요",
        (
            "현재 prototype은 serum creatinine과 "
            "기본 전해질 정보를 입력받습니다."
        ),
    )

    with st.form("clinical_form"):
        with st.container(border=True):
            st.markdown("#### 신장 및 검사 정보")

            col1, col2, col3 = st.columns(3)

            with col1:
                serum_creatinine = st.number_input(
                    "Serum creatinine",
                    min_value=0.1,
                    max_value=20.0,
                    value=float(
                        st.session_state.serum_creatinine
                    ),
                    step=0.1,
                    format="%.1f",
                    help="단위: mg/dL",
                )

            with col2:
                potassium = st.number_input(
                    "Potassium",
                    min_value=1.0,
                    max_value=10.0,
                    value=float(st.session_state.potassium),
                    step=0.1,
                    format="%.1f",
                    help="단위: mmol/L",
                )

            with col3:
                sodium = st.number_input(
                    "Sodium",
                    min_value=100.0,
                    max_value=180.0,
                    value=float(st.session_state.sodium),
                    step=1.0,
                    format="%.0f",
                    help="단위: mmol/L",
                )

            st.write("")

            conditions = st.text_area(
                "주요 질환",
                value=st.session_state.conditions,
                placeholder=(
                    "예: hypertension, insomnia"
                ),
                help="여러 질환은 쉼표로 구분해주세요.",
                height=110,
            )

        st.write("")

        back_col, next_col = st.columns([1, 2])

        with back_col:
            back = st.form_submit_button(
                "이전",
                use_container_width=True,
            )

        with next_col:
            next_step = st.form_submit_button(
                "다음",
                type="primary",
                use_container_width=True,
            )

    if back:
        go_to_step(STEP_PATIENT)

    if next_step:
        st.session_state.serum_creatinine = serum_creatinine
        st.session_state.potassium = potassium
        st.session_state.sodium = sodium
        st.session_state.conditions = conditions
        go_to_step(STEP_MEDICATIONS)


# =========================================================
# Medication information
# =========================================================

elif st.session_state.step == STEP_MEDICATIONS:
    render_page_heading(
        "복용 중인 약물을 입력해주세요",
        (
            "현재 rule engine은 Diazepam, Zolpidem, "
            "Glyburide 규칙을 우선 지원합니다."
        ),
    )

    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    medication_count = st.number_input(
        "약물 개수",
        min_value=1,
        max_value=8,
        value=int(st.session_state.medication_count),
        step=1,
    )

    medication_count = int(medication_count)

    while len(st.session_state.medications) < medication_count:
        st.session_state.medications.append(
            {
                "name": "",
                "dose": "",
                "frequency": "",
            }
        )

    if len(st.session_state.medications) > medication_count:
        st.session_state.medications = (
            st.session_state.medications[:medication_count]
        )

    with st.form("medication_form"):
        medication_rows: list[dict[str, str]] = []

        for index in range(medication_count):
            with st.container(border=True):
                st.markdown(f"#### 약물 {index + 1}")

                col1, col2 = st.columns([1.35, 1])

                with col1:
                    name = st.text_input(
                        "약물명",
                        value=st.session_state.medications[
                            index
                        ].get("name", ""),
                        key=f"med_name_{index}",
                        placeholder="예: Diazepam",
                    )

                with col2:
                    dose = st.text_input(
                        "용량",
                        value=st.session_state.medications[
                            index
                        ].get("dose", ""),
                        key=f"med_dose_{index}",
                        placeholder="예: 5 mg",
                    )

                frequency = st.text_input(
                    "복용 빈도",
                    value=st.session_state.medications[
                        index
                    ].get("frequency", ""),
                    key=f"med_frequency_{index}",
                    placeholder="예: once daily",
                )

                medication_rows.append(
                    {
                        "name": name,
                        "dose": dose,
                        "frequency": frequency,
                    }
                )

            st.write("")

        back_col, review_col = st.columns([1, 2])

        with back_col:
            back = st.form_submit_button(
                "이전",
                use_container_width=True,
            )

        with review_col:
            analyze = st.form_submit_button(
                "약물 안전 검토 시작",
                type="primary",
                use_container_width=True,
            )

    if back:
        go_to_step(STEP_CLINICAL)

    if analyze:
        valid_medications = [
            medication
            for medication in medication_rows
            if medication["name"].strip()
        ]

        if not valid_medications:
            st.error("약물을 한 개 이상 입력해주세요.")
        else:
            st.session_state.medication_count = len(
                valid_medications
            )
            st.session_state.medications = valid_medications
            st.session_state.error_message = None
            st.session_state.step = STEP_ANALYSIS
            st.rerun()


# =========================================================
# Analysis
# =========================================================

elif st.session_state.step == STEP_ANALYSIS:
    st.html(
        """
        <div class="loading-card analysis-hero">
            <div class="analysis-icon">⚕</div>
            <div class="analysis-title">
                처방 안전성을 검토하고 있어요
            </div>
            <div class="analysis-copy">
                계산 결과와 약물 규칙을 확인하고
                구조화된 임상 검토 결과를 생성합니다.
            </div>
        </div>
        """
    )

    st.write("")

    progress = st.progress(0)

    analysis_steps = [
        (
            20,
            "환자 정보를 구조화하고 있어요",
            "입력된 임상 정보를 PatientCase로 변환합니다.",
        ),
        (
            45,
            "신장 기능을 계산하고 있어요",
            "Cockcroft–Gault 기반 CrCl을 계산합니다.",
        ),
        (
            70,
            "고령자 약물 규칙을 확인하고 있어요",
            "현재 CSV rule engine과 처방을 대조합니다.",
        ),
        (
            88,
            "구조화된 검토 결과를 생성하고 있어요",
            "도구 결과를 기반으로 AI가 내용을 정리합니다.",
        ),
    ]

    step_container = st.container(border=True)

    for percentage, title, description in analysis_steps:
        progress.progress(percentage)

        with step_container:
            st.html(
                f"""
                <div class="analysis-item">
                    <div class="analysis-check">✓</div>
                    <div>
                        <div class="analysis-item-title">
                            {escape(title)}
                        </div>
                        <div class="analysis-item-copy">
                            {escape(description)}
                        </div>
                    </div>
                </div>
                """
            )

        time.sleep(0.25)

    with st.spinner("결과를 검증하고 있습니다..."):
        run_review()

    progress.progress(100)
    time.sleep(0.15)
    st.rerun()


# =========================================================
# Results
# =========================================================

elif st.session_state.step == STEP_RESULTS:
    review = st.session_state.review
    validation_errors = st.session_state.validation_errors

    if review is None:
        st.error("검토 결과를 불러올 수 없습니다.")

        if st.button(
            "처음으로 돌아가기",
            use_container_width=True,
        ):
            reset_app()

        st.stop()

    risk_title, risk_copy, risk_class = get_risk_summary(
        review
    )

    st.html(
        f"""
        <div class="risk-banner {risk_class}">
            <div class="risk-eyebrow">
                검토 결과
            </div>
            <div class="risk-title">
                {escape(risk_title)}
            </div>
            <div class="risk-copy">
                {escape(risk_copy)}
            </div>
        </div>
        """
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric(
            "Creatinine clearance",
            f"{review.renal_assessment.creatinine_clearance_ml_min:.1f}",
            "mL/min",
            delta_color="off",
        )

    with metric_col2:
        st.metric(
            "Medication findings",
            len(review.medication_findings),
            "현재 rule set",
            delta_color="off",
        )

    with metric_col3:
        st.metric(
            "Grounding validation",
            (
                "PASS"
                if not validation_errors
                else "REVIEW"
            ),
            (
                "도구 결과 일치"
                if not validation_errors
                else f"{len(validation_errors)} issue"
            ),
            delta_color="off",
        )

    st.write("")

    summary_tab, medication_tab, renal_tab, validation_tab = (
        st.tabs(
            [
                "상태 요약",
                "약물 안전 검토",
                "신장 기능",
                "검증 결과",
            ]
        )
    )

    with summary_tab:
        with st.container(border=True):
            st.markdown("#### 환자 상태 요약")
            st.write(review.patient_overview)

        st.write("")

        with st.container(border=True):
            st.markdown("#### 약사 검토 포인트")

            if review.pharmacist_review_points:
                for index, point in enumerate(
                    review.pharmacist_review_points,
                    start=1,
                ):
                    st.markdown(
                        f"**{index}.** {point}"
                    )
            else:
                st.caption(
                    "생성된 약사 검토 포인트가 없습니다."
                )

        if review.unsupported_assumptions:
            st.write("")

            with st.expander(
                "현재 도구 범위 밖의 확인 사항"
            ):
                for assumption in (
                    review.unsupported_assumptions
                ):
                    st.write(f"- {assumption}")

    with medication_tab:
        if review.medication_findings:
            for finding in review.medication_findings:
                render_finding(finding)
        else:
            st.success(
                "현재 적용된 약물 규칙에서는 "
                "일치하는 위험 항목이 없습니다."
            )

            st.caption(
                "이는 처방 전체의 임상적 안전성을 "
                "보장한다는 의미가 아닙니다."
            )

    with renal_tab:
        renal = review.renal_assessment

        with st.container(border=True):
            st.markdown("#### 신장 기능 평가")

            st.metric(
                "Estimated creatinine clearance",
                (
                    f"{renal.creatinine_clearance_ml_min:.1f} "
                    "mL/min"
                ),
            )

            st.write(f"**계산 방법:** {renal.method}")
            st.write(
                f"**분류:** {renal.category.title()}"
            )

        st.write("")

        with st.expander(
            "계산 가정과 제한사항",
            expanded=True,
        ):
            if getattr(renal, "assumptions", None):
                st.markdown("**가정**")

                for assumption in renal.assumptions:
                    st.write(f"- {assumption}")

            if renal.limitations:
                st.markdown("**제한사항**")

                for limitation in renal.limitations:
                    st.write(f"- {limitation}")

    with validation_tab:
        if validation_errors:
            error_html = "".join(
                f"<li>{escape(error)}</li>"
                for error in validation_errors
            )

            st.html(
                f"""
                <div class="validation-fail">
                    <div class="validation-title">
                        검증 과정에서 차이가 확인됐어요
                    </div>
                    <div class="validation-copy">
                        AI 구조화 결과와 deterministic tool
                        출력 중 일부가 일치하지 않습니다.
                        <ul>{error_html}</ul>
                    </div>
                </div>
                """
            )

        else:
            st.html(
                """
                <div class="validation-pass">
                    <div class="validation-title">
                        Grounding validation passed
                    </div>
                    <div class="validation-copy">
                        신장 기능 수치와 medication rule ID가
                        deterministic tool 결과와 일치합니다.
                    </div>
                </div>
                """
            )

        st.write("")

        with st.expander(
            "구조화된 원본 결과 보기"
        ):
            st.json(review.model_dump())

    st.write("")

    st.warning(
        review.disclaimer
        + " 이 결과는 진단이나 처방 결정을 대체하지 않으며, "
        + "약사 또는 의료전문가의 검토가 필요합니다."
    )

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button(
            "입력 내용 수정",
            use_container_width=True,
        ):
            go_to_step(STEP_PATIENT)

    with action_col2:
        if st.button(
            "새 환자 검토",
            type="primary",
            use_container_width=True,
        ):
            reset_app()