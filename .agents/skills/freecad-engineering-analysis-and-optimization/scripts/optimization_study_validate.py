#!/usr/bin/env python3
"""Validate a deterministic optimization-study contract.

The script validates study design and confirmation evidence. It does not run
DOE, solve CAD/FEM models, or prove that an optimum is globally or physically valid.
"""

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

from validation_common import present


DIRECTIONS = {"minimize", "maximize", "target"}
OPERATORS = {"<=", "<", ">=", ">", "=="}
STATUSES = {"planned", "running", "complete", "superseded"}
APPROVALS = {"not_selected", "selected_pending_confirmation", "confirmed"}
CONFIRMATION_FIELDS = {"authoritative_rebuild", "independent_fine_mesh", "analytical_check", "dfm_review"}
HASH = re.compile(r"^[0-9a-fA-F]{64}$")
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def checked_evidence(record, path, errors, quantitative=False):
    if not isinstance(record, dict):
        errors.append(f"{path} must be structured evidence")
        return
    for key in ("status", "report_sha256", "configuration_hash"):
        if not present(record.get(key)):
            errors.append(f"{path}.{key} is required")
    for key in ("report_sha256", "configuration_hash"):
        if present(record.get(key)) and not HASH.fullmatch(str(record[key])):
            errors.append(f"{path}.{key} must be a SHA-256")
    if record.get("status") != "pass":
        errors.append(f"{path}.status must be pass")
    if quantitative:
        for key in ("result_delta_percent", "tolerance_percent"):
            if not finite(record.get(key)) or record.get(key, -1) < 0:
                errors.append(f"{path}.{key} must be finite and non-negative")
        if (
            finite(record.get("result_delta_percent"))
            and finite(record.get("tolerance_percent"))
            and record["result_delta_percent"] > record["tolerance_percent"]
        ):
            errors.append(f"{path} exceeds its declared correlation tolerance")


def validate(data):
    errors = []
    warnings = []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["study root must be an object"], "warnings": []}
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    record_state = data.get("record_state")
    if record_state not in RECORD_STATES:
        errors.append(f"record_state must be one of {sorted(RECORD_STATES)}")
    study = data.get("study") if isinstance(data.get("study"), dict) else {}
    for key in ("id", "revision", "baseline_analysis_contract", "status", "seed"):
        if not present(study.get(key)):
            errors.append(f"study.{key} is required")
    if study.get("status") not in STATUSES:
        errors.append(f"study.status must be one of {sorted(STATUSES)}")
    if not isinstance(study.get("seed"), int) or isinstance(study.get("seed"), bool):
        errors.append("study.seed must be an integer")

    objectives = data.get("objectives")
    variables = data.get("variables")
    constraints = data.get("constraints")
    noise = data.get("noise_variables")
    confirmations = data.get("confirmation_runs")
    for name, value in (("objectives", objectives), ("variables", variables), ("constraints", constraints), ("noise_variables", noise), ("confirmation_runs", confirmations)):
        if not isinstance(value, list):
            errors.append(f"{name} must be a list")
    objectives = objectives if isinstance(objectives, list) else []
    variables = variables if isinstance(variables, list) else []
    constraints = constraints if isinstance(constraints, list) else []
    noise = noise if isinstance(noise, list) else []
    confirmations = confirmations if isinstance(confirmations, list) else []
    if not objectives:
        errors.append("at least one objective is required")
    if not variables:
        errors.append("at least one design variable is required")
    if not constraints:
        errors.append("at least one requirement-linked constraint is required")

    for name, items, id_key in (("objectives", objectives, "id"), ("variables", variables, "name")):
        keys = [item.get(id_key) for item in items if isinstance(item, dict)]
        if len(keys) != len(set(keys)):
            errors.append(f"{name} {id_key} values must be unique")

    for index, objective in enumerate(objectives):
        if not isinstance(objective, dict):
            errors.append(f"objectives[{index}] must be an object")
            continue
        for key in ("id", "quantity", "direction", "unit"):
            if not present(objective.get(key)):
                errors.append(f"objectives[{index}].{key} is required")
        if objective.get("direction") not in DIRECTIONS:
            errors.append(f"objectives[{index}].direction must be one of {sorted(DIRECTIONS)}")
        if objective.get("direction") == "target" and not isinstance(objective.get("target"), (int, float)):
            errors.append(f"objectives[{index}].target is required for target direction")

    for index, variable in enumerate(variables):
        if not isinstance(variable, dict):
            errors.append(f"variables[{index}] must be an object")
            continue
        for key in ("name", "unit", "lower", "upper", "manufacturing_resolution"):
            if not present(variable.get(key)):
                errors.append(f"variables[{index}].{key} is required")
        lower, upper, resolution = variable.get("lower"), variable.get("upper"), variable.get("manufacturing_resolution")
        if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in (lower, upper, resolution)):
            errors.append(f"variables[{index}] bounds and resolution must be finite numeric")
        elif not lower < upper:
            errors.append(f"variables[{index}].lower must be less than upper")
        elif resolution <= 0 or resolution > upper - lower:
            errors.append(f"variables[{index}].manufacturing_resolution must be positive and no larger than range")

    requirement_ids = []
    for index, constraint in enumerate(constraints):
        if not isinstance(constraint, dict):
            errors.append(f"constraints[{index}] must be an object")
            continue
        for key in ("requirement_id", "quantity", "operator", "limit", "unit"):
            if not present(constraint.get(key)):
                errors.append(f"constraints[{index}].{key} is required")
        requirement_ids.append(constraint.get("requirement_id"))
        if constraint.get("operator") not in OPERATORS:
            errors.append(f"constraints[{index}].operator must be one of {sorted(OPERATORS)}")
        if not isinstance(constraint.get("limit"), (int, float)) or not math.isfinite(constraint.get("limit", math.nan)):
            errors.append(f"constraints[{index}].limit must be finite numeric")
    duplicates = sorted(str(key) for key, count in Counter(requirement_ids).items() if key and count > 1)
    if duplicates:
        warnings.append(f"multiple constraints share requirement IDs: {duplicates}; confirm this is intentional")

    for index, item in enumerate(noise):
        if not isinstance(item, dict):
            errors.append(f"noise_variables[{index}] must be an object")
            continue
        for key in ("name", "unit", "distribution", "source"):
            if not present(item.get(key)):
                errors.append(f"noise_variables[{index}].{key} is required")

    sampling = data.get("sampling")
    if not isinstance(sampling, dict):
        errors.append("sampling must be an object")
    else:
        for key in ("method", "requested_samples", "failed_design_policy", "surrogate_validation"):
            if not present(sampling.get(key)):
                errors.append(f"sampling.{key} is required")
        if not isinstance(sampling.get("requested_samples"), int) or isinstance(sampling.get("requested_samples"), bool) or sampling.get("requested_samples", 0) <= 0:
            errors.append("sampling.requested_samples must be a positive integer")

    outputs = data.get("outputs")
    if not isinstance(outputs, dict):
        errors.append("outputs must be an object")
    else:
        for key in ("run_table", "sensitivity", "pareto_candidates", "robustness"):
            if not present(outputs.get(key)):
                errors.append(f"outputs.{key} is required")

    results = data.get("results")
    if not isinstance(results, dict):
        errors.append("results must be an object")
        results = {}
    candidates = results.get("candidates")
    if not isinstance(candidates, list):
        errors.append("results.candidates must be a list")
        candidates = []
    candidate_ids = []
    objective_ids = {item.get("id") for item in objectives if isinstance(item, dict)}
    constraint_ids = {item.get("requirement_id") for item in constraints if isinstance(item, dict)}
    variable_names = {item.get("name") for item in variables if isinstance(item, dict)}
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"results.candidates[{index}] must be an object")
            continue
        for key in ("id", "variables", "objectives", "constraints", "feasible", "result_sha256"):
            if not present(candidate.get(key)):
                errors.append(f"results.candidates[{index}].{key} is required")
        candidate_ids.append(candidate.get("id"))
        if set((candidate.get("variables") or {}).keys()) != variable_names:
            errors.append(f"results.candidates[{index}] variable coverage is not exact")
        if set((candidate.get("objectives") or {}).keys()) != objective_ids:
            errors.append(f"results.candidates[{index}] objective coverage is not exact")
        if set((candidate.get("constraints") or {}).keys()) != constraint_ids:
            errors.append(f"results.candidates[{index}] constraint coverage is not exact")
        for section in ("variables", "objectives", "constraints"):
            if not isinstance(candidate.get(section), dict) or any(
                not finite(value) for value in (candidate.get(section) or {}).values()
            ):
                errors.append(f"results.candidates[{index}].{section} values must be finite numeric")
        if present(candidate.get("result_sha256")) and not HASH.fullmatch(str(candidate["result_sha256"])):
            errors.append(f"results.candidates[{index}].result_sha256 must be a SHA-256")
    if len(candidate_ids) != len(set(candidate_ids)):
        errors.append("results candidate IDs must be unique")

    for index, confirmation in enumerate(confirmations):
        if not isinstance(confirmation, dict):
            errors.append(f"confirmation_runs[{index}] must be an object")
            continue
        for key in ("candidate_id", "status", *sorted(CONFIRMATION_FIELDS)):
            if not present(confirmation.get(key)):
                errors.append(f"confirmation_runs[{index}].{key} is required")

    selection = data.get("selection")
    if not isinstance(selection, dict):
        errors.append("selection must be an object")
        selection = {}
    approval = selection.get("approval_status")
    if approval not in APPROVALS:
        errors.append(f"selection.approval_status must be one of {sorted(APPROVALS)}")
    if approval in {"selected_pending_confirmation", "confirmed"}:
        if not present(selection.get("candidate_id")) or not present(selection.get("rationale")):
            errors.append("selected candidate requires candidate_id and rationale")
        selected = [item for item in confirmations if isinstance(item, dict) and item.get("candidate_id") == selection.get("candidate_id")]
        selected_result = next(
            (item for item in candidates if isinstance(item, dict) and item.get("id") == selection.get("candidate_id")),
            None,
        )
        if selected_result is None:
            errors.append("selected candidate does not resolve in results.candidates")
        elif selected_result.get("feasible") is not True:
            errors.append("selected candidate must be quantitatively feasible")
        if not selected:
            errors.append("selected candidate requires a matching confirmation run")
        elif approval == "confirmed":
            for index, confirmation in enumerate(selected):
                if confirmation.get("status") != "pass":
                    errors.append(f"confirmed candidate confirmation_runs[{index}].status must be pass")
                for field in CONFIRMATION_FIELDS:
                    checked_evidence(
                        confirmation.get(field),
                        f"confirmation_runs[{index}].{field}",
                        errors,
                        field in {"independent_fine_mesh", "analytical_check"},
                    )
            deltas = selection.get("objective_deltas_from_baseline")
            if not isinstance(deltas, dict) or set(deltas) != objective_ids or any(
                not finite(value) for value in (deltas or {}).values()
            ):
                errors.append("confirmed selection requires finite objective_deltas_from_baseline for every objective")
            robustness = results.get("robustness")
            if not isinstance(robustness, dict):
                errors.append("confirmed selection requires structured results.robustness")
            else:
                for key in ("candidate_id", "sample_count", "constraint_pass_rate", "report_sha256"):
                    if not present(robustness.get(key)):
                        errors.append(f"results.robustness.{key} is required")
                if robustness.get("candidate_id") != selection.get("candidate_id"):
                    errors.append("results.robustness candidate does not match selection")
                if not isinstance(robustness.get("sample_count"), int) or isinstance(robustness.get("sample_count"), bool) or robustness.get("sample_count", 0) <= 0:
                    errors.append("results.robustness.sample_count must be positive")
                if not finite(robustness.get("constraint_pass_rate")) or not 0 <= robustness.get("constraint_pass_rate", -1) <= 1:
                    errors.append("results.robustness.constraint_pass_rate must be between zero and one")
                if present(robustness.get("report_sha256")) and not HASH.fullmatch(str(robustness["report_sha256"])):
                    errors.append("results.robustness.report_sha256 must be a SHA-256")
    if study.get("status") == "complete" and approval == "not_selected":
        warnings.append("completed study has no selected candidate")

    if errors:
        verdict = "FAIL"
    elif approval == "confirmed" and record_state == "controlled_evidence":
        verdict = "PASS"
    elif record_state != "controlled_evidence":
        verdict = "DRAFT"
    else:
        verdict = "CONDITIONAL"
        warnings.append("study structure is valid but no candidate has completed confirmation")
    return {"verdict": verdict, "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(args.study.read_text(encoding="utf-8"))
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
