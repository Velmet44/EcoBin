#!/usr/bin/env python3
"""Adversarial regression tests for reliability_risk_validate.py."""

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "risk_validator", ROOT / "scripts" / "reliability_risk_validate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_contract():
    return json.loads((ROOT / "assets" / "reliability-risk-contract.json").read_text())


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
case["failure_modes"][0]["rpn"] = 59
expect(case, "FAIL", "rpn arithmetic")

case = copy.deepcopy(base)
case["failure_modes"][0]["hazard_ids"] = []
expect(case, "FAIL", "requires hazard linkage")

case = copy.deepcopy(base)
case["failure_modes"][0]["action_ids"] = []
expect(case, "FAIL", "requires closed verified actions")

case = copy.deepcopy(base)
case["failure_modes"][0]["severity"] = 8
case["failure_modes"][0]["rpn"] = 8 * 2 * 3
case["failure_modes"][0]["hazard_ids"] = []
expect(case, "FAIL", "safety-related")

case = copy.deepcopy(base)
case["failure_modes"][0]["severity"] = 8
case["failure_modes"][0]["rpn"] = 8 * 2 * 3
case["failure_modes"][0]["action_ids"] = []
expect(case, "FAIL", "safety-related")

case = copy.deepcopy(base)
case["failure_modes"][0]["safety_related"] = "yes"
expect(case, "FAIL", "must be true or false")

case = copy.deepcopy(base)
case["actions"][0]["status"] = "closed"
case["actions"][0]["verification_evidence"] = "TBD"
expect(case, "FAIL", "closed action")

case = copy.deepcopy(base)
case["actions"][0]["post_rpn"] = 21
expect(case, "FAIL", "post_rpn arithmetic")

case = copy.deepcopy(base)
case["hazards"][0]["measure_ids"] = ["MISSING"]
expect(case, "FAIL", "unknown measure")

case = copy.deepcopy(base)
case["hazards"] = []
expect(case, "FAIL", "at least one hazard")

case = copy.deepcopy(base)
case["coverage_exclusions"] = []
expect(case, "FAIL", "process steps lack PFMEA coverage")

case = copy.deepcopy(base)
case["residual_risk_approvals"][0]["decision"] = "pending"
expect(case, "FAIL", "decision must be accepted")

case = copy.deepcopy(base)
case["life_evidence"][0]["demonstrated_or_calculated_cycles"] = 900000
expect(case, "FAIL", "does not meet required")

case = copy.deepcopy(base)
case["life_evidence"][0]["demonstrated_or_calculated_cycles"] = float("nan")
expect(case, "FAIL", "must be positive")

case = copy.deepcopy(base)
case["change_control"]["open_change_impacts"] = ["CHG-001 brake supplier"]
expect(case, "FAIL", "open change impacts")

case = copy.deepcopy(base)
case["change_control"]["input_hashes"] = ["bad"]
expect(case, "FAIL", "SHA-256")

case = copy.deepcopy(base)
case["release_evidence"][0]["status"] = "planned"
expect(case, "FAIL", "status=pass")

case = copy.deepcopy(base)
case["release_evidence"][0]["source_hash"] = "bad"
expect(case, "FAIL", "source_hash")

case = copy.deepcopy(base)
case["product"]["acceptance_authority_role"] = "unassigned role"
expect(case, "FAIL", "acceptance_authority_role")

case = copy.deepcopy(base)
case["approvals"][0]["role"] = "designer"
expect(case, "FAIL", "acceptance-authority")

case = copy.deepcopy(base)
case["product"]["maturity"] = "prototype"
case["actions"][0]["status"] = "open"
case["actions"][0]["implementation_artifact"] = None
case["actions"][0]["verification_evidence"] = None
case["release_evidence"] = []
case["approvals"] = []
expect(case, "DRAFT")

case = copy.deepcopy(base)
case["product"]["maturity"] = "verification"
case["actions"][0]["status"] = "open"
case["actions"][0]["implementation_artifact"] = None
case["actions"][0]["verification_evidence"] = None
case["release_evidence"] = []
case["approvals"] = []
expect(case, "CONDITIONAL")

expect(None, "FAIL", "JSON object")

print("reliability/risk validator regression tests: PASS")
