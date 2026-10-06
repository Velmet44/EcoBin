#!/usr/bin/env python3
"""Validate declared manufacturing arithmetic, references, and release evidence."""

import argparse
import datetime as dt
import json
import math
import sys
from collections import Counter
from pathlib import Path
import re


MATURITIES = {"concept", "prototype", "production_candidate", "released"}
LAYOUT_TYPES = {"sheet_nest", "plate_nest", "bar_cut", "tube_cut", "additive_build", "other"}
EVIDENCE_TYPES = {
    "source_requirements", "material_balance", "layout_verification", "router",
    "inspection_plan", "cost_report", "packaging_review", "alternative_review",
}
REQUIRED_EVIDENCE = EVIDENCE_TYPES
PLACEHOLDERS = {"", "tbd", "unknown", "unassigned", "n/a", "na", "none", "null", "pending", "yyyy-mm-dd", "?"}
TOLERANCE = 1e-6
HASH = re.compile(r"^[0-9a-fA-F]{64}$")
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}


def present(value):
    return value is not None and (not isinstance(value, str) or value.strip().lower() not in PLACEHOLDERS)


def number(value, minimum=None, strictly=False):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    if minimum is not None and (result <= minimum if strictly else result < minimum):
        return None
    return result


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def objects(data, key, errors):
    value = data.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be a list")
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{key}[{index}] must be an object")
            result.append({})
        else:
            result.append(item)
    return result


def require(item, keys, path, errors):
    for key in keys:
        if not present(item.get(key)):
            errors.append(f"{path}.{key} is required")


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-6, abs_tol=TOLERANCE)


def validate(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["plan root must be an object"], "warnings": [], "metrics": {}}
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    record_state = data.get("record_state")
    if record_state not in RECORD_STATES:
        errors.append(f"record_state must be one of {sorted(RECORD_STATES)}")
    product = data.get("product")
    if not isinstance(product, dict):
        errors.append("product must be an object")
        product = {}
    require(
        product,
        (
            "part_number", "revision", "configuration_id", "maturity", "batch_quantity",
            "annual_quantity", "units", "currency", "cost_basis_date",
            "source_geometry_hash", "acceptance_authority_role",
        ),
        "product", errors,
    )
    if product.get("maturity") not in MATURITIES:
        errors.append(f"product.maturity must be one of {sorted(MATURITIES)}")
    candidate = (
        record_state == "controlled_evidence"
        and product.get("maturity") in {"production_candidate", "released"}
    )
    if present(product.get("source_geometry_hash")) and not HASH.fullmatch(str(product.get("source_geometry_hash"))):
        errors.append("product.source_geometry_hash must be a 64-character SHA-256")
    batch_qty = number(product.get("batch_quantity"), 0, strictly=True)
    annual_qty = number(product.get("annual_quantity"), 0, strictly=True)
    if batch_qty is None:
        errors.append("product.batch_quantity must be positive")
        batch_qty = 0
    if annual_qty is None:
        errors.append("product.annual_quantity must be positive")
    if present(product.get("cost_basis_date")) and not valid_date(product.get("cost_basis_date")):
        errors.append("product.cost_basis_date must be an ISO date")

    requirements = objects(data, "requirements", errors)
    materials = objects(data, "materials", errors)
    layouts = objects(data, "layout_plans", errors)
    operations = objects(data, "operations", errors)
    packaging = objects(data, "packaging", errors)
    alternatives = objects(data, "alternatives", errors)
    sensitivities = objects(data, "sensitivities", errors)
    evidence = objects(data, "release_evidence", errors)
    approvals = objects(data, "approvals", errors)

    requirement_ids = []
    for index, item in enumerate(requirements):
        require(item, ("id", "source", "revision", "requirement", "verification"), f"requirements[{index}]", errors)
        requirement_ids.append(item.get("id"))
    if len(requirement_ids) != len(set(requirement_ids)):
        errors.append("requirement IDs must be unique")
    if candidate and not requirements:
        errors.append("production candidate requires controlled requirements")

    material_ids = []
    purchased_mass_total = finished_mass_total = recoverable_total = disposal_total = 0.0
    material_cost_total = 0.0
    for index, item in enumerate(materials):
        require(
            item,
            (
                "id", "material_spec", "stock_form", "stock_size", "supplier_basis",
                "purchased_quantity", "purchased_mass_kg", "finished_mass_kg",
                "recoverable_remnant_kg", "recyclable_scrap_kg",
                "unrecoverable_process_loss_kg", "mass_source", "mass_uncertainty_kg",
                "unit_stock_cost", "scrap_remnant_credit", "currency", "reuse_disposition",
            ),
            f"materials[{index}]", errors,
        )
        material_ids.append(item.get("id"))
        values = {}
        for key in (
            "purchased_quantity", "purchased_mass_kg", "finished_mass_kg",
            "recoverable_remnant_kg", "recyclable_scrap_kg",
            "unrecoverable_process_loss_kg", "mass_uncertainty_kg",
            "unit_stock_cost", "scrap_remnant_credit",
        ):
            values[key] = number(item.get(key), 0)
            if values[key] is None:
                errors.append(f"materials[{index}].{key} must be non-negative")
                values[key] = 0
        if values["purchased_quantity"] <= 0 or values["purchased_mass_kg"] <= 0:
            errors.append(f"materials[{index}] purchased quantity and mass must be positive")
        outputs = (
            values["finished_mass_kg"] + values["recoverable_remnant_kg"]
            + values["recyclable_scrap_kg"] + values["unrecoverable_process_loss_kg"]
        )
        if not close(values["purchased_mass_kg"], outputs):
            errors.append(f"materials[{index}] mass balance does not close")
        if item.get("currency") != product.get("currency"):
            errors.append(f"materials[{index}].currency differs from product currency")
        if values["recoverable_remnant_kg"] > 0:
            remnant = item.get("remnant_record")
            if not isinstance(remnant, dict):
                errors.append(f"materials[{index}] recoverable remnant requires remnant_record")
            else:
                require(remnant, ("id", "dimensions", "lot_heat_link", "location", "condition", "future_use_rule"), f"materials[{index}].remnant_record", errors)
        purchased_mass_total += values["purchased_mass_kg"]
        finished_mass_total += values["finished_mass_kg"]
        recoverable_total += values["recoverable_remnant_kg"] + values["recyclable_scrap_kg"]
        disposal_total += values["unrecoverable_process_loss_kg"]
        material_cost_total += values["purchased_quantity"] * values["unit_stock_cost"] - values["scrap_remnant_credit"]
    if len(material_ids) != len(set(material_ids)) or any(not present(item) for item in material_ids):
        errors.append("material IDs must be present and unique")
    material_set = set(material_ids)
    if candidate and not materials:
        errors.append("production candidate requires material records")

    layout_ids = []
    for index, item in enumerate(layouts):
        require(
            item,
            (
                "id", "type", "material_id", "stock_count", "stock_usable_measure",
                "net_part_measure", "kerf_support_loss_measure", "remnant_measure",
                "other_waste_measure", "measure_unit", "constraints", "artifact",
                "algorithm_version", "verified_status", "verification_evidence",
                "planned_input_quantity", "finished_mass_kg",
            ),
            f"layout_plans[{index}]", errors,
        )
        layout_ids.append(item.get("id"))
        if item.get("type") not in LAYOUT_TYPES:
            errors.append(f"layout_plans[{index}].type must be one of {sorted(LAYOUT_TYPES)}")
        if item.get("material_id") not in material_set:
            errors.append(f"layout_plans[{index}] references unknown material")
        values = {}
        for key in ("stock_count", "stock_usable_measure", "net_part_measure", "kerf_support_loss_measure", "remnant_measure", "other_waste_measure"):
            values[key] = number(item.get(key), 0)
            if values[key] is None:
                errors.append(f"layout_plans[{index}].{key} must be non-negative")
                values[key] = 0
        available = values["stock_count"] * values["stock_usable_measure"]
        allocated = values["net_part_measure"] + values["kerf_support_loss_measure"] + values["remnant_measure"] + values["other_waste_measure"]
        if not close(available, allocated):
            errors.append(f"layout_plans[{index}] usable-measure balance does not close")
        if candidate and item.get("verified_status") != "pass":
            errors.append(f"layout_plans[{index}] must have verified_status=pass")
        planned_input = number(item.get("planned_input_quantity"), 0, strictly=True)
        layout_finished_mass = number(item.get("finished_mass_kg"), 0)
        if planned_input is None:
            errors.append(f"layout_plans[{index}].planned_input_quantity must be positive")
        material = next((candidate for candidate in materials if candidate.get("id") == item.get("material_id")), None)
        if layout_finished_mass is None:
            errors.append(f"layout_plans[{index}].finished_mass_kg must be non-negative")
        elif material is not None:
            declared = number(material.get("finished_mass_kg"), 0)
            if declared is not None and not close(layout_finished_mass, declared):
                errors.append(f"layout_plans[{index}] finished mass does not reconcile to material balance")
        constraints = item.get("constraints")
        if not isinstance(constraints, dict):
            errors.append(f"layout_plans[{index}].constraints must be an object")
        else:
            require(constraints, ("kerf", "edge_margin", "spacing", "orientation_rule", "clamp_or_drop_rule"), f"layout_plans[{index}].constraints", errors)
    if len(layout_ids) != len(set(layout_ids)):
        errors.append("layout plan IDs must be unique")
    if candidate and not layouts:
        errors.append("production candidate requires an evidenced layout/cut/build plan")

    operation_ids = [item.get("id") for item in operations]
    if len(operation_ids) != len(set(operation_ids)) or any(not present(item) for item in operation_ids):
        errors.append("operation IDs must be present and unique")
    operation_set = set(operation_ids)
    sequences = [item.get("sequence") for item in operations]
    if len(sequences) != len(set(sequences)):
        errors.append("operation sequence values must be unique")
    predecessor_map = {
        item.get("id"): item.get("predecessor_ids") if isinstance(item.get("predecessor_ids"), list) else []
        for item in operations
    }
    colors = {item: 0 for item in operation_set}
    successor_map = {item: [] for item in operation_set}
    for operation_id, predecessors in predecessor_map.items():
        for predecessor in predecessors:
            if predecessor in successor_map:
                successor_map[predecessor].append(operation_id)
    def visit_operation(item):
        if colors.get(item) == 1:
            errors.append(f"operation predecessor cycle detected at {item}")
            return
        if colors.get(item) == 2:
            return
        colors[item] = 1
        for predecessor in predecessor_map.get(item, []):
            if predecessor in colors:
                visit_operation(predecessor)
        colors[item] = 2
    for operation_id in operation_set:
        visit_operation(operation_id)
    operation_cost_total = 0.0
    operation_time_total = 0.0
    operation_metrics = []
    for index, item in enumerate(operations):
        require(
            item,
            (
                "id", "sequence", "predecessor_ids", "input_state", "output_state",
                "work_center", "setup_fixture_tooling", "input_quantity", "good_output_quantity",
                "scrap_quantity", "rework_quantity", "machine_setup_minutes", "labor_setup_minutes",
                "machine_cycle_minutes_per_input", "labor_minutes_per_input",
                "inspection_minutes_per_batch", "rework_minutes_per_unit",
                "machine_rate_per_hour", "labor_rate_per_hour", "tooling_consumables_cost",
                "outside_process_cost", "evidence", "inspection_plan",
            ),
            f"operations[{index}]", errors,
        )
        predecessors = item.get("predecessor_ids")
        if not isinstance(predecessors, list) or set(predecessors) - operation_set:
            errors.append(f"operations[{index}].predecessor_ids must reference known operations")
        if item.get("id") in (predecessors or []):
            errors.append(f"operations[{index}] cannot precede itself")
        values = {}
        for key in (
            "input_quantity", "good_output_quantity", "scrap_quantity", "rework_quantity",
            "machine_setup_minutes", "labor_setup_minutes",
            "machine_cycle_minutes_per_input", "labor_minutes_per_input",
            "inspection_minutes_per_batch", "rework_minutes_per_unit",
            "machine_rate_per_hour", "labor_rate_per_hour", "tooling_consumables_cost",
            "outside_process_cost",
        ):
            values[key] = number(item.get(key), 0)
            if values[key] is None:
                errors.append(f"operations[{index}].{key} must be non-negative")
                values[key] = 0
        if values["input_quantity"] <= 0:
            errors.append(f"operations[{index}].input_quantity must be positive")
        if not close(values["input_quantity"], values["good_output_quantity"] + values["scrap_quantity"]):
            errors.append(f"operations[{index}] quantity balance does not close")
        if values["rework_quantity"] > values["good_output_quantity"]:
            errors.append(f"operations[{index}] rework quantity exceeds good output")
        if candidate and len(predecessors or []) > 1:
            errors.append(f"operations[{index}] multiple predecessors require an explicit split/merge transformation")
        if predecessors and len(predecessors) == 1:
            predecessor = next((op for op in operations if op.get("id") == predecessors[0]), {})
            if item.get("input_state") != predecessor.get("output_state"):
                errors.append(f"operations[{index}] input state does not match predecessor output state")
            predecessor_good = number(predecessor.get("good_output_quantity"), 0)
            if predecessor_good is not None and not close(values["input_quantity"], predecessor_good):
                errors.append(f"operations[{index}] input quantity does not match predecessor good output")
        machine_minutes = values["machine_setup_minutes"] + values["machine_cycle_minutes_per_input"] * values["input_quantity"] + values["rework_minutes_per_unit"] * values["rework_quantity"]
        labor_minutes = values["labor_setup_minutes"] + values["labor_minutes_per_input"] * values["input_quantity"] + values["inspection_minutes_per_batch"] + values["rework_minutes_per_unit"] * values["rework_quantity"]
        cost = (
            machine_minutes / 60 * values["machine_rate_per_hour"]
            + labor_minutes / 60 * values["labor_rate_per_hour"]
            + values["tooling_consumables_cost"] + values["outside_process_cost"]
        )
        operation_cost_total += cost
        operation_time_total += machine_minutes
        operation_metrics.append({
            "id": item.get("id"),
            "first_pass_yield": (values["good_output_quantity"] - values["rework_quantity"]) / values["input_quantity"] if values["input_quantity"] else None,
            "final_yield": values["good_output_quantity"] / values["input_quantity"] if values["input_quantity"] else None,
            "declared_batch_cost": round(cost, 6),
        })
    if candidate and not operations:
        errors.append("production candidate requires a process router")
    terminal_accepted_quantity = 0.0
    if candidate and operations:
        roots = [item for item in operations if not predecessor_map.get(item.get("id"))]
        terminals = [item for item in operations if not successor_map.get(item.get("id"))]
        if len(roots) != 1:
            errors.append("production router must have exactly one root operation")
        if len(terminals) != 1:
            errors.append("production router must have exactly one terminal operation")
        if roots and layouts:
            planned = sum(number(item.get("planned_input_quantity"), 0) or 0 for item in layouts)
            root_input = number(roots[0].get("input_quantity"), 0) or 0
            if not close(planned, root_input):
                errors.append("root operation input quantity does not reconcile to layout plan")
        if terminals:
            terminal = terminals[0]
            if terminal.get("accepted_output") is not True:
                errors.append("terminal operation must declare accepted_output=true")
            terminal_accepted_quantity = number(terminal.get("good_output_quantity"), 0) or 0
            if not close(terminal_accepted_quantity, batch_qty):
                errors.append("terminal accepted quantity must equal product batch quantity")

    packaging_cost = 0.0
    for index, item in enumerate(packaging):
        require(item, ("id", "level", "quantity", "material", "protection_requirements", "reuse_or_disposal", "unit_cost", "currency", "evidence"), f"packaging[{index}]", errors)
        quantity = number(item.get("quantity"), 0, strictly=True)
        unit_cost = number(item.get("unit_cost"), 0)
        if quantity is None:
            errors.append(f"packaging[{index}].quantity must be positive")
            quantity = 0
        if unit_cost is None:
            errors.append(f"packaging[{index}].unit_cost must be non-negative")
            unit_cost = 0
        if item.get("currency") != product.get("currency"):
            errors.append(f"packaging[{index}].currency differs from product currency")
        packaging_cost += quantity * unit_cost
    if candidate and not packaging:
        errors.append("production candidate requires packaging/disposition records")

    alternative_ids = []
    for index, item in enumerate(alternatives):
        require(
            item,
            (
                "id", "route_description", "fixed_cost", "variable_cost_per_accepted_unit",
                "minimum_order_quantity", "lead_time_days", "capacity_units_per_year",
                "quality_risk", "supply_risk", "basis_evidence",
            ),
            f"alternatives[{index}]", errors,
        )
        alternative_ids.append(item.get("id"))
        for key in ("fixed_cost", "variable_cost_per_accepted_unit", "minimum_order_quantity", "lead_time_days", "capacity_units_per_year"):
            if number(item.get(key), 0) is None:
                errors.append(f"alternatives[{index}].{key} must be non-negative")
    if len(alternative_ids) != len(set(alternative_ids)):
        errors.append("alternative IDs must be unique")
    if candidate and len(alternatives) < 2:
        justification = data.get("no_alternative_justification")
        if not isinstance(justification, dict):
            errors.append("production candidate requires at least two route alternatives or a structured approved no-alternative justification")
        else:
            require(
                justification,
                (
                    "reason", "scope", "alternatives_screened", "approver", "role",
                    "date", "configuration_id", "decision", "evidence",
                ),
                "no_alternative_justification",
                errors,
            )
            screened = justification.get("alternatives_screened")
            if not isinstance(screened, list) or not screened or any(not present(item) for item in screened):
                errors.append("no_alternative_justification.alternatives_screened must be a non-empty list")
            if present(justification.get("date")) and not valid_date(justification.get("date")):
                errors.append("no_alternative_justification.date must be an ISO date")
            if justification.get("configuration_id") != product.get("configuration_id"):
                errors.append("no_alternative_justification.configuration_id must match product")
            if justification.get("decision") != "approved":
                errors.append("no_alternative_justification.decision must be approved")

    for index, item in enumerate(sensitivities):
        require(item, ("parameter", "low", "base", "high", "unit", "affected_alternative_ids", "result_artifact"), f"sensitivities[{index}]", errors)
        refs = item.get("affected_alternative_ids")
        if not isinstance(refs, list) or not refs or set(refs) - set(alternative_ids):
            errors.append(f"sensitivities[{index}].affected_alternative_ids must be valid")
        low, base, high = number(item.get("low")), number(item.get("base")), number(item.get("high"))
        if None in {low, base, high} or not low <= base <= high:
            errors.append(f"sensitivities[{index}] requires low <= base <= high")
    if candidate and not sensitivities and len(alternatives) >= 2:
        errors.append("production candidate requires sensitivity evidence")

    passed_evidence = set()
    for index, item in enumerate(evidence):
        require(item, ("id", "type", "status", "artifact", "source_hash"), f"release_evidence[{index}]", errors)
        if present(item.get("source_hash")) and not HASH.fullmatch(str(item.get("source_hash"))):
            errors.append(f"release_evidence[{index}].source_hash must be a 64-character SHA-256")
        if item.get("type") not in EVIDENCE_TYPES:
            errors.append(f"release_evidence[{index}].type must be one of {sorted(EVIDENCE_TYPES)}")
        if item.get("status") not in {"pass", "fail", "conditional"}:
            errors.append(f"release_evidence[{index}].status is invalid")
        elif item.get("status") == "pass":
            passed_evidence.add(item.get("type"))
    if candidate:
        missing = sorted(REQUIRED_EVIDENCE - passed_evidence)
        if missing:
            errors.append(f"production candidate lacks passing release evidence: {missing}")

    for index, item in enumerate(approvals):
        require(item, ("approver", "role", "date", "scope", "configuration_id", "decision"), f"approvals[{index}]", errors)
        if present(item.get("date")) and not valid_date(item.get("date")):
            errors.append(f"approvals[{index}].date must be an ISO date")
        if item.get("decision") not in {"approved", "rejected", "conditional"}:
            errors.append(f"approvals[{index}].decision is invalid")
        if item.get("configuration_id") != product.get("configuration_id"):
            errors.append(f"approvals[{index}] configuration does not match product")
    if candidate and not any(
        item.get("decision") == "approved"
        and item.get("role") == product.get("acceptance_authority_role")
        and item.get("configuration_id") == product.get("configuration_id")
        for item in approvals
    ):
        errors.append("production candidate requires approval by the configured acceptance authority")

    batch_cost = material_cost_total + operation_cost_total + packaging_cost
    return {
        "verdict": "FAIL" if errors else (
            "RELEASED" if candidate and product.get("maturity") == "released"
            else "PASS" if candidate else "DRAFT"
        ),
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "purchased_mass_kg": round(purchased_mass_total, 6),
            "finished_mass_kg": round(finished_mass_total, 6),
            "material_utilization": round(finished_mass_total / purchased_mass_total, 6) if purchased_mass_total else None,
            "buy_to_finished_ratio": round(purchased_mass_total / finished_mass_total, 6) if finished_mass_total else None,
            "recoverable_fraction": round(recoverable_total / purchased_mass_total, 6) if purchased_mass_total else None,
            "disposal_fraction": round(disposal_total / purchased_mass_total, 6) if purchased_mass_total else None,
            "batch_machine_minutes": round(operation_time_total, 6),
            "batch_cost": round(batch_cost, 6),
            "accepted_batch_quantity": terminal_accepted_quantity if candidate else None,
            "cost_per_accepted_unit": round(batch_cost / terminal_accepted_quantity, 6) if terminal_accepted_quantity else None,
            "currency": product.get("currency"),
            "operations": operation_metrics,
        },
        "limitations": [
            "Declared arithmetic and references only; layout geometry, FreeCAD/CAM, machine, supplier, quote, inventory, and hardware were not verified.",
            "Environmental fractions are material-flow diagnostics, not a life-cycle assessment or certification.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"verdict": "FAIL", "errors": [str(exc)]}, indent=2))
        return 2
    report = validate(data)
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.report:
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["verdict"] in {"PASS", "RELEASED"} else 1


if __name__ == "__main__":
    sys.exit(main())
