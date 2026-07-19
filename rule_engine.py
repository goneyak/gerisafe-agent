from csv import DictReader
from pathlib import Path

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


def check_geriatric_medication_risk(
    patient: PatientCase,
    rules_path: Path = DEFAULT_RULES_PATH,
) -> list[RuleMatch]:
    """
    Match a patient's medications against deterministic
    age-based geriatric medication safety rules.

    Returns validated RuleMatch objects.
    """
    rules = load_medication_rules(rules_path)
    findings: list[RuleMatch] = []

    for medication in patient.medications:
        normalized_name = medication.name.strip().lower()

        for rule in rules:
            rule_drug_name = rule["drug_name"].strip().lower()
            minimum_age = int(rule["min_age"])

            if (
                normalized_name == rule_drug_name
                and patient.age >= minimum_age
            ):
                findings.append(
                    RuleMatch(
                        rule_id=rule["rule_id"],
                        rule_type="drug_age",
                        severity=rule["severity"].strip().lower(),
                        medication_names=[medication.name],
                        matched_conditions=[
                            f"age >= {minimum_age}",
                            (
                                "medication name matches "
                                f"{rule['drug_name']}"
                            ),
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