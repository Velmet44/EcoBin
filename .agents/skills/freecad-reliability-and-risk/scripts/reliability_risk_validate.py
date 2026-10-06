#!/usr/bin/env python3
"""Fail-closed structural and traceability checks for reliability/risk contracts."""

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
MATURITIES = {"concept", "prototype", "verification", "production_candidate", "released"}
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}
ANALYSIS_TYPES = {"DFMEA", "PFMEA", "FMECA"}
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
REQUIRED_EVIDENCE = {
    "scope_and_functions", "fmea", "hazard_analysis",
    "life_reliability", "action_closure", "change_impact",
}


def present(value):
    if value is None:
        return False
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in SENTINELS or "unassigned" in normalized:
            return False
    return True


def get(data, path):
    value = data
    for key in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def rating(value):
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 10


def positive(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def id_map(items, kind, errors):
    result = {}
    if not isinstance(items, list):
        errors.append(f"{kind} must be a list")
        return result
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{kind}[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not present(item_id):
            errors.append(f"{kind}[{index}].id is required")
        elif item_id in result:
            errors.append(f"duplicate {kind} id: {item_id}")
        else:
            result[item_id] = item
    return result


def valid_date(value):
    try:
        dt.date.fromisoformat(str(value))
        return True
    except ValueError:
        return False


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
        "product.maturity", "product.intended_use", "product.acceptance_authority_role",
        "method.identifier", "method.revision", "method.rating_scale",
        "method.risk_acceptance_rule", "change_control.baseline_id",
    ):
        if not present(get(data, path)):
            errors.append(f"missing controlled value: {path}")
    maturity = get(data, "product.maturity")
    if maturity not in MATURITIES:
        errors.append(f"product.maturity must be one of {sorted(MATURITIES)}")
    for path in ("product.configurations", "product.foreseeable_misuse", "product.lifecycle_stages"):
        value = get(data, path)
        if not isinstance(value, list) or not value or not all(present(v) for v in value):
            errors.append(f"{path} must be a non-empty controlled list")

    functions = id_map(data.get("functions"), "functions", errors)
    if not functions:
        errors.append("at least one function is required")
    for item_id, item in functions.items():
        for field in ("item_id", "configuration", "statement", "requirement_id", "safe_state", "verification_id"):
            if not present(item.get(field)):
                errors.append(f"function {item_id} requires {field}")

    process_steps = id_map(data.get("process_steps"), "process_steps", errors)
    for item_id, item in process_steps.items():
        for field in ("statement", "output_characteristic", "control_plan_id"):
            if not present(item.get(field)):
                errors.append(f"process step {item_id} requires {field}")

    actions = id_map(data.get("actions"), "actions", errors)
    for action_id, action in actions.items():
        for field in ("description", "owner", "due_date", "status"):
            if not present(action.get(field)):
                errors.append(f"action {action_id} requires {field}")
        if present(action.get("due_date")) and not valid_date(action.get("due_date")):
            errors.append(f"action {action_id} due_date must be YYYY-MM-DD")
        if action.get("status") == "closed":
            for field in ("implementation_artifact", "verification_evidence"):
                if not present(action.get(field)):
                    errors.append(f"closed action {action_id} requires {field}")
            post = (action.get("post_severity"), action.get("post_occurrence"), action.get("post_detection"))
            if not all(rating(v) for v in post):
                errors.append(f"closed action {action_id} requires post-action ratings from 1 to 10")
            elif action.get("post_rpn") != post[0] * post[1] * post[2]:
                errors.append(f"closed action {action_id} post_rpn arithmetic is incorrect")

    hazards = id_map(data.get("hazards"), "hazards", errors)
    measures = id_map(data.get("risk_reduction_measures"), "risk_reduction_measures", errors)
    risk_approvals = id_map(data.get("residual_risk_approvals"), "residual_risk_approvals", errors)
    hazard_analysis = data.get("hazard_analysis")
    if not isinstance(hazard_analysis, dict):
        errors.append("hazard_analysis must be an object")
        hazard_analysis = {}
    else:
        for field in (
            "applicable",
            "method",
            "lifecycle_stages_reviewed",
            "approved_by",
            "approved_by_role",
            "approval_date",
        ):
            if not present(hazard_analysis.get(field)):
                errors.append(f"hazard_analysis.{field} is required")
        if not isinstance(hazard_analysis.get("applicable"), bool):
            errors.append("hazard_analysis.applicable must be true or false")
        reviewed = hazard_analysis.get("lifecycle_stages_reviewed")
        required_stages = set(get(data, "product.lifecycle_stages") or [])
        if not isinstance(reviewed, list) or set(reviewed) != required_stages:
            errors.append(
                "hazard_analysis.lifecycle_stages_reviewed must exactly cover "
                "product.lifecycle_stages"
            )
        if present(hazard_analysis.get("approval_date")) and not valid_date(
            hazard_analysis.get("approval_date")
        ):
            errors.append("hazard_analysis.approval_date must be YYYY-MM-DD")
        if hazard_analysis.get("applicable") is False:
            for field in ("non_applicability_rationale",):
                if not present(hazard_analysis.get(field)):
                    errors.append(f"hazard_analysis.{field} is required")
        elif not hazards:
            errors.append("applicable hazard analysis requires at least one hazard")

    for measure_id, measure in measures.items():
        for field in (
            "hierarchy", "requirement_id", "implementation_artifact",
            "verification_id", "status", "introduced_hazard_review",
        ):
            if not present(measure.get(field)):
                errors.append(f"risk reduction measure {measure_id} requires {field}")
        if maturity in {"production_candidate", "released"} and measure.get("status") != "verified":
            errors.append(f"risk reduction measure {measure_id} must be verified for production maturity")

    for approval_id, approval in risk_approvals.items():
        for field in ("approver", "role", "date", "scope", "decision"):
            if not present(approval.get(field)):
                errors.append(f"residual risk approval {approval_id} requires {field}")
        if present(approval.get("date")) and not valid_date(approval.get("date")):
            errors.append(f"residual risk approval {approval_id} date must be YYYY-MM-DD")
        if approval.get("decision") != "accepted":
            errors.append(f"residual risk approval {approval_id} decision must be accepted")
        if not isinstance(approval.get("evidence_reviewed"), list) or not approval.get("evidence_reviewed"):
            errors.append(f"residual risk approval {approval_id} requires evidence_reviewed")
        allowed_roles = get(data, "product.residual_risk_authority_roles")
        if not isinstance(allowed_roles, list) or approval.get("role") not in allowed_roles:
            errors.append(
                f"residual risk approval {approval_id} role is not authorized by product"
            )

    for hazard_id, hazard in hazards.items():
        for field in (
            "lifecycle_stage", "hazard", "sequence", "exposed", "harm",
            "initial_risk", "residual_risk", "residual_risk_approval_id",
        ):
            if not present(hazard.get(field)):
                errors.append(f"hazard {hazard_id} requires {field}")
        measure_ids = hazard.get("measure_ids")
        if not isinstance(measure_ids, list) or not measure_ids:
            errors.append(f"hazard {hazard_id} requires at least one risk-reduction measure")
        else:
            for measure_id in measure_ids:
                if measure_id not in measures:
                    errors.append(f"hazard {hazard_id} references unknown measure {measure_id}")
        if hazard.get("residual_risk_approval_id") not in risk_approvals:
            errors.append(f"hazard {hazard_id} references unknown residual-risk approval")

    modes = id_map(data.get("failure_modes"), "failure_modes", errors)
    if not modes:
        errors.append("at least one failure mode is required")
    for mode_id, mode in modes.items():
        analysis_type = mode.get("analysis_type")
        if analysis_type not in ANALYSIS_TYPES:
            errors.append(f"failure mode {mode_id} analysis_type must be one of {sorted(ANALYSIS_TYPES)}")
        function_id, process_id = mode.get("function_id"), mode.get("process_step_id")
        if analysis_type in {"DFMEA", "FMECA"} and function_id not in functions:
            errors.append(f"failure mode {mode_id} requires a known function_id")
        if analysis_type == "PFMEA" and process_id not in process_steps:
            errors.append(f"failure mode {mode_id} requires a known process_step_id")
        for field in (
            "item_id", "configuration", "lifecycle_state", "failure_mode",
            "local_effect", "next_effect", "end_effect", "rating_rationale",
            "classification_basis", "classified_by",
        ):
            if not present(mode.get(field)):
                errors.append(f"failure mode {mode_id} requires {field}")
        for field in ("causes", "prevention_controls", "detection_controls"):
            if not isinstance(mode.get(field), list) or not mode.get(field) or not all(present(v) for v in mode.get(field, [])):
                errors.append(f"failure mode {mode_id} requires non-empty {field}")
        scores = (mode.get("severity"), mode.get("occurrence"), mode.get("detection"))
        if not all(rating(v) for v in scores):
            errors.append(f"failure mode {mode_id} ratings must be integers from 1 to 10")
        elif mode.get("rpn") != scores[0] * scores[1] * scores[2]:
            errors.append(f"failure mode {mode_id} rpn arithmetic is incorrect")
        safety_related = mode.get("safety_related")
        if not isinstance(safety_related, bool):
            errors.append(f"failure mode {mode_id} safety_related must be true or false")
        hazard_ids = mode.get("hazard_ids")
        requires_escalation = (rating(scores[0]) and scores[0] >= 9) or safety_related is True
        if requires_escalation and (not isinstance(hazard_ids, list) or not hazard_ids):
            errors.append(
                f"high-severity or safety-related failure mode {mode_id} requires hazard linkage"
            )
        if isinstance(hazard_ids, list):
            for hazard_id in hazard_ids:
                if hazard_id not in hazards:
                    errors.append(f"failure mode {mode_id} references unknown hazard {hazard_id}")
        action_ids = mode.get("action_ids")
        if not isinstance(action_ids, list):
            errors.append(f"failure mode {mode_id} action_ids must be a list")
            action_ids = []
        for action_id in action_ids:
            if action_id not in actions:
                errors.append(f"failure mode {mode_id} references unknown action {action_id}")
        if maturity in {"production_candidate", "released"} and requires_escalation:
            if not action_ids or any(actions.get(action_id, {}).get("status") != "closed" for action_id in action_ids):
                errors.append(
                    f"high-severity or safety-related failure mode {mode_id} "
                    "requires closed verified actions"
                )

    exclusions = id_map(data.get("coverage_exclusions"), "coverage_exclusions", errors)
    excluded_function_ids = set()
    excluded_process_ids = set()
    for exclusion_id, exclusion in exclusions.items():
        for field in ("kind", "target_id", "rationale", "approved_by", "approval_date"):
            if not present(exclusion.get(field)):
                errors.append(f"coverage exclusion {exclusion_id} requires {field}")
        if present(exclusion.get("approval_date")) and not valid_date(
            exclusion.get("approval_date")
        ):
            errors.append(
                f"coverage exclusion {exclusion_id} approval_date must be YYYY-MM-DD"
            )
        if exclusion.get("kind") == "function":
            if exclusion.get("target_id") not in functions:
                errors.append(
                    f"coverage exclusion {exclusion_id} references unknown function"
                )
            excluded_function_ids.add(exclusion.get("target_id"))
        elif exclusion.get("kind") == "process_step":
            if exclusion.get("target_id") not in process_steps:
                errors.append(
                    f"coverage exclusion {exclusion_id} references unknown process step"
                )
            excluded_process_ids.add(exclusion.get("target_id"))
        else:
            errors.append(
                f"coverage exclusion {exclusion_id} kind must be function or process_step"
            )
    analyzed_function_ids = {
        mode.get("function_id")
        for mode in modes.values()
        if mode.get("analysis_type") in {"DFMEA", "FMECA"}
    }
    analyzed_process_ids = {
        mode.get("process_step_id")
        for mode in modes.values()
        if mode.get("analysis_type") == "PFMEA"
    }
    uncovered_functions = set(functions) - analyzed_function_ids - excluded_function_ids
    uncovered_processes = set(process_steps) - analyzed_process_ids - excluded_process_ids
    if uncovered_functions:
        errors.append(
            f"functions lack FMEA coverage or approved exclusion: {sorted(uncovered_functions)}"
        )
    if uncovered_processes:
        errors.append(
            f"process steps lack PFMEA coverage or approved exclusion: {sorted(uncovered_processes)}"
        )

    life_items = id_map(data.get("life_evidence"), "life_evidence", errors)
    if not life_items:
        errors.append("at least one life_evidence item is required")
    for life_id, item in life_items.items():
        for field in (
            "item_id", "configuration", "mission_profile", "failure_mechanism",
            "method_source", "evidence", "status",
        ):
            if not present(item.get(field)):
                errors.append(f"life evidence {life_id} requires {field}")
        required = item.get("required_cycles")
        demonstrated = item.get("demonstrated_or_calculated_cycles")
        if not positive(required):
            errors.append(f"life evidence {life_id} required_cycles must be positive")
        if not positive(demonstrated):
            errors.append(f"life evidence {life_id} demonstrated_or_calculated_cycles must be positive")
        if positive(required) and positive(demonstrated) and demonstrated < required:
            errors.append(f"life evidence {life_id} does not meet required cycles")
        if maturity in {"production_candidate", "released"} and item.get("status") != "pass":
            errors.append(f"life evidence {life_id} must have status=pass for production maturity")

    change = data.get("change_control")
    if not isinstance(change, dict):
        errors.append("change_control must be an object")
    else:
        hashes = change.get("input_hashes")
        if not isinstance(hashes, list) or not hashes:
            errors.append("change_control.input_hashes must be a non-empty list")
        elif any(not isinstance(value, str) or not SHA256.fullmatch(value) for value in hashes):
            errors.append("change_control.input_hashes must contain 64-character SHA-256 values")
        triggers = change.get("invalidation_triggers")
        if not isinstance(triggers, list) or not triggers or not all(present(v) for v in triggers):
            errors.append("change_control.invalidation_triggers must be a non-empty controlled list")
        impacts = change.get("open_change_impacts")
        if not isinstance(impacts, list):
            errors.append("change_control.open_change_impacts must be a list")
        elif maturity in {"production_candidate", "released"} and impacts:
            errors.append("production maturity cannot have open change impacts")

    evidence_items = data.get("release_evidence")
    seen = set()
    if not isinstance(evidence_items, list):
        errors.append("release_evidence must be a list")
        evidence_items = []
    for index, item in enumerate(evidence_items):
        if not isinstance(item, dict):
            errors.append(f"release_evidence[{index}] must be an object")
            continue
        kind = item.get("type")
        if kind in seen:
            errors.append(f"duplicate release evidence type: {kind}")
        seen.add(kind)
        if not present(kind) or not present(item.get("artifact")):
            errors.append(f"release_evidence[{index}] requires type and artifact")
        if not isinstance(item.get("source_hash"), str) or not SHA256.fullmatch(
            item.get("source_hash", "")
        ):
            errors.append(
                f"release_evidence[{index}].source_hash must be a controlled SHA-256"
            )
        configurations = item.get("configurations")
        product_configurations = set(get(data, "product.configurations") or [])
        if (
            not isinstance(configurations, list)
            or not configurations
            or set(configurations) != product_configurations
        ):
            errors.append(
                f"release_evidence[{index}].configurations must exactly cover product configurations"
            )
        if item.get("status") != "pass":
            errors.append(f"release_evidence[{index}] must have status=pass")

    if maturity in {"production_candidate", "released"}:
        missing = REQUIRED_EVIDENCE - seen
        if missing:
            errors.append(f"production maturity missing release evidence: {sorted(missing)}")
        approvals = data.get("approvals")
        if not isinstance(approvals, list) or not approvals:
            errors.append("production maturity requires approvals")
        else:
            authority_coverage = set()
            for index, approval in enumerate(approvals):
                if not isinstance(approval, dict):
                    errors.append(f"approvals[{index}] must be an object")
                    continue
                for field in ("approver", "role", "date", "scope", "decision"):
                    if not present(approval.get(field)):
                        errors.append(f"approvals[{index}].{field} is required")
                if present(approval.get("date")) and not valid_date(approval.get("date")):
                    errors.append(f"approvals[{index}].date must be YYYY-MM-DD")
                if approval.get("decision") != "approved":
                    errors.append(f"approvals[{index}].decision must be approved")
                configurations = approval.get("configurations")
                if (
                    approval.get("role")
                    == get(data, "product.acceptance_authority_role")
                    and approval.get("decision") == "approved"
                    and isinstance(configurations, list)
                ):
                    authority_coverage.update(configurations)
            missing_authority = set(get(data, "product.configurations") or []) - authority_coverage
            if missing_authority:
                errors.append(
                    "acceptance-authority approval does not cover configurations "
                    f"{sorted(missing_authority)}"
                )
        if record_state != "controlled_evidence":
            warnings.append("template/fixture record cannot receive a production PASS")
    else:
        warnings.append("non-production maturity: release closure is not enforced")

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
