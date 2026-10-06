#!/usr/bin/env python3
"""Adversarial regression tests for robot_mechanism_validate.py."""

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "robot_validator", ROOT / "scripts" / "robot_mechanism_validate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_contract():
    return json.loads((ROOT / "assets" / "robot-mechanism-contract.json").read_text())


def controlled_contract():
    data = valid_contract()
    data["record_state"] = "controlled_evidence"
    return data


def expect(data, verdict, phrase=None):
    report = MODULE.validate(data)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in error for error in report["errors"]), report


expect(valid_contract(), "DRAFT")
base = controlled_contract()
expect(base, "PASS")

case = copy.deepcopy(base)
case["frames"].append(copy.deepcopy(case["frames"][0]))
expect(case, "FAIL", "duplicate frame")

case = copy.deepcopy(base)
case["frames"][1]["parent"] = "link1"
expect(case, "FAIL", "cycle")

case = copy.deepcopy(base)
case["joints"][0]["axis"] = [0, 0, 2]
expect(case, "FAIL", "unit vector")

case = copy.deepcopy(base)
case["joints"][0]["home_rad"] = 4
expect(case, "FAIL", "lower_limit < home < upper_limit")

case = copy.deepcopy(base)
case["load_cases"][0]["rms_torque_Nm"] = 50
expect(case, "FAIL", "RMS torque")

case = copy.deepcopy(base)
case["axes"][0]["required_motor_peak_torque_Nm"] = 4
expect(case, "FAIL", "load-case reconciliation")

case = copy.deepcopy(base)
case["axes"][0]["required_motor_peak_torque_Nm"] = 19
expect(case, "FAIL", "peak torque exceeds")

case = copy.deepcopy(base)
case["axes"][0]["reflected_load_inertia_kg_m2"] = 0.007
expect(case, "FAIL", "inertia ratio")

case = copy.deepcopy(base)
case["bearings"][0]["calculated_life_cycles"] = 900000
expect(case, "FAIL", "below required life")

case = copy.deepcopy(base)
case["stopping"]["hazardous_axes"][0]["brake_dynamic_energy_capacity_J"] = 100
expect(case, "FAIL", "dynamic energy")

case = copy.deepcopy(base)
case["stopping"]["hazardous_axes"][0]["required_stop_energy_J"] = 100
expect(case, "FAIL", "governing load case")

case = copy.deepcopy(base)
case["axes"][0]["hazardous_motion"] = False
expect(case, "FAIL", "gravity-loaded")

case = copy.deepcopy(base)
case["stopping"]["hazardous_axes"] = []
expect(case, "FAIL", "missing stopping/brake evidence")

case = copy.deepcopy(base)
second_axis = copy.deepcopy(case["axes"][0])
second_axis["joint_id"] = "J2"
case["axes"].append(second_axis)
case["joints"].append({
    "id": "J2",
    "parent_frame": "link1",
    "child_frame": "tool0",
    "axis": [0, 1, 0],
    "lower_limit_rad": -1.0,
    "upper_limit_rad": 1.0,
    "home_rad": 0.0,
    "hard_stop_evidence": "TEST-STOP-002",
})
expect(case, "FAIL", "J2")

case = copy.deepcopy(base)
case["performance_budget"]["predicted_endpoint_error_m"] = 0.002
expect(case, "FAIL", "endpoint error")

case = copy.deepcopy(base)
case["release_evidence"][0]["status"] = "planned"
expect(case, "FAIL", "status=pass")

case = copy.deepcopy(base)
case["release_evidence"][0]["source_hash"] = "bad"
expect(case, "FAIL", "source_hash")

case = copy.deepcopy(base)
case["release_evidence"] = [
    item for item in case["release_evidence"]
    if item["type"] != "motion_dynamics_validation"
]
expect(case, "FAIL", "motion_dynamics_validation")

case = copy.deepcopy(base)
case["robot_description"]["source_hash"] = "not-a-hash"
expect(case, "FAIL", "64-character")

case = copy.deepcopy(base)
case["product"]["acceptance_authority_role"] = "unassigned role"
expect(case, "FAIL", "acceptance_authority_role")

case = copy.deepcopy(base)
case["approvals"][0]["role"] = "designer"
expect(case, "FAIL", "acceptance_authority_role")

case = copy.deepcopy(base)
case["product"]["maturity"] = "prototype"
case["release_evidence"] = []
case["approvals"] = []
expect(case, "DRAFT")

case = copy.deepcopy(base)
case["product"]["maturity"] = "verification"
case["release_evidence"] = []
case["approvals"] = []
expect(case, "CONDITIONAL")

case = copy.deepcopy(base)
case["physical_verification"] = {
    "state": "passed",
    "plan_artifact": "PLAN-001",
    "acceptance_evidence": "REPORT-ACCEPT-001",
    "acceptance_evidence_hash": "9999999999999999999999999999999999999999999999999999999999999999",
    "accepted_by": "A. Test",
    "accepted_by_role": "robotics design authority",
    "acceptance_date": "2026-07-24",
    "configuration": "PAYLOAD-5KG",
}
expect(case, "FAIL", "physical_acceptance evidence")

case = copy.deepcopy(base)
case["physical_verification"] = {
    "state": "passed",
    "plan_artifact": "PLAN-001",
    "acceptance_evidence": "REPORT-ACCEPT-001",
    "acceptance_evidence_hash": "9999999999999999999999999999999999999999999999999999999999999999",
    "accepted_by": "A. Test",
    "accepted_by_role": "robotics design authority",
    "acceptance_date": "2026-07-24",
    "configuration": "PAYLOAD-5KG",
}
case["release_evidence"].append({
    "type": "physical_acceptance",
    "artifact": "REPORT-ACCEPT-001",
    "source_hash": "9999999999999999999999999999999999999999999999999999999999999999",
    "configuration": "PAYLOAD-5KG",
    "status": "pass",
})
expect(case, "PASS")

case = copy.deepcopy(base)
case["product"]["maturity"] = "released"
expect(case, "FAIL", "released maturity requires passed")

expect(None, "FAIL", "JSON object")

print("robot mechanism validator regression tests: PASS")
