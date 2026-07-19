from csv import DictReader
from pathlib import Path

from renal_tools import calculate_patient_creatinine_clearance
from schemas import PatientCase, RuleMatch


DEFAULT_RULES_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "medication_rules.csv"
)


def load_medication_rules(
    rules_path: Path = DEFAULT_RULES_PATH,
) -> list[dict[str, str]]:
    """
    Load medication safety rules from a CSV file.
    """
    if not rules_path.exists():
        raise FileNotFoundError(
            f"Medication rules file not found: {rules_path}"
        )

    with rules_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        return list(DictReader(csv_file))


def _matches_age_rule(
    patient: PatientCase,
    rule: dict[str, str],
) -> tuple[bool, list[str]]:
    """
    Evaluate a drug-age rule.
    """
    minimum_age_text = rule.get("min_age", "").strip()

    if not minimum_age_text:
        return False, []

    minimum_age = int(minimum_age_text)
    matched = patient.age >= minimum_age

    return matched, [f"age >= {minimum_age}"]


def _matches_renal_rule(
    patient: PatientCase,
    rule: dict[str, str],
) -> tuple[bool, list[str]]:
    """
    Evaluate a drug-renal rule using Cockcroft-Gault CrCl.
    """
    maximum_crcl_text = rule.get("max_crcl", "").strip()

    if not maximum_crcl_text:
        return False, []

    maximum_crcl = float(maximum_crcl_text)

    renal_assessment = calculate_patient_creatinine_clearance(
        patient
    )
    patient_crcl = renal_assessment[
        "creatinine_clearance_ml_min"
    ]

    matched = patient_crcl < maximum_crcl

    return matched, [
        f"creatinine clearance < {maximum_crcl:g} mL/min",
        f"calculated creatinine clearance = {patient_crcl:g} mL/min",
    ]


def _evaluate_rule(
    patient: PatientCase,
    rule: dict[str, str],
) -> tuple[bool, list[str]]:
    """
    Dispatch a rule to the appropriate deterministic evaluator.
    """
    rule_type = rule["rule_type"].strip().lower()

    if rule_type == "drug_age":
        return _matches_age_rule(patient, rule)

    if rule_type == "drug_renal":
        return _matches_renal_rule(patient, rule)

    raise ValueError(
        f"Unsupported rule type: {rule_type}"
    )


def check_geriatric_medication_risk(
    patient: PatientCase,
    rules_path: Path = DEFAULT_RULES_PATH,
) -> list[RuleMatch]:
    """
    Match patient medications against deterministic
    medication safety rules.

    Returns validated RuleMatch objects.
    """
    rules = load_medication_rules(rules_path)
    findings: list[RuleMatch] = []

    for medication in patient.medications:
        normalized_name = medication.name.strip().lower()

        for rule in rules:
            rule_drug_name = rule["drug_name"].strip().lower()

            if normalized_name != rule_drug_name:
                continue

            matched, matched_conditions = _evaluate_rule(
                patient,
                rule,
            )

            if not matched:
                continue

            findings.append(
                RuleMatch(
                    rule_id=rule["rule_id"],
                    rule_type=rule["rule_type"]
                    .strip()
                    .lower(),
                    severity=rule["severity"]
                    .strip()
                    .lower(),
                    medication_names=[medication.name],
                    matched_conditions=[
                        (
                            "medication name matches "
                            f"{rule['drug_name']}"
                        ),
                        *matched_conditions,
                    ],
                    category=rule["category"],
                    rationale=rule["rationale"],
                    recommended_action=rule["action"],
                    source_name=rule["source_name"],
                    source_year=int(rule["source_year"]),
                    human_review_required=True,
                )
            )

    return findings