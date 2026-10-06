#!/usr/bin/env python3
"""Validate multibody/controls dynamics evidence without claiming physical truth."""

import json
import math
import re
import sys
from datetime import date
from pathlib import Path

MATURITIES = {"concept", "prototype", "verification", "production_candidate", "released"}
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}
HASH = re.compile(r"^[0-9a-fA-F]{64}$")
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


def require(obj, fields, prefix, errors):
    for field in fields:
        if not present(obj.get(field)):
            errors.append(f"{prefix}.{field} is required")


def symmetric_eigenvalues_3x3(matrix):
    """Closed-form eigenvalues for a real symmetric 3x3 matrix."""
    a, b, c = matrix[0]
    _, d, e = matrix[1]
    _, _, f = matrix[2]
    p1 = b * b + c * c + e * e
    if p1 == 0:
        return [a, d, f]
    q = (a + d + f) / 3.0
    p2 = (a - q) ** 2 + (d - q) ** 2 + (f - q) ** 2 + 2 * p1
    p = math.sqrt(p2 / 6.0)
    normalized = [[(matrix[i][j] - (q if i == j else 0.0)) / p for j in range(3)] for i in range(3)]
    determinant = (
        normalized[0][0] * (normalized[1][1] * normalized[2][2] - normalized[1][2] * normalized[2][1])
        - normalized[0][1] * (normalized[1][0] * normalized[2][2] - normalized[1][2] * normalized[2][0])
        + normalized[0][2] * (normalized[1][0] * normalized[2][1] - normalized[1][1] * normalized[2][0])
    )
    r = max(-1.0, min(1.0, determinant / 2.0))
    phi = math.acos(r) / 3.0
    eig1 = q + 2 * p * math.cos(phi)
    eig3 = q + 2 * p * math.cos(phi + 2 * math.pi / 3)
    eig2 = 3 * q - eig1 - eig3
    return [eig1, eig2, eig3]


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
    require(product, ("part_number", "revision", "configuration", "maturity", "acceptance_authority_role"), "product", errors)
    maturity = product.get("maturity")
    if maturity not in MATURITIES:
        errors.append(f"product.maturity must be one of {sorted(MATURITIES)}")
    require(data.get("intended_use", {}), ("prediction", "acceptance_limits", "excluded_physics", "consequence"),
            "intended_use", errors)
    links = data.get("links", [])
    if not links:
        errors.append("links must contain at least one moving link")
    ids = set()
    for index, link in enumerate(links):
        if not isinstance(link, dict):
            errors.append(f"links[{index}] must be an object")
            continue
        require(link, ("id", "occurrence_id", "source_hash", "mass_properties_hash", "frame", "mass_kg", "cog_m", "inertia_kg_m2",
                       "uncertainty", "measured_reconciliation"), f"links[{index}]", errors)
        if link.get("id") in ids:
            errors.append(f"duplicate link ID {link.get('id')}")
        ids.add(link.get("id"))
        if present(link.get("source_hash")) and not HASH.fullmatch(str(link["source_hash"])):
            errors.append(f"links[{index}].source_hash must be a 64-character SHA-256")
        if present(link.get("mass_properties_hash")) and not HASH.fullmatch(
            str(link["mass_properties_hash"])
        ):
            errors.append(
                f"links[{index}].mass_properties_hash must be a 64-character SHA-256"
            )
        if not finite_number(link.get("mass_kg"), positive=True):
            errors.append(f"links[{index}].mass_kg must be positive finite numeric")
        cog, inertia = link.get("cog_m"), link.get("inertia_kg_m2")
        if not isinstance(cog, list) or len(cog) != 3 or not all(finite_number(x) for x in cog):
            errors.append(f"links[{index}].cog_m must contain three finite numbers")
        if not (isinstance(inertia, list) and len(inertia) == 3 and all(isinstance(r, list) and len(r) == 3 for r in inertia)):
            errors.append(f"links[{index}].inertia_kg_m2 must be 3x3")
        elif not all(finite_number(x) for row in inertia for x in row):
            errors.append(f"links[{index}].inertia_kg_m2 must be finite numeric")
        else:
            for i in range(3):
                if inertia[i][i] <= 0:
                    errors.append(f"links[{index}] inertia diagonal must be positive")
                for j in range(3):
                    if not math.isclose(inertia[i][j], inertia[j][i], rel_tol=1e-8, abs_tol=1e-12):
                        errors.append(f"links[{index}] inertia tensor must be symmetric")
            principal = symmetric_eigenvalues_3x3(inertia)
            if any(value <= 0 for value in principal):
                errors.append(f"links[{index}] inertia tensor must have positive principal moments")
            if max(principal) > sum(principal) - max(principal) + 1e-10:
                errors.append(f"links[{index}] inertia principal moments violate triangle inequality")
    require(data.get("model", {}), ("joint_and_constraint_evidence", "friction_compliance_backlash_evidence",
            "contact_and_stop_evidence", "actuator_drive_controller_evidence",
            "base_fixture_compliance_evidence", "gravity_and_initial_conditions"), "model", errors)
    co_sim = data.get("model", {}).get("co_simulation", {})
    if not isinstance(co_sim.get("required"), bool):
        errors.append("model.co_simulation.required must be true or false")
    elif co_sim.get("required"):
        require(co_sim, ("interface_contract", "exchange_variables_frames_units", "sample_rates_and_latency",
                "coupling_and_convergence", "initialization_and_failure_handling"), "model.co_simulation", errors)
    trajectory = data.get("trajectory", {})
    require(trajectory, ("artifact", "source_hash", "sample_rate_hz", "duration_s"), "trajectory", errors)
    if present(trajectory.get("source_hash")) and not HASH.fullmatch(str(trajectory["source_hash"])):
        errors.append("trajectory.source_hash must be a 64-character SHA-256")
    for field in ("sample_rate_hz", "duration_s"):
        if not finite_number(trajectory.get(field), positive=True):
            errors.append(f"trajectory.{field} must be positive finite numeric")
    solver = data.get("solver", {})
    require(solver, ("name", "version", "model_input_hash", "integrator", "time_step_s",
            "relative_tolerance", "absolute_tolerance", "contact_formulation", "run_environment"), "solver", errors)
    if present(solver.get("model_input_hash")) and not HASH.fullmatch(str(solver["model_input_hash"])):
        errors.append("solver.model_input_hash must be a 64-character SHA-256")
    for field in ("time_step_s", "relative_tolerance", "absolute_tolerance"):
        if not finite_number(solver.get(field), positive=True):
            errors.append(f"solver.{field} must be positive finite numeric")
    verification = data.get("verification", {})
    require(verification, ("analytical_or_benchmark_evidence", "constraint_residual_limit",
            "constraint_residual_observed", "energy_balance_evidence", "time_step_sensitivity_evidence",
            "parameter_sensitivity_evidence", "deterministic_rerun_evidence"), "verification", errors)
    limit, observed = verification.get("constraint_residual_limit"), verification.get("constraint_residual_observed")
    if not finite_number(limit, nonnegative=True) or not finite_number(
        observed, nonnegative=True
    ):
        errors.append("constraint residual values must be finite non-negative numbers")
    elif observed > limit:
        errors.append("constraint residual exceeds declared limit")
    reconciliation = data.get("load_reconciliation", {})
    require(reconciliation, ("robot_sizing_contract", "fea_load_transfer", "governing_event_table"),
            "load_reconciliation", errors)
    for field in ("robot_sizing_contract", "fea_load_transfer", "governing_event_table"):
        item = reconciliation.get(field)
        if not isinstance(item, dict):
            errors.append(f"load_reconciliation.{field} must be an object")
            continue
        require(
            item,
            ("artifact", "source_hash", "configuration"),
            f"load_reconciliation.{field}",
            errors,
        )
        if present(item.get("source_hash")) and not HASH.fullmatch(
            str(item["source_hash"])
        ):
            errors.append(
                f"load_reconciliation.{field}.source_hash must be a 64-character SHA-256"
            )
        if item.get("configuration") != product.get("configuration"):
            errors.append(
                f"load_reconciliation.{field}.configuration must match product.configuration"
            )
    correlation = data.get("physical_correlation", {})
    require(correlation, ("state", "test_plan", "instrumentation_and_uncertainty"), "physical_correlation", errors)
    if correlation.get("state") not in {"planned", "available", "in_progress", "passed", "failed"}:
        errors.append("physical_correlation.state is invalid")
    if correlation.get("state") == "passed":
        require(correlation, ("independent_validation_data", "correlation_report", "source_hash",
                "configuration", "test_date", "channels", "accepted_by", "accepted_by_role"),
                "physical_correlation", errors)
        if present(correlation.get("source_hash")) and not HASH.fullmatch(
            str(correlation["source_hash"])
        ):
            errors.append(
                "physical_correlation.source_hash must be a 64-character SHA-256"
            )
        if correlation.get("configuration") != product.get("configuration"):
            errors.append(
                "physical_correlation.configuration must match product.configuration"
            )
        if present(correlation.get("test_date")) and not valid_date(
            correlation.get("test_date")
        ):
            errors.append("physical_correlation.test_date must be ISO YYYY-MM-DD")
        if correlation.get("accepted_by_role") != product.get(
            "acceptance_authority_role"
        ):
            errors.append(
                "physical_correlation.accepted_by_role must match "
                "product.acceptance_authority_role"
            )
        channels = correlation.get("channels")
        if not isinstance(channels, list) or not channels:
            errors.append("physical_correlation.channels must be a non-empty list")
        else:
            channel_ids = set()
            for index, channel in enumerate(channels):
                if not isinstance(channel, dict):
                    errors.append(
                        f"physical_correlation.channels[{index}] must be an object"
                    )
                    continue
                require(
                    channel,
                    (
                        "id",
                        "quantity",
                        "unit",
                        "predicted",
                        "measured",
                        "acceptance_tolerance",
                        "expanded_uncertainty",
                        "result",
                    ),
                    f"physical_correlation.channels[{index}]",
                    errors,
                )
                channel_id = channel.get("id")
                if channel_id in channel_ids:
                    errors.append(
                        f"duplicate physical correlation channel ID {channel_id}"
                    )
                channel_ids.add(channel_id)
                numerics = (
                    channel.get("predicted"),
                    channel.get("measured"),
                    channel.get("acceptance_tolerance"),
                    channel.get("expanded_uncertainty"),
                )
                if not all(finite_number(value) for value in numerics):
                    errors.append(
                        f"physical_correlation.channels[{index}] numeric values "
                        "must be finite"
                    )
                else:
                    delta = abs(channel["predicted"] - channel["measured"])
                    allowed = (
                        channel["acceptance_tolerance"]
                        + channel["expanded_uncertainty"]
                    )
                    calculated = delta <= allowed
                    if channel.get("result") != ("pass" if calculated else "fail"):
                        errors.append(
                            f"physical_correlation.channels[{index}].result "
                            "disagrees with the quantitative comparison"
                        )
                    if not calculated:
                        errors.append(
                            f"physical_correlation.channels[{index}] exceeds "
                            "correlation acceptance"
                        )
    if correlation.get("state") == "failed" and maturity in {"production_candidate", "released"}:
        errors.append("failed physical correlation blocks production maturity")
    if maturity in {"production_candidate", "released"} and correlation.get("state") != "passed":
        errors.append("production maturity requires passed physical correlation")
    if maturity in {"production_candidate", "released"}:
        release = data.get("release", {})
        require(release, ("limitations", "approver", "approver_role", "approval_date"), "release", errors)
        if release.get("approver_role") != product.get("acceptance_authority_role"):
            errors.append("release.approver_role must match product.acceptance_authority_role")
        if present(release.get("approval_date")) and not valid_date(
            release.get("approval_date")
        ):
            errors.append("release.approval_date must be ISO YYYY-MM-DD")
        if record_state != "controlled_evidence":
            warnings.append("template/fixture record cannot receive a production PASS")
    else:
        warnings.append("non-production maturity: full release evidence is not enforced")
    if errors:
        verdict = "FAIL"
    elif record_state != "controlled_evidence":
        verdict = "DRAFT"
    elif maturity in {"concept", "prototype"}:
        verdict = "DRAFT"
    elif maturity == "verification":
        verdict = "CONDITIONAL"
    elif maturity == "released":
        release = data.get("release", {})
        for field in ("baseline_id", "effectivity", "release_authority_record"):
            if not present(release.get(field)):
                errors.append(f"release.{field} is required for released maturity")
        verdict = "FAIL" if errors else "RELEASED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "errors": errors, "warnings": warnings}


def main():
    if len(sys.argv) != 2:
        print("usage: motion_dynamics_validate.py CONTRACT.json", file=sys.stderr)
        return 2
    report = validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] in {"PASS", "RELEASED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
