#!/usr/bin/env python3
"""Validate an engineering-analysis evidence contract.

This validates records and cross-references. It does not run a solver, judge
physical fidelity, certify a design, or authorize release.
"""

import argparse
import datetime as dt
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

from validation_common import present


ANALYSIS_TYPES = {
    "analytical", "static", "thermal", "thermomechanical", "modal", "buckling",
    "fatigue", "harmonic", "transient", "random_vibration", "coupled",
    "optimization_confirmation", "other",
}
CLASSIFICATIONS = {"service", "proof", "ultimate", "fatigue", "fault", "abuse", "transport", "assembly", "maintenance", "other"}
CASE_VERDICTS = {"PASS", "CONDITIONAL", "FAIL"}
DOC_STATUSES = {"draft", "in_review", "approved", "superseded"}
REVIEW_STATUSES = {"pending", "pass", "fail"}
RELEASE_DECISIONS = {"not_requested", "withheld", "approved_by_authority"}
ACTION_SEVERITIES = {"blocker", "major", "minor", "opportunity"}
ACTION_STATUSES = {"open", "closed", "waived"}
VALIDATION_STATUSES = {"not_required", "planned", "in_progress", "pass", "fail", "waived_with_justification"}
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
DEFAULT_MAX_REACTION_BALANCE_LIMIT_PERCENT = 2.0
DEFAULT_MAX_ANALYTICAL_COMPARISON_ACCEPTANCE_PERCENT = 20.0
DEFAULT_MAX_CONVERGENCE_ACCEPTANCE_PERCENT = 5.0
TYPE_SPECIFIC_VERIFICATION = {
    "modal": (
        "frequency_range",
        "mode_count",
        "effective_mass_participation",
        "rigid_body_mode_disposition",
    ),
    "harmonic": (
        "frequency_range",
        "frequency_step_sensitivity",
        "damping_source",
        "response_quantity",
    ),
    "random_vibration": (
        "psd_definition",
        "frequency_range",
        "damping_source",
        "statistical_basis",
        "integration_check",
    ),
    "transient": (
        "time_history_source",
        "time_step_sensitivity",
        "integrator",
        "energy_or_momentum_check",
    ),
    "fatigue": (
        "load_spectrum",
        "cycle_counting_method",
        "material_curve_source",
        "mean_stress_method",
        "scatter_or_reliability_basis",
    ),
    "buckling": (
        "imperfection_basis",
        "eigenvalue_or_nonlinear_method",
        "load_factor_interpretation",
    ),
}


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def object_list(data, key, errors):
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


def require_fields(obj, fields, prefix, errors):
    for field in fields:
        if not present(obj.get(field)):
            errors.append(f"{prefix}.{field} is required and must be controlled")


def unique_ids(items, prefix, errors):
    values = [item.get("id") for item in items]
    if any(not present(value) for value in values):
        errors.append(f"{prefix} IDs must be present")
    duplicates = sorted(str(value) for value, count in Counter(values).items() if value is not None and count > 1)
    if duplicates:
        errors.append(f"{prefix} IDs must be unique; duplicates={duplicates}")
    return {value for value in values if present(value)}


def evaluate(actual, operator, limit):
    operations = {
        "<=": lambda a, b: a <= b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        ">": lambda a, b: a > b,
        "==": lambda a, b: a == b,
    }
    return operations[operator](actual, limit)


def approved_exception(verification, key, prefix, errors):
    """Require a dated, named approval for a looser-than-default limit."""
    exceptions = verification.get("acceptance_limit_justifications")
    item = exceptions.get(key) if isinstance(exceptions, dict) else None
    if not isinstance(item, dict):
        errors.append(
            f"{prefix}.verification.acceptance_limit_justifications.{key} "
            "is required when the acceptance limit exceeds the default ceiling"
        )
        return False
    require_fields(
        item,
        ("justification", "approved_by", "approval_date"),
        f"{prefix}.verification.acceptance_limit_justifications.{key}",
        errors,
    )
    if present(item.get("approval_date")) and not valid_date(item.get("approval_date")):
        errors.append(
            f"{prefix}.verification.acceptance_limit_justifications.{key}."
            "approval_date must be ISO YYYY-MM-DD"
        )
        return False
    return all(present(item.get(field)) for field in ("justification", "approved_by", "approval_date"))


def validate_convergence_levels(levels, prefix, errors):
    """Validate one convergence study and return (quantity, valid, values)."""
    verification_ok = True
    if not isinstance(levels, list) or len(levels) < 3:
        errors.append(f"{prefix} requires at least three levels")
        return None, False, []
    quantities = set()
    result_units = set()
    sizes = []
    dofs = []
    values = []
    for level_index, level in enumerate(levels):
        if not isinstance(level, dict):
            errors.append(f"{prefix}[{level_index}] must be an object")
            verification_ok = False
            continue
        require_fields(
            level,
            ("level", "characteristic_size", "size_unit", "degrees_of_freedom", "quantity", "value", "unit"),
            f"{prefix}[{level_index}]",
            errors,
        )
        quantities.add(level.get("quantity"))
        result_units.add(level.get("unit"))
        sizes.append(level.get("characteristic_size"))
        dofs.append(level.get("degrees_of_freedom"))
        values.append(level.get("value"))
    if len(quantities) != 1 or len(result_units) != 1:
        errors.append(f"{prefix} levels must use one quantity and result unit")
        verification_ok = False
    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in sizes + dofs + values):
        errors.append(f"{prefix} size, DOF, and value fields must be finite numeric")
        verification_ok = False
    else:
        if not all(a > b > 0 for a, b in zip(sizes, sizes[1:])):
            errors.append(f"{prefix} characteristic size must decrease monotonically")
            verification_ok = False
        if not all(a < b for a, b in zip(dofs, dofs[1:])):
            errors.append(f"{prefix} DOF must increase monotonically")
            verification_ok = False
    quantity = next(iter(quantities)) if len(quantities) == 1 else None
    return quantity, verification_ok, values


def validate(data):
    errors = []
    warnings = []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["contract root must be an object"], "warnings": []}
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")

    document = data.get("document") if isinstance(data.get("document"), dict) else {}
    product = data.get("product") if isinstance(data.get("product"), dict) else {}
    units = data.get("units") if isinstance(data.get("units"), dict) else {}
    if not document:
        errors.append("document must be an object")
    if not product:
        errors.append("product must be an object")
    require_fields(document, ("analysis_id", "revision", "title", "status", "author", "independent_reviewer", "date"), "document", errors)
    if document.get("status") not in DOC_STATUSES:
        errors.append(f"document.status must be one of {sorted(DOC_STATUSES)}")
    if present(document.get("date")) and not valid_date(document.get("date")):
        errors.append("document.date must be ISO YYYY-MM-DD")
    require_fields(product, ("part_number", "revision", "configuration", "authoritative_model", "geometry_sha256", "coordinate_system", "consequence"), "product", errors)
    if present(product.get("geometry_sha256")) and not SHA256.fullmatch(str(product.get("geometry_sha256"))):
        errors.append("product.geometry_sha256 must contain 64 hexadecimal characters")
    for field in ("length", "force", "mass", "time", "temperature", "stress", "energy"):
        if not present(units.get(field)):
            errors.append(f"units.{field} is required")

    requirements = object_list(data, "requirements", errors)
    idealizations = object_list(data, "geometry_idealizations", errors)
    materials = object_list(data, "materials", errors)
    load_cases = object_list(data, "load_cases", errors)
    bcs = object_list(data, "boundary_conditions", errors)
    cases = object_list(data, "analysis_cases", errors)
    actions = object_list(data, "open_actions", errors)
    for key, values in (
        ("requirements", requirements),
        ("materials", materials),
        ("load_cases", load_cases),
        ("boundary_conditions", bcs),
        ("analysis_cases", cases),
    ):
        if not values:
            errors.append(f"{key} must contain at least one controlled record")
    req_ids = unique_ids(requirements, "requirements", errors)
    idealization_ids = unique_ids(idealizations, "geometry_idealizations", errors)
    material_ids = unique_ids(materials, "materials", errors)
    load_ids = unique_ids(load_cases, "load_cases", errors)
    bc_ids = unique_ids(bcs, "boundary_conditions", errors)
    unique_ids(cases, "analysis_cases", errors)
    unique_ids(actions, "open_actions", errors)

    req_by_id = {}
    for index, requirement in enumerate(requirements):
        require_fields(requirement, ("id", "description", "source", "acceptance"), f"requirements[{index}]", errors)
        acceptance = requirement.get("acceptance")
        if isinstance(acceptance, dict):
            require_fields(acceptance, ("quantity", "operator", "limit", "unit"), f"requirements[{index}].acceptance", errors)
            if acceptance.get("operator") not in {"<=", "<", ">=", ">", "=="}:
                errors.append(f"requirements[{index}].acceptance.operator is invalid")
            if not isinstance(acceptance.get("limit"), (int, float)) or not math.isfinite(acceptance.get("limit", math.nan)):
                errors.append(f"requirements[{index}].acceptance.limit must be finite numeric")
        else:
            errors.append(f"requirements[{index}].acceptance must be an object")
        req_by_id[requirement.get("id")] = requirement

    for index, item in enumerate(idealizations):
        require_fields(item, ("id", "change", "justification", "preserved_properties", "check"), f"geometry_idealizations[{index}]", errors)
        if not isinstance(item.get("preserved_properties"), list) or not item.get("preserved_properties"):
            errors.append(f"geometry_idealizations[{index}].preserved_properties must be a non-empty list")

    for index, material in enumerate(materials):
        require_fields(material, ("id", "regions", "specification", "product_form_condition", "orientation", "property_source"), f"materials[{index}]", errors)
        if not isinstance(material.get("regions"), list) or not material.get("regions"):
            errors.append(f"materials[{index}].regions must be a non-empty list")
        for group in ("properties", "allowables"):
            entries = material.get(group)
            if not isinstance(entries, list) or not entries:
                errors.append(f"materials[{index}].{group} must be a non-empty list")
                continue
            for entry_index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    errors.append(f"materials[{index}].{group}[{entry_index}] must be an object")
                    continue
                require_fields(entry, ("name", "value", "unit", "temperature", "temperature_unit"), f"materials[{index}].{group}[{entry_index}]", errors)
                if group == "allowables" and not present(entry.get("basis")):
                    errors.append(f"materials[{index}].allowables[{entry_index}].basis is required")
                if not isinstance(entry.get("value"), (int, float)) or entry.get("value", 0) <= 0:
                    errors.append(f"materials[{index}].{group}[{entry_index}].value must be positive numeric")

    for index, bc in enumerate(bcs):
        require_fields(bc, ("id", "type", "region", "physical_basis", "sensitivity"), f"boundary_conditions[{index}]", errors)

    for index, load_case in enumerate(load_cases):
        require_fields(load_case, ("id", "configuration", "event", "classification", "duty", "loads", "boundary_condition_ids", "environment", "requirement_ids", "combination_rule"), f"load_cases[{index}]", errors)
        if load_case.get("classification") not in CLASSIFICATIONS:
            errors.append(f"load_cases[{index}].classification must be one of {sorted(CLASSIFICATIONS)}")
        loads = load_case.get("loads")
        if not isinstance(loads, list) or not loads:
            errors.append(f"load_cases[{index}].loads must be a non-empty list")
        else:
            for load_index, load in enumerate(loads):
                if not isinstance(load, dict):
                    errors.append(f"load_cases[{index}].loads[{load_index}] must be an object")
                    continue
                require_fields(load, ("type", "value", "unit", "application", "source"), f"load_cases[{index}].loads[{load_index}]", errors)
        for key, known in (("boundary_condition_ids", bc_ids), ("requirement_ids", req_ids)):
            refs = load_case.get(key)
            if not isinstance(refs, list) or not refs:
                errors.append(f"load_cases[{index}].{key} must be a non-empty list")
            elif set(refs) - known:
                errors.append(f"load_cases[{index}].{key} contains unknown IDs {sorted(set(refs) - known)}")
        environment = load_case.get("environment")
        if not isinstance(environment, dict) or not present(environment.get("temperature")) or not present(environment.get("temperature_unit")):
            errors.append(f"load_cases[{index}].environment requires temperature and temperature_unit")

    any_case_fail = False
    any_case_conditional = False
    release_case_verdicts = []
    globally_covered_requirements = set()
    for index, case in enumerate(cases):
        prefix = f"analysis_cases[{index}]"
        require_fields(case, ("id", "analysis_type", "release_driving", "solver", "load_case_ids", "material_ids", "idealization_ids", "boundary_condition_ids", "element_formulation", "mesh", "verification", "results", "verdict"), prefix, errors)
        if case.get("analysis_type") not in ANALYSIS_TYPES:
            errors.append(f"{prefix}.analysis_type must be one of {sorted(ANALYSIS_TYPES)}")
        if not isinstance(case.get("release_driving"), bool):
            errors.append(f"{prefix}.release_driving must be boolean")
        if case.get("verdict") not in CASE_VERDICTS:
            errors.append(f"{prefix}.verdict must be one of {sorted(CASE_VERDICTS)}")
        any_case_fail |= case.get("verdict") == "FAIL"
        any_case_conditional |= case.get("verdict") == "CONDITIONAL"
        if case.get("release_driving") is True:
            release_case_verdicts.append(case.get("verdict"))
        solver = case.get("solver")
        if isinstance(solver, dict):
            require_fields(solver, ("name", "version", "interface"), f"{prefix}.solver", errors)
        else:
            errors.append(f"{prefix}.solver must be an object")
        for key, known, allow_empty in (
            ("load_case_ids", load_ids, False),
            ("material_ids", material_ids, False),
            ("idealization_ids", idealization_ids, True),
            ("boundary_condition_ids", bc_ids, False),
        ):
            refs = case.get(key)
            if not isinstance(refs, list) or (not refs and not allow_empty):
                errors.append(f"{prefix}.{key} must be {'a list' if allow_empty else 'a non-empty list'}")
            elif set(refs) - known:
                errors.append(f"{prefix}.{key} contains unknown IDs {sorted(set(refs) - known)}")
        mesh = case.get("mesh")
        if isinstance(mesh, dict):
            require_fields(mesh, ("mesher", "quality_evidence", "result_extraction"), f"{prefix}.mesh", errors)
        else:
            errors.append(f"{prefix}.mesh must be an object")

        verification = case.get("verification")
        verification_ok = True
        if not isinstance(verification, dict):
            errors.append(f"{prefix}.verification must be an object")
            verification = {}
            verification_ok = False
        require_fields(verification, ("solver_log", "warnings_disposition", "reaction_balance_percent", "reaction_balance_limit_percent", "energy_balance", "analytical_comparison", "mesh_convergence", "convergence_acceptance_percent", "singularities"), f"{prefix}.verification", errors)
        type_specific_fields = TYPE_SPECIFIC_VERIFICATION.get(case.get("analysis_type"))
        if type_specific_fields:
            type_specific = verification.get("type_specific")
            if not isinstance(type_specific, dict):
                errors.append(
                    f"{prefix}.verification.type_specific must be an object "
                    f"for {case.get('analysis_type')} analysis"
                )
                verification_ok = False
            else:
                require_fields(
                    type_specific,
                    type_specific_fields,
                    f"{prefix}.verification.type_specific",
                    errors,
                )
        balance = verification.get("reaction_balance_percent")
        balance_limit = verification.get("reaction_balance_limit_percent")
        if not all(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0 for value in (balance, balance_limit)):
            errors.append(f"{prefix}.verification reaction balance values must be finite non-negative numbers")
            verification_ok = False
        elif balance > balance_limit:
            errors.append(f"{prefix} reaction balance {balance}% exceeds {balance_limit}%")
            verification_ok = False
        elif balance_limit > DEFAULT_MAX_REACTION_BALANCE_LIMIT_PERCENT:
            if not approved_exception(verification, "reaction_balance", prefix, errors):
                verification_ok = False
        energy = verification.get("energy_balance")
        if not isinstance(energy, dict) or energy.get("status") != "pass" or not present(energy.get("evidence")):
            errors.append(f"{prefix}.verification.energy_balance requires pass status and evidence")
            verification_ok = False
        comparison = verification.get("analytical_comparison")
        if not isinstance(comparison, dict):
            errors.append(f"{prefix}.verification.analytical_comparison must be an object")
            verification_ok = False
        else:
            require_fields(comparison, ("method", "discrepancy_percent", "acceptance_percent", "evidence"), f"{prefix}.verification.analytical_comparison", errors)
            discrepancy = comparison.get("discrepancy_percent")
            acceptance = comparison.get("acceptance_percent")
            if not all(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0 for value in (discrepancy, acceptance)):
                errors.append(f"{prefix}.verification analytical comparison values must be finite non-negative numbers")
                verification_ok = False
            elif discrepancy > acceptance:
                errors.append(f"{prefix} analytical discrepancy {discrepancy}% exceeds {acceptance}%")
                verification_ok = False
            elif acceptance > DEFAULT_MAX_ANALYTICAL_COMPARISON_ACCEPTANCE_PERCENT:
                if not approved_exception(verification, "analytical_comparison", prefix, errors):
                    verification_ok = False
        convergence = verification.get("mesh_convergence")
        convergence_limit = verification.get("convergence_acceptance_percent")
        if not isinstance(convergence_limit, (int, float)) or not math.isfinite(convergence_limit) or convergence_limit <= 0:
            errors.append(f"{prefix}.verification.convergence_acceptance_percent must be positive finite numeric")
            verification_ok = False
        elif convergence_limit > DEFAULT_MAX_CONVERGENCE_ACCEPTANCE_PERCENT:
            if not approved_exception(verification, "mesh_convergence", prefix, errors):
                verification_ok = False
        converged_quantities = set()
        if not isinstance(convergence, list) or not convergence:
            errors.append(f"{prefix}.verification.mesh_convergence must be a non-empty list")
            verification_ok = False
        else:
            flat_study = all(isinstance(item, dict) and "level" in item for item in convergence)
            structured_studies = all(isinstance(item, dict) and "levels" in item for item in convergence)
            if flat_study:
                studies = [{"levels": convergence}]
            else:
                studies = convergence
            for study_index, study in enumerate(studies):
                study_prefix = f"{prefix}.verification.mesh_convergence"
                if structured_studies:
                    study_prefix += f"[{study_index}].levels"
                if not isinstance(study, dict) or not isinstance(study.get("levels"), list):
                    errors.append(f"{prefix}.verification.mesh_convergence[{study_index}] must contain a levels list")
                    verification_ok = False
                    continue
                quantity, study_ok, values = validate_convergence_levels(study["levels"], study_prefix, errors)
                verification_ok &= study_ok
                declared_quantity = study.get("quantity")
                if declared_quantity is not None and declared_quantity != quantity:
                    errors.append(f"{study_prefix} quantity does not match its study quantity")
                    verification_ok = False
                if quantity and study_ok and isinstance(convergence_limit, (int, float)) and convergence_limit > 0:
                    final_change = abs(values[-1] - values[-2]) / max(abs(values[-1]), 1e-12) * 100
                    if final_change > convergence_limit:
                        errors.append(f"{study_prefix} final mesh change {final_change:.3g}% exceeds {convergence_limit}%")
                        verification_ok = False
                    else:
                        converged_quantities.add(quantity)
        singularities = verification.get("singularities")
        if not isinstance(singularities, list):
            errors.append(f"{prefix}.verification.singularities must be a list")
            verification_ok = False
        else:
            for singularity_index, singularity in enumerate(singularities):
                if not isinstance(singularity, dict):
                    errors.append(f"{prefix}.verification.singularities[{singularity_index}] must be an object")
                    verification_ok = False
                else:
                    require_fields(singularity, ("location", "disposition"), f"{prefix}.verification.singularities[{singularity_index}]", errors)

        results = case.get("results")
        criteria_ok = True
        covered = set()
        result_quantities = set()
        if not isinstance(results, list) or not results:
            errors.append(f"{prefix}.results must be a non-empty list")
            criteria_ok = False
        else:
            for result_index, result in enumerate(results):
                if not isinstance(result, dict):
                    errors.append(f"{prefix}.results[{result_index}] must be an object")
                    criteria_ok = False
                    continue
                require_fields(result, ("requirement_id", "quantity", "value", "unit", "criterion_met", "evidence"), f"{prefix}.results[{result_index}]", errors)
                requirement = req_by_id.get(result.get("requirement_id"))
                if requirement is None:
                    errors.append(f"{prefix}.results[{result_index}] references unknown requirement")
                    criteria_ok = False
                    continue
                covered.add(result.get("requirement_id"))
                globally_covered_requirements.add(result.get("requirement_id"))
                if present(result.get("quantity")):
                    result_quantities.add(result.get("quantity"))
                acceptance = requirement.get("acceptance", {})
                if result.get("quantity") != acceptance.get("quantity") or result.get("unit") != acceptance.get("unit"):
                    errors.append(f"{prefix}.results[{result_index}] quantity/unit does not match requirement")
                    criteria_ok = False
                value = result.get("value")
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    errors.append(f"{prefix}.results[{result_index}].value must be finite numeric")
                    criteria_ok = False
                elif acceptance.get("operator") in {"<=", "<", ">=", ">", "=="} and isinstance(acceptance.get("limit"), (int, float)):
                    calculated = evaluate(value, acceptance.get("operator"), acceptance.get("limit"))
                    if result.get("criterion_met") is not calculated:
                        errors.append(f"{prefix}.results[{result_index}].criterion_met disagrees with requirement calculation")
                        criteria_ok = False
                    if not calculated:
                        criteria_ok = False
            required_for_case = set()
            for load_id in case.get("load_case_ids", []):
                load_case = next((item for item in load_cases if item.get("id") == load_id), {})
                required_for_case.update(load_case.get("requirement_ids", []))
            if required_for_case - covered:
                errors.append(f"{prefix}.results missing requirements {sorted(required_for_case - covered)}")
                criteria_ok = False
        if case.get("release_driving"):
            missing_convergence = sorted(result_quantities - converged_quantities)
            unrelated_convergence = sorted(converged_quantities - result_quantities)
            if missing_convergence:
                errors.append(
                    f"{prefix} release-driving result quantities lack converged mesh evidence: "
                    f"{missing_convergence}"
                )
                verification_ok = False
            if unrelated_convergence:
                errors.append(
                    f"{prefix} mesh convergence quantities are not bound to a release-driving "
                    f"result/requirement: {unrelated_convergence}"
                )
                verification_ok = False

        if case.get("release_driving") and case.get("verdict") == "PASS" and (not verification_ok or not criteria_ok):
            errors.append(f"{prefix} cannot be PASS with incomplete verification or unmet criteria")
        if case.get("verdict") == "PASS" and not criteria_ok:
            errors.append(f"{prefix} PASS is inconsistent with result criteria")

    requirements_without_loads = sorted(
        req_ids
        - {
            requirement_id
            for load_case in load_cases
            for requirement_id in load_case.get("requirement_ids", [])
        }
    )
    if requirements_without_loads:
        errors.append(
            "requirements are not assigned to any load case: "
            f"{requirements_without_loads}"
        )
    requirements_without_results = sorted(req_ids - globally_covered_requirements)
    if requirements_without_results:
        errors.append(
            "requirements have no analysis result coverage: "
            f"{requirements_without_results}"
        )

    validation = data.get("validation")
    validation_status = None
    if not isinstance(validation, dict):
        errors.append("validation must be an object")
    else:
        validation_status = validation.get("status")
        if validation_status not in VALIDATION_STATUSES:
            errors.append(f"validation.status must be one of {sorted(VALIDATION_STATUSES)}")
        if validation_status in {"planned", "in_progress", "pass", "waived_with_justification"}:
            evidence = validation.get("evidence")
            if not isinstance(evidence, list) or not evidence or not all(present(value) for value in evidence):
                errors.append("validation.evidence must be a non-empty controlled list")
        if validation_status in {"not_required", "waived_with_justification"}:
            require_fields(
                validation,
                ("rationale", "scope", "approved_by", "approval_date"),
                "validation",
                errors,
            )
            if present(validation.get("approval_date")) and not valid_date(
                validation.get("approval_date")
            ):
                errors.append("validation.approval_date must be ISO YYYY-MM-DD")

    critical_open = False
    for index, action in enumerate(actions):
        require_fields(action, ("id", "severity", "description", "owner", "status"), f"open_actions[{index}]", errors)
        if action.get("severity") not in ACTION_SEVERITIES:
            errors.append(f"open_actions[{index}].severity must be one of {sorted(ACTION_SEVERITIES)}")
        if action.get("status") not in ACTION_STATUSES:
            errors.append(f"open_actions[{index}].status must be one of {sorted(ACTION_STATUSES)}")
        if action.get("status") == "waived":
            require_fields(
                action,
                ("waiver_rationale", "waiver_scope", "waived_by", "waiver_date"),
                f"open_actions[{index}]",
                errors,
            )
            if present(action.get("waiver_date")) and not valid_date(
                action.get("waiver_date")
            ):
                errors.append(
                    f"open_actions[{index}].waiver_date must be ISO YYYY-MM-DD"
                )
        critical_open |= action.get("severity") in {"blocker", "major"} and action.get("status") == "open"

    approval = data.get("approval")
    if not isinstance(approval, dict):
        errors.append("approval must be an object")
        approval = {}
    require_fields(approval, ("analysis_verdict", "independent_review", "release_decision", "authority", "residual_risks"), "approval", errors)
    if approval.get("analysis_verdict") not in CASE_VERDICTS:
        errors.append(f"approval.analysis_verdict must be one of {sorted(CASE_VERDICTS)}")
    if approval.get("independent_review") not in REVIEW_STATUSES:
        errors.append(f"approval.independent_review must be one of {sorted(REVIEW_STATUSES)}")
    if approval.get("release_decision") not in RELEASE_DECISIONS:
        errors.append(f"approval.release_decision must be one of {sorted(RELEASE_DECISIONS)}")
    if not isinstance(approval.get("residual_risks"), list):
        errors.append("approval.residual_risks must be a list")
    if any_case_fail and approval.get("analysis_verdict") != "FAIL":
        errors.append("approval.analysis_verdict must be FAIL when an analysis case FAILs")
    if any_case_conditional and approval.get("analysis_verdict") == "PASS":
        errors.append("approval.analysis_verdict cannot be PASS when an analysis case is CONDITIONAL")
    if critical_open and approval.get("analysis_verdict") == "PASS":
        errors.append("approval.analysis_verdict cannot be PASS with open blocker/major actions")
    if approval.get("analysis_verdict") == "PASS" and validation_status not in {"pass", "not_required", "waived_with_justification"}:
        errors.append("approval.analysis_verdict PASS requires completed or justified validation disposition")
    if approval.get("analysis_verdict") == "PASS" and approval.get("independent_review") != "pass":
        errors.append("approval.analysis_verdict PASS requires independent_review=pass")
    if approval.get("analysis_verdict") == "PASS":
        if not release_case_verdicts:
            errors.append(
                "approval.analysis_verdict PASS requires at least one release-driving analysis case"
            )
        elif any(verdict != "PASS" for verdict in release_case_verdicts):
            errors.append(
                "approval.analysis_verdict PASS requires every release-driving case to PASS"
            )
    if approval.get("release_decision") == "approved_by_authority":
        if approval.get("analysis_verdict") != "PASS":
            errors.append("release approval requires analysis_verdict=PASS")
        if approval.get("independent_review") != "pass":
            errors.append("release approval requires independent_review=pass")
        if critical_open:
            errors.append("release approval cannot have open blocker/major actions")
        if not valid_date(approval.get("date")):
            errors.append("release approval requires ISO approval.date")
    elif approval.get("date") is not None and not valid_date(approval.get("date")):
        errors.append("approval.date must be null or ISO YYYY-MM-DD")

    if errors:
        verdict = "FAIL"
    elif approval.get("analysis_verdict") == "PASS":
        verdict = "PASS"
    else:
        verdict = "CONDITIONAL"
        warnings.append("contract is structurally valid but analysis/release approval remains conditional or withheld")
    return {"verdict": verdict, "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit machine-readable result")
    args = parser.parse_args()
    try:
        data = json.loads(args.contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {"verdict": "FAIL", "errors": [str(exc)], "warnings": []}
    else:
        result = validate(data)
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["verdict"])
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 1 if result["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
