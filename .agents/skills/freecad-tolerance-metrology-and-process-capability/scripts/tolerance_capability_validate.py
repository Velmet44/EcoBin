#!/usr/bin/env python3
"""Fail-closed validator for the tolerance capability contract."""

import json
import math
import re
import sys
from datetime import date
from pathlib import Path

MATURITIES = {"concept", "prototype", "verification", "production_candidate", "released"}
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}
SENTINEL = re.compile(
    r"(?:^|[\s<\[({:/_-])(?:tbd|todo|unknown|unassigned|placeholder|"
    r"replace[\s_-]?me|to[\s_-]?be[\s_-]?determined|not[\s_-]?set|"
    r"n/?a|none|null|yyyy[\s_-]?mm[\s_-]?dd|xxx|\?+)"
    r"(?:$|[\s>\])}:/_-])",
    re.IGNORECASE,
)


def present(value):
    if value is None or value == [] or value == {}:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and not SENTINEL.search(value.strip())
    return True


def finite_number(value, *, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if not math.isfinite(value):
        return False
    if positive and value <= 0:
        return False
    if nonnegative and value < 0:
        return False
    return True


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["contract must be a JSON object"], "warnings": []}
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    record_state = data.get("record_state")
    if record_state not in RECORD_STATES:
        errors.append(f"record_state must be one of {sorted(RECORD_STATES)}")

    product = data.get("product", {})
    for field in ("part_number", "revision", "configuration", "maturity", "units", "gps_system", "acceptance_authority_role"):
        if not present(product.get(field)):
            errors.append(f"product.{field} is required")
    maturity = product.get("maturity")
    if maturity not in MATURITIES:
        errors.append(f"product.maturity must be one of {sorted(MATURITIES)}")

    scope = data.get("process_scope", {})
    for field in ("supplier", "site", "machine_id", "process", "material", "setup_or_parameter_revision",
                  "orientation_or_workholding", "valid_feature_range", "evidence_expiry_or_change_trigger"):
        if not present(scope.get(field)):
            errors.append(f"process_scope.{field} is required")

    studies = data.get("capability_studies", [])
    measurements = data.get("measurement_systems", [])
    study_ids = {x.get("id") for x in studies if isinstance(x, dict) and present(x.get("id"))}
    measurement_ids = {x.get("id") for x in measurements if isinstance(x, dict) and present(x.get("id"))}
    if len(study_ids) != len(studies):
        errors.append("capability study IDs must be present and unique")
    if len(measurement_ids) != len(measurements):
        errors.append("measurement system IDs must be present and unique")

    for index, study in enumerate(studies):
        if not isinstance(study, dict):
            errors.append(f"capability_studies[{index}] must be an object")
            continue
        for field in (
            "basis",
            "sample_size",
            "representative_scope",
            "method",
            "raw_data_artifact",
            "approved_by",
            "minimum_sample_size",
            "sample_size_justification",
            "subgroup_policy",
            "distribution_assessment",
            "confidence_method",
            "minimum_cpk",
            "minimum_ppk",
        ):
            if not present(study.get(field)):
                errors.append(f"capability_studies[{index}].{field} is required")
        basis = study.get("basis")
        n = study.get("sample_size")
        if basis == "production_study":
            minimum_n = study.get("minimum_sample_size")
            if (
                isinstance(n, bool)
                or not isinstance(n, int)
                or isinstance(minimum_n, bool)
                or not isinstance(minimum_n, int)
                or minimum_n <= 0
                or n < minimum_n
            ):
                errors.append(
                    f"capability_studies[{index}] sample_size must satisfy the "
                    "approved minimum_sample_size"
                )
            if not present(study.get("stability_evidence")):
                errors.append(f"capability_studies[{index}].stability_evidence is required")
            for field in ("mean", "cp", "cpk", "pp", "ppk"):
                if not finite_number(study.get(field)):
                    errors.append(
                        f"capability_studies[{index}].{field} must be finite numeric"
                    )
            for field in ("sigma_within", "sigma_overall"):
                if not finite_number(study.get(field), positive=True):
                    errors.append(
                        f"capability_studies[{index}].{field} must be positive finite numeric"
                    )
            for field in ("minimum_cpk", "minimum_ppk"):
                if not finite_number(study.get(field), positive=True):
                    errors.append(
                        f"capability_studies[{index}].{field} must be positive finite numeric"
                    )
        elif basis not in {"fai_100_percent", "qualified_family"}:
            errors.append(f"capability_studies[{index}].basis is invalid")
        if basis != "production_study" and any(present(study.get(x)) for x in ("cpk", "ppk")):
            errors.append(f"capability_studies[{index}] cannot claim Cpk/Ppk for {basis}")

    for index, system in enumerate(measurements):
        if not isinstance(system, dict):
            errors.append(f"measurement_systems[{index}] must be an object")
            continue
        for field in ("method", "instrument_id", "calibration_evidence", "resolution", "expanded_uncertainty",
                      "uncertainty_units", "decision_rule", "guard_band", "environment_and_fixture"):
            if not present(system.get(field)):
                errors.append(f"measurement_systems[{index}].{field} is required")
        for field in ("resolution", "expanded_uncertainty", "guard_band"):
            if not finite_number(system.get(field), nonnegative=True):
                errors.append(f"measurement_systems[{index}].{field} must be non-negative numeric")
        if maturity in {"production_candidate", "released"} and not present(system.get("msa_evidence")):
            errors.append(f"measurement_systems[{index}].msa_evidence is required for production maturity")

    characteristics = data.get("characteristics", [])
    if not characteristics:
        errors.append("characteristics must contain at least one CTQ")
    for index, item in enumerate(characteristics):
        if not isinstance(item, dict):
            errors.append(f"characteristics[{index}] must be an object")
            continue
        for field in ("id", "feature", "nominal", "units", "datum_reference", "process_state",
                      "measurement_id", "capability_id", "fit_or_stack_evidence", "control_plan_evidence"):
            if not present(item.get(field)):
                errors.append(f"characteristics[{index}].{field} is required")
        lsl, usl = item.get("lsl"), item.get("usl")
        if not finite_number(lsl) and not finite_number(usl):
            errors.append(f"characteristics[{index}] requires at least one numeric specification limit")
        if finite_number(lsl) and finite_number(usl) and lsl >= usl:
            errors.append(f"characteristics[{index}] requires lsl < usl")
        if item.get("capability_id") not in study_ids:
            errors.append(f"characteristics[{index}].capability_id does not resolve")
        if item.get("measurement_id") not in measurement_ids:
            errors.append(f"characteristics[{index}].measurement_id does not resolve")
        study = next((x for x in studies if isinstance(x, dict) and x.get("id") == item.get("capability_id")), None)
        if study and study.get("basis") == "production_study":
            mean = study.get("mean")
            sigma_within = study.get("sigma_within")
            sigma_overall = study.get("sigma_overall")
            if all(
                finite_number(value, positive=field.startswith("sigma"))
                for field, value in (
                    ("mean", mean),
                    ("sigma_within", sigma_within),
                    ("sigma_overall", sigma_overall),
                )
            ):
                within_limits = []
                overall_limits = []
                if finite_number(usl):
                    within_limits.append((usl - mean) / (3 * sigma_within))
                    overall_limits.append((usl - mean) / (3 * sigma_overall))
                if finite_number(lsl):
                    within_limits.append((mean - lsl) / (3 * sigma_within))
                    overall_limits.append((mean - lsl) / (3 * sigma_overall))
                calculated_cpk = min(within_limits)
                calculated_ppk = min(overall_limits)
                for field, calculated in (
                    ("cpk", calculated_cpk),
                    ("ppk", calculated_ppk),
                ):
                    declared = study.get(field)
                    if finite_number(declared) and not math.isclose(
                        calculated, declared, rel_tol=0.03, abs_tol=0.03
                    ):
                        errors.append(
                            f"capability study {study.get('id')} {field.upper()} "
                            "does not match declared limits/statistics"
                        )
                if finite_number(lsl) and finite_number(usl):
                    calculated_cp = (usl - lsl) / (6 * sigma_within)
                    calculated_pp = (usl - lsl) / (6 * sigma_overall)
                    for field, calculated in (
                        ("cp", calculated_cp),
                        ("pp", calculated_pp),
                    ):
                        declared = study.get(field)
                        if finite_number(declared) and not math.isclose(
                            calculated, declared, rel_tol=0.03, abs_tol=0.03
                        ):
                            errors.append(
                                f"capability study {study.get('id')} {field.upper()} "
                                "does not match declared limits/statistics"
                            )
                if calculated_cpk < study.get("minimum_cpk", math.inf):
                    errors.append(
                        f"capability study {study.get('id')} Cpk "
                        f"{calculated_cpk:.3g} is below the approved threshold"
                    )
                if calculated_ppk < study.get("minimum_ppk", math.inf):
                    errors.append(
                        f"capability study {study.get('id')} Ppk "
                        f"{calculated_ppk:.3g} is below the approved threshold"
                    )
            system = next((x for x in measurements if isinstance(x, dict) and x.get("id") == item.get("measurement_id")), None)
            if system and isinstance(system.get("guard_band"), (int, float)):
                specification_width = None
                if finite_number(lsl) and finite_number(usl):
                    specification_width = usl - lsl
                if specification_width is not None and 2 * system["guard_band"] >= specification_width - 1e-12:
                    errors.append(f"measurement system {system.get('id')} guard band consumes the specification zone")

    compensation = data.get("compensation", {})
    if compensation.get("nominal_model_remains_authoritative") is not True:
        errors.append("compensation.nominal_model_remains_authoritative must be true")
    if compensation.get("used"):
        for field in ("controlled_derivative_id", "validity_envelope", "before_after_validation"):
            if not present(compensation.get(field)):
                errors.append(f"compensation.{field} is required when compensation is used")

    release = data.get("release", {})
    if maturity in {"production_candidate", "released"}:
        for field in (
            "first_article_or_control_plan",
            "supplier_approval",
            "change_control",
            "approver",
            "approver_role",
            "approval_date",
        ):
            if not present(release.get(field)):
                errors.append(f"release.{field} is required for production maturity")
        if release.get("approver_role") != product.get("acceptance_authority_role"):
            errors.append(
                "release.approver_role must match product.acceptance_authority_role"
            )
        if present(release.get("approval_date")) and not valid_date(
            release.get("approval_date")
        ):
            errors.append("release.approval_date must be ISO YYYY-MM-DD")
        if record_state != "controlled_evidence":
            warnings.append(
                "template/fixture record cannot receive a production evidence PASS"
            )
    else:
        warnings.append("non-production maturity: release completeness is not enforced")

    if errors:
        verdict = "FAIL"
    elif record_state != "controlled_evidence":
        verdict = "DRAFT"
    elif maturity in {"concept", "prototype"}:
        verdict = "DRAFT"
    elif maturity == "verification":
        verdict = "CONDITIONAL"
    elif maturity == "released":
        for field in ("baseline_id", "effectivity", "release_authority_record"):
            if not present(release.get(field)):
                errors.append(f"release.{field} is required for released maturity")
        verdict = "FAIL" if errors else "RELEASED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "errors": errors, "warnings": warnings}


def main():
    if len(sys.argv) != 2:
        print("usage: tolerance_capability_validate.py CONTRACT.json", file=sys.stderr)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    report = validate(data)
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] in {"PASS", "RELEASED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
