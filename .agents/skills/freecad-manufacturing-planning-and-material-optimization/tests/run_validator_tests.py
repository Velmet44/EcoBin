#!/usr/bin/env python3
"""Regression tests for manufacturing_plan_validate.py."""

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("plan_validator", ROOT / "scripts" / "manufacturing_plan_validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_plan():
    evidence = [
        {"id": f"E-{kind}", "type": kind, "status": "pass", "artifact": f"{kind}.json", "source_hash": "a" * 64}
        for kind in MODULE.REQUIRED_EVIDENCE
    ]
    return {
        "schema_version": "1.1",
        "record_state": "controlled_evidence",
        "product": {
            "part_number": "PLT-001", "revision": "A", "configuration_id": "BASE",
            "maturity": "production_candidate", "batch_quantity": 100, "annual_quantity": 1200,
            "units": "mm", "currency": "USD", "cost_basis_date": "2026-07-24",
            "source_geometry_hash": "b" * 64, "acceptance_authority_role": "manufacturing authority",
        },
        "requirements": [
            {"id": "REQ-1", "source": "drawing-PLT-001-A.pdf", "revision": "A", "requirement": "6061-T6, grain along X", "verification": "material cert and nest review"}
        ],
        "materials": [
            {
                "id": "MAT-1", "material_spec": "6061-T6 per ASTM B209", "stock_form": "sheet",
                "stock_size": "1525 x 3050 x 6 mm", "supplier_basis": "quote Q-1",
                "purchased_quantity": 2, "purchased_mass_kg": 150, "finished_mass_kg": 100,
                "recoverable_remnant_kg": 20, "recyclable_scrap_kg": 25,
                "unrecoverable_process_loss_kg": 5, "mass_source": "CAD plus scale trial",
                "mass_uncertainty_kg": 1, "unit_stock_cost": 500, "scrap_remnant_credit": 100,
                "currency": "USD", "reuse_disposition": "remnant inventory and segregated recycling",
                "remnant_record": {
                    "id": "REM-1", "dimensions": "500 x 700 x 6 mm", "lot_heat_link": "HEAT-1",
                    "location": "rack A3", "condition": "protected", "future_use_rule": "match same spec and grain",
                },
            }
        ],
        "layout_plans": [
            {
                "id": "NEST-1", "type": "sheet_nest", "material_id": "MAT-1",
                "stock_count": 2, "stock_usable_measure": 1000, "net_part_measure": 1400,
                "kerf_support_loss_measure": 100, "remnant_measure": 400,
                "other_waste_measure": 100, "measure_unit": "arbitrary normalized area",
                "constraints": {
                    "kerf": "0.2 mm", "edge_margin": "10 mm", "spacing": "5 mm",
                    "orientation_rule": "0/180 degrees; grain X", "clamp_or_drop_rule": "25 mm clamp zone",
                },
                "artifact": "nest-1.dxf", "algorithm_version": "Nester 4.2 seed 10",
                "verified_status": "pass", "verification_evidence": "nest-review.pdf",
                "planned_input_quantity": 105, "finished_mass_kg": 100,
            }
        ],
        "operations": [
            {
                "id": "OP-10", "sequence": 10, "predecessor_ids": [], "input_state": "sheet",
                "output_state": "cut blanks", "work_center": "laser-1", "setup_fixture_tooling": "sheet fixture",
                "input_quantity": 105, "good_output_quantity": 100, "scrap_quantity": 5,
                "rework_quantity": 2, "machine_setup_minutes": 30, "labor_setup_minutes": 20,
                "machine_cycle_minutes_per_input": 2,
                "labor_minutes_per_input": 0.5, "inspection_minutes_per_batch": 30,
                "rework_minutes_per_unit": 5, "machine_rate_per_hour": 120,
                "labor_rate_per_hour": 45, "tooling_consumables_cost": 50,
                "outside_process_cost": 0, "evidence": "laser-trial.csv",
                "inspection_plan": "IP-PLT-001", "accepted_output": True,
            }
        ],
        "packaging": [
            {
                "id": "PKG-1", "level": "batch", "quantity": 1, "material": "returnable tote",
                "protection_requirements": "separators protect cosmetic faces",
                "reuse_or_disposal": "return loop", "unit_cost": 20, "currency": "USD",
                "evidence": "packaging-review.pdf",
            }
        ],
        "alternatives": [
            {
                "id": "ALT-4X8", "route_description": "4x8 sheet laser",
                "fixed_cost": 1000, "variable_cost_per_accepted_unit": 18,
                "minimum_order_quantity": 1, "lead_time_days": 10,
                "capacity_units_per_year": 5000, "quality_risk": "low",
                "supply_risk": "dual source", "basis_evidence": "alt-4x8.xlsx",
            },
            {
                "id": "ALT-5X10", "route_description": "5x10 sheet laser",
                "fixed_cost": 1400, "variable_cost_per_accepted_unit": 16,
                "minimum_order_quantity": 1, "lead_time_days": 12,
                "capacity_units_per_year": 6000, "quality_risk": "low",
                "supply_risk": "single local source", "basis_evidence": "alt-5x10.xlsx",
            },
        ],
        "no_alternative_justification": None,
        "sensitivities": [
            {
                "parameter": "material price", "low": 0.8, "base": 1.0, "high": 1.3,
                "unit": "price multiplier", "affected_alternative_ids": ["ALT-4X8", "ALT-5X10"],
                "result_artifact": "sensitivity.json",
            }
        ],
        "release_evidence": evidence,
        "approvals": [
            {
                "approver": "M. Engineer", "role": "manufacturing authority",
                "date": "2026-07-24", "scope": "PLT-001 revision A plan",
                "configuration_id": "BASE", "decision": "approved",
            }
        ],
    }


def expect(data, verdict, phrase=None):
    report = MODULE.validate(data)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in item for item in report["errors"]), report
    return report


base = valid_plan()
report = expect(base, "PASS")
assert report["metrics"]["material_utilization"] == round(100 / 150, 6)
assert report["metrics"]["batch_cost"] > 0
assert report["metrics"]["accepted_batch_quantity"] == 100

case = copy.deepcopy(base)
case["materials"][0]["finished_mass_kg"] = 101
expect(case, "FAIL", "mass balance")

case = copy.deepcopy(base)
case["materials"][0]["remnant_record"] = None
expect(case, "FAIL", "requires remnant_record")

case = copy.deepcopy(base)
case["layout_plans"][0]["net_part_measure"] = 1401
expect(case, "FAIL", "usable-measure balance")

case = copy.deepcopy(base)
case["layout_plans"][0]["verified_status"] = "planned"
expect(case, "FAIL", "verified_status=pass")

case = copy.deepcopy(base)
case["operations"][0]["good_output_quantity"] = 99
expect(case, "FAIL", "quantity balance")

case = copy.deepcopy(base)
case["operations"][0]["accepted_output"] = False
expect(case, "FAIL", "accepted_output")

case = copy.deepcopy(base)
case["layout_plans"][0]["planned_input_quantity"] = 104
expect(case, "FAIL", "root operation input")

case = copy.deepcopy(base)
case["layout_plans"][0]["finished_mass_kg"] = 99
expect(case, "FAIL", "reconcile")

case = copy.deepcopy(base)
case["operations"][0]["rework_quantity"] = 101
expect(case, "FAIL", "rework quantity exceeds")

case = copy.deepcopy(base)
case["operations"][0]["predecessor_ids"] = ["MISSING"]
expect(case, "FAIL", "known operations")

case = copy.deepcopy(base)
case["operations"].append(copy.deepcopy(case["operations"][0]))
case["operations"][1]["id"] = "OP-20"
case["operations"][1]["sequence"] = 20
case["operations"][0]["predecessor_ids"] = ["OP-20"]
case["operations"][1]["predecessor_ids"] = ["OP-10"]
expect(case, "FAIL", "predecessor cycle")

case = copy.deepcopy(base)
case["materials"][0]["currency"] = "EUR"
expect(case, "FAIL", "differs from product currency")

case = copy.deepcopy(base)
case["alternatives"] = [case["alternatives"][0]]
expect(case, "FAIL", "at least two")

case = copy.deepcopy(base)
case["alternatives"] = [case["alternatives"][0]]
case["sensitivities"] = []
case["no_alternative_justification"] = {
    "reason": "qualified laser route is mandated by material and edge requirements",
    "scope": "PLT-001 revision A, quantity through 1200/year",
    "alternatives_screened": ["machining rejected for cost and capacity", "punching rejected for edge requirement"],
    "approver": "M. Authority", "role": "manufacturing authority",
    "date": "2026-07-24", "configuration_id": "BASE",
    "decision": "approved", "evidence": "route-screening-PLT-001.pdf",
}
expect(case, "PASS")

case = copy.deepcopy(base)
case["alternatives"] = [case["alternatives"][0]]
case["sensitivities"] = []
case["no_alternative_justification"] = {
    "reason": "only route", "scope": "PLT-001", "alternatives_screened": ["machining"],
    "approver": "M. Authority", "role": "manufacturing authority",
    "date": "2026-07-24", "configuration_id": "BASE",
    "decision": "conditional", "evidence": "screening.pdf",
}
expect(case, "FAIL", "decision must be approved")

case = copy.deepcopy(base)
case["sensitivities"][0]["low"] = 2
expect(case, "FAIL", "low <= base <= high")

case = copy.deepcopy(base)
case["release_evidence"][0]["status"] = "conditional"
expect(case, "FAIL", "lacks passing release evidence")

case = copy.deepcopy(base)
case["approvals"] = ["approved"]
expect(case, "FAIL", "approvals[0]")

case = copy.deepcopy(base)
case["approvals"][0]["role"] = "drafter"
expect(case, "FAIL", "acceptance authority")

print("manufacturing/material optimization validator regression tests: PASS")
