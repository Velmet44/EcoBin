#!/usr/bin/env python3
"""Regression tests for bom_contract_validate.py."""

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bom_validator", ROOT / "scripts" / "bom_contract_validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def effectivity():
    return {
        "configurations": ["BASE"], "serial_from": None, "serial_to": None,
        "date_from": "2026-07-24", "date_to": None, "sites": ["PLANT-1"],
    }


def valid_contract():
    return {
        "schema_version": "1.1",
        "record_state": "controlled_evidence",
        "product": {
            "part_number": "ASM-100", "revision": "A", "name": "robot module",
            "lifecycle_state": "production_candidate", "owner": "robotics engineering",
            "units": "mm", "currency": "USD", "cost_basis_date": "2026-07-24",
            "configuration_procedure": "CM-PROC-001", "acceptance_authority_role": "configuration authority",
        },
        "source_systems": [
            {"domain": "CAD", "system": "FreeCAD 1.1.2", "extract_id": "CAD-X1", "extracted_at": "2026-07-24T12:00:00Z", "source_hash": "a" * 64}
        ],
        "configurations": [{"id": "BASE", "status": "candidate", "effectivity": effectivity()}],
        "definitions": [
            {
                "part_number": "ASM-100", "revision": "A", "description": "robot module",
                "item_type": "make", "uom": "EA", "criticality": "major",
                "material_spec": "per child definitions", "finish": "per child definitions",
            },
            {
                "part_number": "SRV-010", "revision": "B", "description": "servo",
                "item_type": "buy", "uom": "EA", "criticality": "critical",
                "material_spec": None, "finish": None,
            },
        ],
        "views": [
            {"id": "EBOM-A", "type": "ebom", "revision": "A", "authority": "PLM", "status": "candidate"},
            {"id": "MBOM-A", "type": "mbom", "revision": "A", "authority": "MES", "status": "candidate"},
        ],
        "occurrences": [
            {
                "id": "E-ROOT", "view_id": "EBOM-A", "parent_id": None,
                "part_number": "ASM-100", "revision": "A", "quantity": 1,
                "configuration_ids": ["BASE"],
            },
            {
                "id": "E-SERVO", "view_id": "EBOM-A", "parent_id": "E-ROOT",
                "part_number": "SRV-010", "revision": "B", "quantity": 1,
                "configuration_ids": ["BASE"],
            },
            {
                "id": "M-ROOT", "view_id": "MBOM-A", "parent_id": None,
                "part_number": "ASM-100", "revision": "A", "quantity": 1,
                "configuration_ids": ["BASE"],
            },
            {
                "id": "M-SERVO", "view_id": "MBOM-A", "parent_id": "M-ROOT",
                "part_number": "SRV-010", "revision": "B", "quantity": 1,
                "configuration_ids": ["BASE"],
            },
        ],
        "transformations": [
            {
                "id": "X-SERVO", "source_occurrence_ids": ["E-SERVO"],
                "target_occurrence_ids": ["M-SERVO"], "quantity_factor": 1,
                "reason": "direct issue", "approval": "CM-APP-1", "effectivity": effectivity(),
            }
        ],
        "approved_sources": [
            {
                "id": "ASL-1", "part_number": "SRV-010", "revision": "B",
                "manufacturer": "Servo Co", "manufacturer_part_number": "SV10",
                "supplier": "Authorized Distributor", "supplier_part_number": "SV10-D",
                "status": "approved", "lifecycle": "active", "lead_time_days": 42,
                "moq": 1, "order_multiple": 1, "evidence": "ASL-001.pdf",
            }
        ],
        "alternates": [],
        "deviations": [],
        "changes": [
            {
                "id": "ECO-1", "state": "approved", "reason": "servo revision update",
                "affected_definition_keys": [{"part_number": "SRV-010", "revision": "B"}],
                "affected_view_ids": ["EBOM-A", "MBOM-A"],
                "where_used_evidence": "where-used-ECO-1.json", "effectivity": effectivity(),
                "approval": "CCB-2026-44",
            }
        ],
        "cost_records": [
            {
                "part_number": "ASM-100", "revision": "A", "cost_type": "conversion",
                "unit_cost": 75, "currency": "USD", "quantity_basis": 100,
                "source": "manufacturing-plan-42.json", "valid_from": "2026-07-24", "valid_to": "2027-07-23",
            },
            {
                "part_number": "SRV-010", "revision": "B", "cost_type": "purchase",
                "unit_cost": 120, "currency": "USD", "quantity_basis": 100,
                "source": "quote-Q44.pdf", "valid_from": "2026-07-24", "valid_to": "2026-10-24",
            },
        ],
        "as_built_units": [
            {
                "product_serial": "RM-0001", "configuration_id": "BASE", "bom_baseline": "EBOM-A/MBOM-A",
                "work_order": "WO-001", "build_date": "2026-07-24", "site": "PLANT-1",
                "installed_items": [
                    {
                        "occurrence_id": "E-SERVO", "part_number": "SRV-010", "revision": "B",
                        "quantity": 1, "traceability_type": "serial", "serial": "SV-991",
                        "lot": None, "evidence": "traveler-WO-001.pdf",
                    }
                ],
                "evidence": "acceptance-RM-0001.pdf",
            }
        ],
        "maintenance_events": [],
        "reconciliations": [
            {
                "id": "R-CAD", "type": "cad_to_ebom", "configuration_ids": ["BASE"],
                "status": "pass", "differences": [], "artifact": "cad-ebom-diff.json", "source_hash": "b" * 64,
            },
            {
                "id": "R-MFG", "type": "ebom_to_mbom", "configuration_ids": ["BASE"],
                "status": "pass", "differences": [], "artifact": "ebom-mbom-diff.json", "source_hash": "c" * 64,
            },
        ],
        "approvals": [
            {
                "approver": "A. Engineer", "role": "configuration authority",
                "date": "2026-07-24", "scope": "ASM-100 revision A production candidate",
                "configuration_ids": ["BASE"], "decision": "approved",
            }
        ],
    }


def expect(data, verdict, phrase=None):
    report = MODULE.validate(data)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in item for item in report["errors"]), report


def add_substitute(data):
    data["definitions"].append({
        "part_number": "SRV-011", "revision": "A", "description": "qualified alternate servo",
        "item_type": "buy", "uom": "EA", "criticality": "critical",
        "material_spec": None, "finish": None,
    })
    data["approved_sources"].append({
        "id": "ASL-2", "part_number": "SRV-011", "revision": "A",
        "manufacturer": "Servo Co 2", "manufacturer_part_number": "SV11",
        "supplier": "Authorized Distributor", "supplier_part_number": "SV11-D",
        "status": "approved", "lifecycle": "active", "lead_time_days": 35,
        "moq": 1, "order_multiple": 1, "evidence": "ASL-002.pdf",
    })
    data["cost_records"].append({
        "part_number": "SRV-011", "revision": "A", "cost_type": "purchase",
        "unit_cost": 125, "currency": "USD", "quantity_basis": 100,
        "source": "quote-Q45.pdf", "valid_from": "2026-07-24", "valid_to": "2026-10-24",
    })
    item = data["as_built_units"][0]["installed_items"][0]
    item["part_number"] = "SRV-011"
    item["revision"] = "A"


base = valid_contract()
expect(base, "PASS")
assert base["product"]["currency"] == "USD"
report = MODULE.validate(base)
assert report["metrics"]["configured_cost_by_configuration"]["BASE"] == 195.0, report

case = copy.deepcopy(base)
case["occurrences"][1]["quantity"] = 10
case["occurrences"][3]["quantity"] = 10
report = MODULE.validate(case)
assert report["verdict"] == "PASS", report
assert report["metrics"]["configured_cost_by_configuration"]["BASE"] == 1275.0, report

case = copy.deepcopy(base)
case["occurrences"][0]["parent_id"] = "E-SERVO"
expect(case, "FAIL", "cycle")

case = copy.deepcopy(base)
case["views"] = [case["views"][0]]
expect(case, "FAIL", "ebom and mbom")

case = copy.deepcopy(base)
case["transformations"][0]["target_occurrence_ids"] = ["MISSING"]
expect(case, "FAIL", "known occurrences")

case = copy.deepcopy(base)
case["transformations"][0]["target_occurrence_ids"] = ["E-SERVO"]
expect(case, "FAIL", "explicit eBOM-to-mBOM")

case = copy.deepcopy(base)
case["approved_sources"][0]["status"] = "proposed"
expect(case, "FAIL", "lacks an approved source")

case = copy.deepcopy(base)
case["alternates"] = [{
    "primary_part": {"part_number": "SRV-010", "revision": "B"},
    "alternate_part": {"part_number": "NOPE", "revision": "X"},
    "class": "equivalent", "restrictions": "none", "qualification_evidence": "Q.pdf",
    "approval": "CCB", "effectivity": effectivity(),
}]
expect(case, "FAIL", "known definition")

case = copy.deepcopy(base)
case["cost_records"][1]["currency"] = "EUR"
expect(case, "FAIL", "differs from product currency")

case = copy.deepcopy(base)
case["cost_records"][1]["valid_from"] = "2026-01-01"
case["cost_records"][1]["valid_to"] = "2026-07-23"
expect(case, "FAIL", "cost_basis_date")

case = copy.deepcopy(base)
case["as_built_units"][0]["installed_items"][0]["serial"] = None
expect(case, "FAIL", "lacks serial")

case = copy.deepcopy(base)
add_substitute(case)
expect(case, "FAIL", "lacks an effective approved alternate or deviation")

case = copy.deepcopy(base)
add_substitute(case)
case["alternates"] = [{
    "primary_part": {"part_number": "SRV-010", "revision": "B"},
    "alternate_part": {"part_number": "SRV-011", "revision": "A"},
    "class": "equivalent", "restrictions": "same interface and qualified firmware",
    "qualification_evidence": "ALT-Q-1.pdf", "approval": "CCB-45",
    "effectivity": effectivity(),
}]
expect(case, "PASS")

case = copy.deepcopy(base)
add_substitute(case)
case["as_built_units"][0]["installed_items"][0]["deviation_id"] = "DEV-1"
case["deviations"] = [{
    "id": "DEV-1", "status": "approved",
    "nominal_part": {"part_number": "SRV-010", "revision": "B"},
    "substitute_part": {"part_number": "SRV-011", "revision": "A"},
    "product_serials": ["RM-0001"], "reason": "bounded shortage substitution",
    "evidence": "DEV-1.pdf",
    "approval": {
        "approver": "C. Authority", "role": "configuration authority",
        "date": "2026-07-24", "decision": "approved",
    },
}]
expect(case, "PASS")

case = copy.deepcopy(base)
case["definitions"].append({
    "part_number": "FW-1", "revision": "1.2.0", "description": "controller firmware",
    "item_type": "firmware", "uom": "EA", "criticality": "critical",
})
case["occurrences"].append({
    "id": "E-FW", "view_id": "EBOM-A", "parent_id": "E-ROOT",
    "part_number": "FW-1", "revision": "1.2.0", "quantity": 1,
    "configuration_ids": ["BASE"],
})
case["as_built_units"][0]["installed_items"].append({
    "occurrence_id": "E-FW", "part_number": "FW-1", "revision": "1.2.0",
    "quantity": 1, "traceability_type": "none", "version": "1.2.0",
    "checksum": None, "target": "CTRL-1", "evidence": "load-log.txt",
})
expect(case, "FAIL", "checksum")

case = copy.deepcopy(base)
case["reconciliations"][1]["status"] = "conditional"
expect(case, "FAIL", "requires passing")

case = copy.deepcopy(base)
case["source_systems"][0]["source_hash"] = "not-a-hash"
expect(case, "FAIL", "source_hash")

case = copy.deepcopy(base)
case["reconciliations"][0]["source_hash"] = "not-a-hash"
expect(case, "FAIL", "source_hash")

case = copy.deepcopy(base)
case["approvals"][0]["role"] = "designer"
expect(case, "FAIL", "acceptance-authority")

case = copy.deepcopy(base)
case["approvals"] = ["approved"]
expect(case, "FAIL", "approvals[0]")

print("BOM/configuration validator regression tests: PASS")
