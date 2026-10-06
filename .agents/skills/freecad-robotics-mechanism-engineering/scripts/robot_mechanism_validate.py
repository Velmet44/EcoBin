#!/usr/bin/env python3
"""Fail-closed structural and arithmetic checks for a robot mechanism contract."""

import argparse
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path


SENTINELS = {
    "", "tbd", "unknown", "unassigned", "n/a", "na", "none", "null",
    "pending", "xxx", "?", "yyyy-mm-dd",
}
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
MATURITIES = {"concept", "prototype", "verification", "production_candidate", "released"}
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}
REQUIRED_EVIDENCE = {
    "kinematics", "trajectory_loads", "drive_thermal",
    "transmission_bearing_life", "accuracy_calibration",
    "stopping_power_loss", "motion_dynamics_validation",
    "physical_verification_plan",
}


def present(value):
    if value is None:
        return False
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in SENTINELS or "unassigned" in normalized:
            return False
    return True


def positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def get(data, path):
    value = data
    for key in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def validate(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["contract must be a JSON object"], "warnings": []}
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    record_state = data.get("record_state")
    if record_state not in RECORD_STATES:
        errors.append(f"record_state must be one of {sorted(RECORD_STATES)}")

    for path in (
        "schema_version", "product.part_number", "product.revision",
        "product.configuration", "product.maturity", "product.units",
        "product.base_frame", "product.acceptance_authority_role",
        "requirements.duty_cycle_source", "kinematics.model_id",
        "kinematics.workspace_evidence", "kinematics.singularity_metric",
        "kinematics.singularity_evidence", "kinematics.known_pose_test",
        "safety.risk_assessment_id", "safety.applicable_standard_register",
        "safety.residual_risk_approval",
    ):
        if not present(get(data, path)):
            errors.append(f"missing controlled value: {path}")

    maturity = get(data, "product.maturity")
    if maturity not in MATURITIES:
        errors.append(f"product.maturity must be one of {sorted(MATURITIES)}")

    for path in (
        "requirements.payload_mass_kg", "requirements.reach_m",
        "requirements.accuracy_m", "requirements.repeatability_m",
        "requirements.life_cycles", "kinematics.singularity_threshold",
        "performance_budget.predicted_endpoint_error_m",
        "performance_budget.allowable_endpoint_error_m",
    ):
        if not positive(get(data, path)):
            errors.append(f"{path} must be a positive finite number")

    frames = data.get("frames")
    frame_ids = set()
    if not isinstance(frames, list) or not frames:
        errors.append("frames must be a non-empty list")
        frames = []
    for index, frame in enumerate(frames):
        if not isinstance(frame, dict):
            errors.append(f"frames[{index}] must be an object")
            continue
        frame_id = frame.get("id")
        if not present(frame_id):
            errors.append(f"frames[{index}].id is required")
        elif frame_id in frame_ids:
            errors.append(f"duplicate frame id: {frame_id}")
        else:
            frame_ids.add(frame_id)
        if not present(frame.get("kind")) or not present(frame.get("source")):
            errors.append(f"frames[{index}] requires kind and source")
    for index, frame in enumerate(frames):
        if isinstance(frame, dict) and frame.get("parent") is not None and frame.get("parent") not in frame_ids:
            errors.append(f"frames[{index}].parent references unknown frame")
    roots = [f for f in frames if isinstance(f, dict) and f.get("parent") is None]
    if len(roots) != 1:
        errors.append("frames must have exactly one root")
    elif frame_ids:
        root_id = roots[0].get("id")
        parent_by_id = {
            frame.get("id"): frame.get("parent")
            for frame in frames
            if isinstance(frame, dict) and present(frame.get("id"))
        }
        for frame_id in frame_ids:
            visited = set()
            cursor = frame_id
            while cursor is not None and cursor not in visited:
                visited.add(cursor)
                cursor = parent_by_id.get(cursor)
            if cursor is not None:
                errors.append(f"frame graph contains a cycle involving {frame_id}")
                break
            if root_id not in visited:
                errors.append(f"frame {frame_id} is disconnected from root {root_id}")
    if get(data, "product.base_frame") not in frame_ids:
        errors.append("product.base_frame references unknown frame")

    joints = data.get("joints")
    joint_ids = set()
    if not isinstance(joints, list) or not joints:
        errors.append("joints must be a non-empty list")
        joints = []
    for index, joint in enumerate(joints):
        if not isinstance(joint, dict):
            errors.append(f"joints[{index}] must be an object")
            continue
        joint_id = joint.get("id")
        if not present(joint_id):
            errors.append(f"joints[{index}].id is required")
        elif joint_id in joint_ids:
            errors.append(f"duplicate joint id: {joint_id}")
        else:
            joint_ids.add(joint_id)
        for field in ("parent_frame", "child_frame"):
            if joint.get(field) not in frame_ids:
                errors.append(f"joints[{index}].{field} references unknown frame")
        axis = joint.get("axis")
        if not isinstance(axis, list) or len(axis) != 3 or not all(
            isinstance(v, (int, float))
            and not isinstance(v, bool)
            and math.isfinite(v)
            for v in axis
        ):
            errors.append(f"joints[{index}].axis must contain three numbers")
        elif math.sqrt(sum(v * v for v in axis)) < 0.999 or math.sqrt(sum(v * v for v in axis)) > 1.001:
            errors.append(f"joints[{index}].axis must be a unit vector")
        lower, upper, home = joint.get("lower_limit_rad"), joint.get("upper_limit_rad"), joint.get("home_rad")
        if not all(
            isinstance(v, (int, float))
            and not isinstance(v, bool)
            and math.isfinite(v)
            for v in (lower, upper, home)
        ) or not lower < home < upper:
            errors.append(f"joints[{index}] requires lower_limit < home < upper_limit")
        if not present(joint.get("hard_stop_evidence")):
            errors.append(f"joints[{index}].hard_stop_evidence is required")

    load_cases = data.get("load_cases")
    load_cases_by_joint = {}
    if not isinstance(load_cases, list) or not load_cases:
        errors.append("load_cases must be a non-empty list")
    else:
        for index, case in enumerate(load_cases):
            if not isinstance(case, dict):
                errors.append(f"load_cases[{index}] must be an object")
                continue
            for field in ("id", "joint_id", "trajectory_source"):
                if not present(case.get(field)):
                    errors.append(f"load_cases[{index}].{field} is required")
            if case.get("joint_id") not in joint_ids:
                errors.append(f"load_cases[{index}].joint_id references unknown joint")
            else:
                load_cases_by_joint.setdefault(case.get("joint_id"), []).append(case)
            for field in ("payload_kg", "peak_torque_Nm", "rms_torque_Nm", "peak_speed_rad_s", "stop_energy_J"):
                if not positive(case.get(field)):
                    errors.append(f"load_cases[{index}].{field} must be positive")
            if positive(case.get("peak_torque_Nm")) and positive(case.get("rms_torque_Nm")):
                if case["rms_torque_Nm"] > case["peak_torque_Nm"]:
                    errors.append(f"load_cases[{index}] RMS torque cannot exceed peak torque")

    axes = data.get("axes")
    if not isinstance(axes, list) or not axes:
        errors.append("axes must be a non-empty list")
        axes = []
    axis_joint_ids = set()
    axes_by_joint = {}
    for index, axis in enumerate(axes):
        if not isinstance(axis, dict):
            errors.append(f"axes[{index}] must be an object")
            continue
        joint_id = axis.get("joint_id")
        if joint_id not in joint_ids:
            errors.append(f"axes[{index}].joint_id references unknown joint")
        elif joint_id in axis_joint_ids:
            errors.append(f"duplicate axis sizing record for joint: {joint_id}")
        else:
            axis_joint_ids.add(joint_id)
            axes_by_joint[joint_id] = axis
        if not present(axis.get("actuator_part_number")):
            errors.append(f"axes[{index}].actuator_part_number is required")
        numeric = (
            "rated_continuous_torque_Nm", "rated_peak_torque_Nm", "rated_speed_rad_s",
            "gear_ratio", "required_motor_peak_torque_Nm", "required_motor_rms_torque_Nm",
            "required_motor_speed_rad_s", "motor_inertia_kg_m2",
            "reflected_load_inertia_kg_m2", "maximum_inertia_ratio",
        )
        for field in numeric:
            if not positive(axis.get(field)):
                errors.append(f"axes[{index}].{field} must be positive")
        for field in ("forward_efficiency", "reverse_efficiency"):
            value = axis.get(field)
            if not positive(value) or value > 1:
                errors.append(f"axes[{index}].{field} must be > 0 and <= 1")
        if positive(axis.get("required_motor_peak_torque_Nm")) and positive(axis.get("rated_peak_torque_Nm")):
            if axis["required_motor_peak_torque_Nm"] > axis["rated_peak_torque_Nm"]:
                errors.append(f"axes[{index}] required peak torque exceeds rating")
        if positive(axis.get("required_motor_rms_torque_Nm")) and positive(axis.get("rated_continuous_torque_Nm")):
            if axis["required_motor_rms_torque_Nm"] > axis["rated_continuous_torque_Nm"]:
                errors.append(f"axes[{index}] required RMS torque exceeds continuous rating")
        if positive(axis.get("required_motor_speed_rad_s")) and positive(axis.get("rated_speed_rad_s")):
            if axis["required_motor_speed_rad_s"] > axis["rated_speed_rad_s"]:
                errors.append(f"axes[{index}] required speed exceeds rating")
        if positive(axis.get("motor_inertia_kg_m2")) and positive(axis.get("reflected_load_inertia_kg_m2")):
            ratio = axis["reflected_load_inertia_kg_m2"] / axis["motor_inertia_kg_m2"]
            if positive(axis.get("maximum_inertia_ratio")) and ratio > axis["maximum_inertia_ratio"]:
                errors.append(f"axes[{index}] reflected inertia ratio exceeds declared maximum")
        for field in ("thermal_evidence", "transmission_life_evidence"):
            if not present(axis.get(field)):
                errors.append(f"axes[{index}].{field} is required")
        for field in ("gravity_loaded", "hazardous_motion"):
            if not isinstance(axis.get(field), bool):
                errors.append(f"axes[{index}].{field} must be true or false")
        if not present(axis.get("hazard_assessment_id")):
            errors.append(f"axes[{index}].hazard_assessment_id is required")
        if axis.get("gravity_loaded") is True and axis.get("hazardous_motion") is not True:
            errors.append(
                f"axes[{index}] gravity-loaded motion must be classified hazardous"
            )
        if axis.get("hazardous_motion") is False:
            disposition = axis.get("non_hazardous_disposition")
            if not isinstance(disposition, dict):
                errors.append(
                    f"axes[{index}].non_hazardous_disposition must be controlled"
                )
            else:
                for field in ("rationale", "approved_by", "approval_date"):
                    if not present(disposition.get(field)):
                        errors.append(
                            f"axes[{index}].non_hazardous_disposition.{field} is required"
                        )
                try:
                    dt.date.fromisoformat(str(disposition.get("approval_date")))
                except ValueError:
                    errors.append(
                        f"axes[{index}].non_hazardous_disposition.approval_date "
                        "must be YYYY-MM-DD"
                    )
        if not isinstance(axis.get("hazardous_motion"), bool):
            errors.append(f"axes[{index}].hazardous_motion must be true or false")

    missing_axis_coverage = joint_ids - axis_joint_ids
    if missing_axis_coverage:
        errors.append(
            f"moving joints missing actuator sizing records: {sorted(missing_axis_coverage)}"
        )
    missing_load_coverage = joint_ids - set(load_cases_by_joint)
    if missing_load_coverage:
        errors.append(
            f"moving joints missing load-case coverage: {sorted(missing_load_coverage)}"
        )
    for joint_id, axis in axes_by_joint.items():
        cases_for_joint = load_cases_by_joint.get(joint_id, [])
        if not cases_for_joint:
            continue
        peak = max(
            (
                case["peak_torque_Nm"]
                for case in cases_for_joint
                if positive(case.get("peak_torque_Nm"))
            ),
            default=0,
        )
        rms = max(
            (
                case["rms_torque_Nm"]
                for case in cases_for_joint
                if positive(case.get("rms_torque_Nm"))
            ),
            default=0,
        )
        speed = max(
            (
                case["peak_speed_rad_s"]
                for case in cases_for_joint
                if positive(case.get("peak_speed_rad_s"))
            ),
            default=0,
        )
        if all(
            positive(axis.get(field))
            for field in ("gear_ratio", "forward_efficiency", "required_motor_peak_torque_Nm")
        ):
            calculated_peak = peak / (
                axis["gear_ratio"] * axis["forward_efficiency"]
            )
            if axis["required_motor_peak_torque_Nm"] + 1e-12 < calculated_peak:
                errors.append(
                    f"axis {joint_id} required motor peak torque is below "
                    "load-case reconciliation"
                )
        if all(
            positive(axis.get(field))
            for field in ("gear_ratio", "forward_efficiency", "required_motor_rms_torque_Nm")
        ):
            calculated_rms = rms / (
                axis["gear_ratio"] * axis["forward_efficiency"]
            )
            if axis["required_motor_rms_torque_Nm"] + 1e-12 < calculated_rms:
                errors.append(
                    f"axis {joint_id} required motor RMS torque is below "
                    "load-case reconciliation"
                )
        if positive(axis.get("gear_ratio")) and positive(
            axis.get("required_motor_speed_rad_s")
        ):
            calculated_speed = speed * axis["gear_ratio"]
            if axis["required_motor_speed_rad_s"] + 1e-12 < calculated_speed:
                errors.append(
                    f"axis {joint_id} required motor speed is below "
                    "load-case reconciliation"
                )

    bearings = data.get("bearings")
    bearing_joint_ids = set()
    if not isinstance(bearings, list) or not bearings:
        errors.append("bearings must be a non-empty list")
    else:
        for index, bearing in enumerate(bearings):
            if not isinstance(bearing, dict):
                errors.append(f"bearings[{index}] must be an object")
                continue
            for field in ("id", "load_spectrum_source", "lubrication_contamination_basis"):
                if not present(bearing.get(field)):
                    errors.append(f"bearings[{index}].{field} is required")
            if bearing.get("joint_id") not in joint_ids:
                errors.append(f"bearings[{index}].joint_id references unknown joint")
            else:
                bearing_joint_ids.add(bearing.get("joint_id"))
            for field in ("required_life_cycles", "calculated_life_cycles", "static_safety_factor"):
                if not positive(bearing.get(field)):
                    errors.append(f"bearings[{index}].{field} must be positive")
            if positive(bearing.get("required_life_cycles")) and positive(bearing.get("calculated_life_cycles")):
                if bearing["calculated_life_cycles"] < bearing["required_life_cycles"]:
                    errors.append(f"bearings[{index}] calculated life is below required life")
            if positive(bearing.get("required_life_cycles")) and positive(
                get(data, "requirements.life_cycles")
            ):
                if bearing["required_life_cycles"] < get(
                    data, "requirements.life_cycles"
                ):
                    errors.append(
                        f"bearings[{index}] required life is below product life requirement"
                    )
    missing_bearing_coverage = joint_ids - bearing_joint_ids
    if missing_bearing_coverage:
        errors.append(
            f"moving joints missing bearing-life coverage: {sorted(missing_bearing_coverage)}"
        )

    if positive(get(data, "performance_budget.predicted_endpoint_error_m")) and positive(get(data, "performance_budget.allowable_endpoint_error_m")):
        if get(data, "performance_budget.predicted_endpoint_error_m") > get(data, "performance_budget.allowable_endpoint_error_m"):
            errors.append("predicted endpoint error exceeds allowable endpoint error")
    for path in (
        "performance_budget.backlash_evidence", "performance_budget.stiffness_evidence",
        "performance_budget.calibration_evidence", "cables_and_sensors.routing_evidence",
        "cables_and_sensors.cycle_life_evidence", "cables_and_sensors.homing_evidence",
        "cables_and_sensors.fault_response_evidence", "robot_description.artifact",
        "robot_description.frame_round_trip_evidence",
        "robot_description.inertia_validation_evidence", "safety.protective_stop_evidence",
    ):
        if not present(get(data, path)):
            errors.append(f"missing controlled value: {path}")
    source_hash = get(data, "robot_description.source_hash")
    if not isinstance(source_hash, str) or not SHA256.fullmatch(source_hash):
        errors.append("robot_description.source_hash must be a 64-character hexadecimal SHA-256")
    limitations = get(data, "robot_description.declared_model_limitations")
    if not isinstance(limitations, list):
        errors.append("robot_description.declared_model_limitations must be a list")

    stopping = data.get("stopping")
    stopping_axes = []
    if not isinstance(stopping, dict):
        errors.append("stopping must be an object")
    elif not isinstance(stopping.get("hazardous_axes"), list):
        errors.append("stopping.hazardous_axes must be a list")
    else:
        stopping_axes = stopping["hazardous_axes"]
    hazardous_joint_ids = {
        axis.get("joint_id") for axis in axes
        if isinstance(axis, dict) and axis.get("hazardous_motion") is True
    }
    covered_joint_ids = set()
    for index, stop in enumerate(stopping_axes):
        if not isinstance(stop, dict):
            errors.append(f"stopping.hazardous_axes[{index}] must be an object")
            continue
        joint_id = stop.get("joint_id")
        if joint_id not in hazardous_joint_ids:
            errors.append(
                f"stopping.hazardous_axes[{index}].joint_id must reference a hazardous axis"
            )
        elif joint_id in covered_joint_ids:
            errors.append(f"duplicate stopping evidence for hazardous axis: {joint_id}")
        else:
            covered_joint_ids.add(joint_id)
        for field in (
            "required_hold_torque_Nm", "brake_hold_capacity_Nm",
            "required_stop_energy_J", "brake_dynamic_energy_capacity_J",
        ):
            if not positive(stop.get(field)):
                errors.append(f"stopping.hazardous_axes[{index}].{field} must be positive")
        for field in (
            "power_loss_safe_state", "power_loss_test",
            "stopping_analysis_evidence", "brake_proof_evidence",
        ):
            if not present(stop.get(field)):
                errors.append(f"stopping.hazardous_axes[{index}].{field} is required")
        if positive(stop.get("required_hold_torque_Nm")) and positive(stop.get("brake_hold_capacity_Nm")):
            if stop["brake_hold_capacity_Nm"] < stop["required_hold_torque_Nm"]:
                errors.append(f"hazardous axis {joint_id} brake hold capacity is below required hold torque")
        if positive(stop.get("required_stop_energy_J")) and positive(stop.get("brake_dynamic_energy_capacity_J")):
            if stop["brake_dynamic_energy_capacity_J"] < stop["required_stop_energy_J"]:
                errors.append(f"hazardous axis {joint_id} brake dynamic energy capacity is below required stop energy")
        load_stop_energy = max(
            (
                case.get("stop_energy_J", 0)
                for case in load_cases_by_joint.get(joint_id, [])
                if positive(case.get("stop_energy_J"))
            ),
            default=0,
        )
        if positive(stop.get("required_stop_energy_J")) and load_stop_energy > stop[
            "required_stop_energy_J"
        ]:
            errors.append(
                f"hazardous axis {joint_id} required stop energy is below "
                "the governing load case"
            )
    uncovered = hazardous_joint_ids - covered_joint_ids
    if uncovered:
        errors.append(f"hazardous axes missing stopping/brake evidence: {sorted(uncovered)}")

    release_evidence = data.get("release_evidence")
    seen_evidence = set()
    if not isinstance(release_evidence, list):
        errors.append("release_evidence must be a list")
        release_evidence = []
    for index, item in enumerate(release_evidence):
        if not isinstance(item, dict):
            errors.append(f"release_evidence[{index}] must be an object")
            continue
        kind = item.get("type")
        if kind in seen_evidence:
            errors.append(f"duplicate release evidence type: {kind}")
        seen_evidence.add(kind)
        if not present(kind) or not present(item.get("artifact")):
            errors.append(f"release_evidence[{index}] requires type and artifact")
        if not isinstance(item.get("source_hash"), str) or not SHA256.fullmatch(
            item.get("source_hash", "")
        ):
            errors.append(
                f"release_evidence[{index}].source_hash must be a controlled SHA-256"
            )
        if item.get("configuration") != get(data, "product.configuration"):
            errors.append(
                f"release_evidence[{index}].configuration must match product configuration"
            )
        expected_status = "available" if kind == "physical_verification_plan" else "pass"
        if item.get("status") != expected_status:
            errors.append(
                f"release_evidence[{index}] type {kind} must have status={expected_status}"
            )

    if maturity in {"production_candidate", "released"}:
        missing = REQUIRED_EVIDENCE - seen_evidence
        if missing:
            errors.append(f"production maturity missing release evidence: {sorted(missing)}")
        approvals = data.get("approvals")
        if not isinstance(approvals, list) or not approvals:
            errors.append("production maturity requires approvals")
        else:
            authority_coverage = False
            for index, approval in enumerate(approvals):
                if not isinstance(approval, dict):
                    errors.append(f"approvals[{index}] must be an object")
                    continue
                for field in ("approver", "role", "date", "scope", "decision"):
                    if not present(approval.get(field)):
                        errors.append(f"approvals[{index}].{field} is required")
                try:
                    dt.date.fromisoformat(str(approval.get("date")))
                except ValueError:
                    errors.append(f"approvals[{index}].date must be YYYY-MM-DD")
                if approval.get("decision") != "approved":
                    errors.append(f"approvals[{index}].decision must be approved")
                if (
                    approval.get("role")
                    == get(data, "product.acceptance_authority_role")
                    and approval.get("configuration")
                    == get(data, "product.configuration")
                    and approval.get("decision") == "approved"
                ):
                    authority_coverage = True
            if not authority_coverage:
                errors.append(
                    "approval from product.acceptance_authority_role for the "
                    "product configuration is required"
                )
        if record_state != "controlled_evidence":
            warnings.append("template/fixture record cannot receive a production PASS")
    else:
        warnings.append("non-production maturity: release-evidence completeness is not enforced")

    physical = data.get("physical_verification")
    if not isinstance(physical, dict):
        errors.append("physical_verification must be an object")
    else:
        state = physical.get("state")
        allowed_states = {"planned", "available", "in_progress", "passed", "failed"}
        if state not in allowed_states:
            errors.append(f"physical_verification.state must be one of {sorted(allowed_states)}")
        if not present(physical.get("plan_artifact")):
            errors.append("physical_verification.plan_artifact is required")
        if state == "passed":
            for field in (
                "acceptance_evidence",
                "acceptance_evidence_hash",
                "accepted_by",
                "accepted_by_role",
                "acceptance_date",
                "configuration",
            ):
                if not present(physical.get(field)):
                    errors.append(f"passed physical verification requires {field}")
            if not isinstance(
                physical.get("acceptance_evidence_hash"), str
            ) or not SHA256.fullmatch(physical.get("acceptance_evidence_hash", "")):
                errors.append(
                    "physical_verification.acceptance_evidence_hash must be a controlled SHA-256"
                )
            if physical.get("accepted_by_role") != get(
                data, "product.acceptance_authority_role"
            ):
                errors.append(
                    "physical_verification.accepted_by_role must match "
                    "product.acceptance_authority_role"
                )
            if physical.get("configuration") != get(
                data, "product.configuration"
            ):
                errors.append(
                    "physical_verification.configuration must match product configuration"
                )
            try:
                dt.date.fromisoformat(str(physical.get("acceptance_date")))
            except ValueError:
                errors.append("physical_verification.acceptance_date must be YYYY-MM-DD")
            physical_acceptance = [
                item for item in release_evidence
                if isinstance(item, dict) and item.get("type") == "physical_acceptance"
            ]
            if (
                len(physical_acceptance) != 1
                or physical_acceptance[0].get("status") != "pass"
                or physical_acceptance[0].get("artifact")
                != physical.get("acceptance_evidence")
                or physical_acceptance[0].get("source_hash")
                != physical.get("acceptance_evidence_hash")
            ):
                errors.append("passed physical verification requires physical_acceptance evidence with status=pass")
        elif maturity == "released":
            errors.append("released maturity requires passed physical verification")
        elif state == "failed":
            errors.append("failed physical verification blocks production maturity")

    if errors:
        verdict = "FAIL"
    elif record_state != "controlled_evidence":
        verdict = "DRAFT"
    elif maturity in {"concept", "prototype"}:
        verdict = "DRAFT"
    elif maturity == "verification":
        verdict = "CONDITIONAL"
    elif maturity == "released":
        release = data.get("release")
        if not isinstance(release, dict):
            errors.append("released maturity requires release baseline metadata")
        else:
            for field in ("baseline_id", "effectivity", "release_authority_record"):
                if not present(release.get(field)):
                    errors.append(f"release.{field} is required for released maturity")
        verdict = "FAIL" if errors else "RELEASED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(json.loads(args.contract.read_text(encoding="utf-8")))
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["verdict"] in {"PASS", "RELEASED"} else 2


if __name__ == "__main__":
    sys.exit(main())
