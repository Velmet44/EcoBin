#!/usr/bin/env python3
"""Validate controlled additive-manufacturing process and release evidence."""

import datetime as dt
import json
import math
import re
import sys
from pathlib import Path

MATURITIES = {"concept", "prototype", "verification", "production_candidate", "released"}
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}
PROCESS_CATEGORIES = {
    "material extrusion", "vat photopolymerization", "powder bed fusion",
    "binder jetting", "directed energy deposition", "material jetting",
    "sheet lamination",
}
HASH = re.compile(r"^[0-9a-fA-F]{64}$")
SENTINEL = re.compile(
    r"^(?:tbd|todo|unknown|unassigned|sample|example|placeholder|pending|"
    r"project-recorded|project-pinned|yyyy-mm-dd|n/?a)$", re.I
)


def present(value):
    return value is not None and value != "" and value != [] and value != {}


def controlled(value):
    return present(value) and not (
        isinstance(value, str) and SENTINEL.fullmatch(value.strip())
    )


def finite(value, positive=False):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and (not positive or value > 0)
    )


def iso_date(value):
    try:
        dt.date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def require(obj, fields, prefix, errors, strict=False):
    if not isinstance(obj, dict):
        errors.append(f"{prefix} must be an object")
        return
    predicate = controlled if strict else present
    for field in fields:
        if not predicate(obj.get(field)):
            errors.append(f"{prefix}.{field} is required")


def hash_field(obj, field, prefix, errors):
    if present(obj.get(field)) and not HASH.fullmatch(str(obj[field])):
        errors.append(f"{prefix}.{field} must be a 64-character SHA-256")


def evidence_record(value, prefix, errors):
    require(value, ("id", "revision", "sha256", "status"), prefix, errors, True)
    if isinstance(value, dict):
        hash_field(value, "sha256", prefix, errors)
        if value.get("status") not in {"pass", "accepted", "approved"}:
            errors.append(f"{prefix}.status must be pass, accepted, or approved")


def validate(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["contract must be a JSON object"], "warnings": []}
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    state = data.get("record_state")
    if state not in RECORD_STATES:
        errors.append(f"record_state must be one of {sorted(RECORD_STATES)}")
    strict = state == "controlled_evidence"

    product = data.get("product", {})
    require(
        product,
        ("part_number", "revision", "configuration", "maturity", "acceptance_authority_role"),
        "product", errors, strict,
    )
    maturity = product.get("maturity")
    if maturity not in MATURITIES:
        errors.append(f"product.maturity must be one of {sorted(MATURITIES)}")
    candidate = strict and maturity in {"production_candidate", "released"}

    process = data.get("process_tuple", {})
    require(
        process,
        (
            "supplier", "site", "machine_id", "process_category", "material_and_lot",
            "parameter_set_revision", "build_software_version", "orientation_and_position",
            "support_strategy", "atmosphere_or_conditioning", "requalification_triggers",
        ),
        "process_tuple", errors, strict,
    )
    if strict and process.get("process_category") not in PROCESS_CATEGORIES:
        errors.append(f"process_tuple.process_category must be one of {sorted(PROCESS_CATEGORIES)}")

    states = data.get("state_chain")
    if not isinstance(states, list) or len(states) < 2 or any(not controlled(item) for item in states):
        errors.append("state_chain requires at least two controlled named states")
    elif len(set(states)) != len(states):
        errors.append("state_chain states must be unique")
    elif candidate and not any("inspect" in str(item).lower() for item in states):
        errors.append("production state_chain must include a final inspected state")

    require(
        data.get("design_review", {}),
        (
            "orientation_anisotropy_evidence", "support_and_removal_evidence",
            "warp_and_residual_stress_evidence", "trapped_material_and_cleaning_evidence",
            "machining_stock_and_datums", "holes_threads_and_inserts_strategy",
        ),
        "design_review", errors, strict,
    )
    qualification = data.get("qualification", {})
    require(
        qualification,
        (
            "material_allowables_evidence", "representative_coupon_plan",
            "geometric_artifact_plan", "tolerance_capability_contract", "physical_test_plan",
        ),
        "qualification", errors, strict,
    )
    post = data.get("postprocess_and_inspection", {})
    require(
        post,
        (
            "support_or_powder_removal", "heat_treatment_or_conditioning",
            "machining_and_surface_route", "cleanliness_acceptance",
            "nde_or_internal_inspection", "final_inspection_plan",
        ),
        "postprocess_and_inspection", errors, strict,
    )

    control = data.get("data_control", {})
    require(
        control,
        ("nominal_fcstd_hash", "step_hash", "build_input_hash", "build_record_and_lot_traceability"),
        "data_control", errors, strict,
    )
    for field in ("nominal_fcstd_hash", "step_hash", "build_input_hash"):
        hash_field(control, field, "data_control", errors)
    if present(control.get("compensated_derivative_id")) and not controlled(control.get("compensation_validation")):
        errors.append("data_control.compensation_validation is required for a compensated derivative")

    if candidate:
        feedstock = data.get("feedstock_control", {})
        require(
            feedstock,
            (
                "manufacturer", "material_specification", "lot_id", "certificate_sha256",
                "receipt_date", "storage_condition", "drying_or_conditioning_record",
                "reuse_policy", "reuse_count", "contamination_control",
            ),
            "feedstock_control", errors, True,
        )
        hash_field(feedstock, "certificate_sha256", "feedstock_control", errors)
        if not iso_date(feedstock.get("receipt_date")):
            errors.append("feedstock_control.receipt_date must be an ISO date")
        if not isinstance(feedstock.get("reuse_count"), int) or isinstance(feedstock.get("reuse_count"), bool) or feedstock.get("reuse_count", -1) < 0:
            errors.append("feedstock_control.reuse_count must be a non-negative integer")

        equipment = data.get("equipment_control", {})
        require(
            equipment,
            (
                "qualification_record", "calibration_record", "maintenance_record",
                "last_maintenance_date", "next_due_date", "build_platform_id",
                "environment_monitoring",
            ),
            "equipment_control", errors, True,
        )
        for field in ("qualification_record", "calibration_record", "maintenance_record"):
            evidence_record(equipment.get(field), f"equipment_control.{field}", errors)
        if not iso_date(equipment.get("last_maintenance_date")) or not iso_date(equipment.get("next_due_date")):
            errors.append("equipment control maintenance dates must be ISO dates")

        execution = data.get("build_execution", {})
        require(
            execution,
            (
                "build_id", "operator_id", "parameter_file_sha256", "support_file_sha256",
                "orientation_file_sha256", "machine_log_sha256", "monitoring_disposition",
                "build_start", "build_end", "part_serials",
            ),
            "build_execution", errors, True,
        )
        for field in (
            "parameter_file_sha256", "support_file_sha256", "orientation_file_sha256",
            "machine_log_sha256",
        ):
            hash_field(execution, field, "build_execution", errors)
        if not isinstance(execution.get("part_serials"), list) or not execution.get("part_serials"):
            errors.append("build_execution.part_serials must be a non-empty list")

        coupons = qualification.get("coupon_results")
        if not isinstance(coupons, list) or not coupons:
            errors.append("qualification.coupon_results must contain measured production-build results")
        else:
            for index, coupon in enumerate(coupons):
                require(
                    coupon,
                    ("id", "build_id", "orientation", "test_method", "result", "unit", "lower_limit", "status", "report_sha256"),
                    f"qualification.coupon_results[{index}]", errors, True,
                )
                if isinstance(coupon, dict):
                    for field in ("result", "lower_limit"):
                        if not finite(coupon.get(field)):
                            errors.append(f"qualification.coupon_results[{index}].{field} must be finite numeric")
                    if finite(coupon.get("result")) and finite(coupon.get("lower_limit")) and coupon["result"] < coupon["lower_limit"]:
                        errors.append(f"qualification.coupon_results[{index}] is below its lower limit")
                    if coupon.get("build_id") != execution.get("build_id"):
                        errors.append(f"qualification.coupon_results[{index}] does not belong to production build")
                    if coupon.get("status") != "pass":
                        errors.append(f"qualification.coupon_results[{index}].status must be pass")
                    hash_field(coupon, "report_sha256", f"qualification.coupon_results[{index}]", errors)

        certificates = post.get("certificates")
        if not isinstance(certificates, list) or not certificates:
            errors.append("postprocess_and_inspection.certificates must contain controlled certificates")
        else:
            for index, certificate in enumerate(certificates):
                evidence_record(certificate, f"postprocess_and_inspection.certificates[{index}]", errors)

        personnel = data.get("personnel_and_ehs", {})
        require(
            personnel,
            (
                "operator_qualification", "site_process_qualification",
                "ppe_and_exposure_control", "powder_or_resin_handling",
                "fire_explosion_control", "waste_disposition",
            ),
            "personnel_and_ehs", errors, True,
        )
        evidence_record(personnel.get("operator_qualification"), "personnel_and_ehs.operator_qualification", errors)
        evidence_record(personnel.get("site_process_qualification"), "personnel_and_ehs.site_process_qualification", errors)

        release = data.get("release", {})
        require(release, ("approvals", "approval_date", "configuration"), "release", errors, True)
        if not iso_date(release.get("approval_date")):
            errors.append("release.approval_date must be an ISO date")
        if release.get("configuration") != product.get("configuration"):
            errors.append("release.configuration must match product configuration")
        approvals = release.get("approvals")
        roles = {
            item.get("role") for item in approvals if isinstance(item, dict) and item.get("status") == "approved"
        } if isinstance(approvals, list) else set()
        required_roles = {"supplier quality", "quality authority", product.get("acceptance_authority_role")}
        if not isinstance(approvals, list) or not required_roles.issubset(roles):
            errors.append(f"release.approvals must include approved roles {sorted(str(x) for x in required_roles)}")
    elif maturity in {"production_candidate", "released"}:
        warnings.append("template/fixture record cannot be production evidence")
    else:
        warnings.append("non-production maturity: release approvals are not enforced")

    if errors:
        verdict = "FAIL"
    elif state != "controlled_evidence" or maturity in {"concept", "prototype"}:
        verdict = "DRAFT"
    elif maturity == "verification":
        verdict = "CONDITIONAL"
    elif maturity == "released":
        verdict = "RELEASED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "errors": errors, "warnings": warnings}


def main():
    if len(sys.argv) != 2:
        print("usage: additive_contract_validate.py CONTRACT.json", file=sys.stderr)
        return 2
    report = validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] in {"PASS", "RELEASED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
