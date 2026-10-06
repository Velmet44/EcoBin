#!/usr/bin/env python3
"""Adversarial regression tests for assembly_contract_validate.py."""

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "assembly_validator", ROOT / "scripts" / "assembly_contract_validate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_contract():
    data = json.loads((ROOT / "assets" / "assembly-contract.json").read_text())
    data["product"].update({
        "part_number": "ASM-001",
        "name": "validated assembly",
        "maturity": "production_candidate",
        "coordinate_system": "ASM_ORIGIN",
        "governing_product_definition": "ISO GPS",
        "acceptance_authority_role": "design authority",
    })
    data["configurations"][0].update({"effectivity": "all units", "status": "candidate"})
    data["definitions"][0].update({"part_number": "ASM-001", "revision": "A"})
    data["definitions"][0]["mass"].update({
        "value": 1.0, "source": "CAD-001", "applicability": "required"
    })
    data["occurrences"][0].update({"part_number": "ASM-001", "revision": "A"})
    data["definitions"].append({
        "part_number": "PART-001",
        "revision": "A",
        "description": "controlled child part",
        "item_type": "make",
        "component_record": None,
        "mass": {
            "value": 0.5,
            "unit": "kg",
            "source": "CAD-002",
            "applicability": "required",
            "justification": None,
        },
    })
    data["occurrences"].append({
        "occurrence_id": "OCC-002",
        "parent_occurrence_id": "OCC-001",
        "part_number": "PART-001",
        "revision": "A",
        "quantity": 1,
        "configuration_ids": ["BASE"],
        "rigid_at_parent": True,
    })
    data["grounding"][0].update({"datum": "ASM_ORIGIN", "intent": "product base"})
    data["test_cases"] = [{
        "id": "TEST-001",
        "kind": "fit_stack",
        "configuration_id": "BASE",
        "status": "pass",
        "expected": "clearance >= 0.2 mm",
        "actual": "clearance 0.25 mm",
        "evidence": ["fit-report.json"],
    }]
    data["joints"] = [{
        "joint_id": "JOINT-001",
        "occurrence_a": "OCC-001",
        "occurrence_b": "OCC-002",
        "type": "fixed",
        "expected_remaining_dof": 0,
        "test_case_ids": ["TEST-001"],
    }]
    data["interfaces"] = [{
        "interface_id": "IF-001",
        "configuration_id": "BASE",
        "occurrence_a": "OCC-001",
        "datum_a": "ASM_ORIGIN",
        "occurrence_b": "OCC-002",
        "datum_b": "PART_DATUM",
        "function": "controlled mounting clearance",
        "classification": "clearance",
        "standard_and_edition": "ISO 286-1:2010",
        "worst_case_min": "0.25 mm",
        "worst_case_max": "0.40 mm",
        "thermal_coating_load_basis": "20-60 C; no coating",
        "test_case_id": "TEST-001",
        "status": "pass",
        "evidence": ["fit-report.json"],
    }]
    data["release_evidence"] = [
        {
            "evidence_id": f"E-{kind}",
            "type": kind,
            "configuration_ids": ["BASE"],
            "status": "pass",
            "artifact": f"{kind}.json",
            "source_hash": "a" * 64,
        }
        for kind in MODULE.REQUIRED_EVIDENCE
    ]
    data["approvals"] = [{
        "approver": "A. Engineer",
        "role": "design authority",
        "date": "2026-07-24",
        "scope": "ASM-001 revision A production candidate",
        "configuration_ids": ["BASE"],
        "decision": "approved",
    }]
    return data


def expect(data, verdict, phrase=None):
    report = MODULE.validate(data)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in error for error in report["errors"]), report


base = valid_contract()
expect(base, "PASS")

case = copy.deepcopy(base)
case["occurrences"].append({
    "occurrence_id": "ROOT-2", "parent_occurrence_id": None,
    "part_number": "ASM-001", "revision": "A", "quantity": 1,
    "configuration_ids": ["BASE"], "rigid_at_parent": True,
})
expect(case, "FAIL", "exactly one root")

case = copy.deepcopy(base)
case["interfaces"] = [{}]
expect(case, "FAIL", "interfaces[0]")

case = copy.deepcopy(base)
case["test_cases"][0]["status"] = "planned"
expect(case, "FAIL", "must have status=pass")

case = copy.deepcopy(base)
case["approvals"] = ["ok"]
expect(case, "FAIL", "approvals[0]")

case = copy.deepcopy(base)
case["grounding"].append(copy.deepcopy(case["grounding"][0]))
expect(case, "FAIL", "exactly one intentional ground")

case = copy.deepcopy(base)
case["definitions"][0]["item_type"] = "reference"
case["definitions"][0]["mass"].update({
    "value": None, "source": "not applicable", "applicability": "non_mass_item"
})
expect(case, "PASS")

case = copy.deepcopy(base)
case["definitions"][0]["item_type"] = "consumable"
case["definitions"][0]["component_record"] = None
case["definitions"][0]["mass"].update({
    "value": None, "source": "batch record", "applicability": "included_in_parent",
    "justification": "measured in cured parent assembly",
})
expect(case, "FAIL", "governed component_record")

case = copy.deepcopy(base)
case["occurrences"][0]["parent_occurrence_id"] = "OCC-001"
expect(case, "FAIL", "cycle")

case = copy.deepcopy(base)
case["interfaces"][0]["worst_case_min"] = "banana"
expect(case, "FAIL", "signed value")

case = copy.deepcopy(base)
case["product"] = None
expect(case, "FAIL", "product must be")

case = copy.deepcopy(base)
case["occurrences"] = None
expect(case, "FAIL", "occurrences must be a list")

print("assembly contract validator regression tests: PASS")
