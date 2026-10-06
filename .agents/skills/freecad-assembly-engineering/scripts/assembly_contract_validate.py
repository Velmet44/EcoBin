#!/usr/bin/env python3
"""Validate assembly product structure and declared evidence references.

This checks a JSON engineering contract. It does not open FreeCAD, solve joints,
run collision tests, verify external files, or authorize a release.
"""

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


ITEM_TYPES = {"make", "buy", "standard", "bulk", "consumable", "reference", "ecad", "software"}
MATURITIES = {"concept", "prototype", "production_candidate", "released"}
INTERFACE_CLASSES = {"forbidden_interference", "intentional_contact", "clearance", "transition", "interference", "flexible_envelope"}
TEST_STATUSES = {"planned", "pass", "fail", "waived"}
TEST_KINDS = {"solve_dof", "static_clearance", "swept_motion", "fit_stack", "installation", "service", "functional", "mass_properties", "other"}
MASS_APPLICABILITY = {"required", "non_mass_item", "included_in_parent", "excluded_with_justification"}
EVIDENCE_TYPES = {"bom_reconciliation", "assembly_sequence", "mass_properties", "exploded_view_review", "motion_clearance", "step_reimport"}
REQUIRED_EVIDENCE = {"bom_reconciliation", "assembly_sequence", "mass_properties", "exploded_view_review", "motion_clearance"}
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
LENGTH = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)\s*(?:mm|in|µm|um)$")


def present(value):
    if value is None:
        return False
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"", "tbd", "unassigned", "unknown", "n/a", "na", "none", "null", "pending", "xxx", "?", "yyyy-mm-dd"}:
            return False
        if "unassigned" in normalized:
            return False
    return True


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def evidence_list(value):
    return isinstance(value, list) and bool(value) and all(present(item) for item in value)


def object_list(data, key, errors):
    value = data.get(key)
    if value is None:
        errors.append(f"{key} must be a list, not null")
        return []
    if not isinstance(value, list):
        errors.append(f"{key} must be a list")
        return []
    normalized = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{key}[{index}] must be a structured object")
            normalized.append({})
        else:
            normalized.append(item)
    return normalized


def validate(data):
    errors = []
    warnings = []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["contract root must be a JSON object"], "warnings": []}
    product = data.get("product")
    if not isinstance(product, dict):
        errors.append("product must be a structured object")
        product = {}
    configs = object_list(data, "configurations", errors)
    definitions = object_list(data, "definitions", errors)
    occurrences = object_list(data, "occurrences", errors)
    grounds = object_list(data, "grounding", errors)
    joints = object_list(data, "joints", errors)
    test_cases = object_list(data, "test_cases", errors)
    interfaces = object_list(data, "interfaces", errors)
    release_evidence = object_list(data, "release_evidence", errors)
    approvals = object_list(data, "approvals", errors)
    for key in (
        "part_number", "name", "revision", "maturity", "units",
        "coordinate_system", "governing_product_definition", "acceptance_authority_role",
    ):
        if not present(product.get(key)):
            errors.append(f"product.{key} is not controlled")
    if product.get("maturity") not in MATURITIES:
        errors.append(f"product.maturity must be one of {sorted(MATURITIES)}")

    config_ids = [c.get("id") for c in configs]
    if not configs or any(not present(v) for v in config_ids):
        errors.append("at least one named configuration is required")
    if len(config_ids) != len(set(config_ids)):
        errors.append("configuration IDs must be unique")
    for index, configuration in enumerate(configs):
        for key in ("effectivity", "status"):
            if not present(configuration.get(key)):
                errors.append(f"configurations[{index}].{key} is required")

    definition_keys = []
    for index, definition in enumerate(definitions):
        key = (definition.get("part_number"), definition.get("revision"))
        definition_keys.append(key)
        if not all(present(v) for v in key):
            errors.append(f"definitions[{index}] requires part_number and revision")
        if definition.get("item_type") not in ITEM_TYPES:
            errors.append(f"definitions[{index}].item_type must be one of {sorted(ITEM_TYPES)}")
        mass = definition.get("mass")
        if not isinstance(mass, dict):
            errors.append(f"definitions[{index}].mass must be a structured object")
            mass = {}
        if product.get("maturity") in {"production_candidate", "released"}:
            applicability = mass.get("applicability")
            if applicability not in MASS_APPLICABILITY:
                errors.append(f"definitions[{index}].mass.applicability must be one of {sorted(MASS_APPLICABILITY)}")
            item_type = definition.get("item_type")
            if item_type in {"make", "buy", "standard", "ecad"} and applicability != "required":
                errors.append(f"definitions[{index}] mass-bearing item requires mass.applicability=required")
            if item_type in {"reference", "software"} and applicability != "non_mass_item":
                errors.append(f"definitions[{index}] reference/software item requires mass.applicability=non_mass_item")
            if applicability == "required":
                if not isinstance(mass.get("value"), (int, float)) or mass.get("value", 0) <= 0:
                    errors.append(f"definitions[{index}] requires positive controlled mass")
                if not present(mass.get("source")):
                    errors.append(f"definitions[{index}] requires mass source")
            elif applicability in {"included_in_parent", "excluded_with_justification"}:
                if not present(mass.get("justification")):
                    errors.append(f"definitions[{index}] mass exclusion/inclusion requires justification")
    if len(definition_keys) != len(set(definition_keys)):
        errors.append("definition part_number/revision keys must be unique")
    known_definitions = set(definition_keys)

    occurrence_ids = [o.get("occurrence_id") for o in occurrences]
    if not occurrences:
        errors.append("at least one occurrence is required")
    if any(not present(v) for v in occurrence_ids) or len(occurrence_ids) != len(set(occurrence_ids)):
        errors.append("occurrence IDs must be present and unique")
    known_occurrences = set(occurrence_ids)
    children = defaultdict(list)
    for index, occurrence in enumerate(occurrences):
        key = (occurrence.get("part_number"), occurrence.get("revision"))
        if key not in known_definitions:
            errors.append(f"occurrences[{index}] references unknown definition {key}")
        quantity = occurrence.get("quantity")
        if quantity != 1:
            errors.append(f"occurrences[{index}].quantity must be 1; represent repeated placements as unique occurrences")
        parent = occurrence.get("parent_occurrence_id")
        if parent is not None and parent not in known_occurrences:
            errors.append(f"occurrences[{index}] references unknown parent {parent}")
        children[parent].append(occurrence.get("occurrence_id"))
        memberships = occurrence.get("configuration_ids")
        if not isinstance(memberships, list):
            errors.append(f"occurrences[{index}].configuration_ids must be a list")
            memberships = []
        unknown = sorted(set(memberships) - set(config_ids))
        if not memberships or unknown:
            errors.append(f"occurrences[{index}] requires valid configuration_ids; unknown={unknown}")

    colors = {node: 0 for node in known_occurrences}
    for start in known_occurrences:
        if colors[start] != 0:
            continue
        stack = [(start, False)]
        path = []
        while stack:
            node, exiting = stack.pop()
            if exiting:
                colors[node] = 2
                if path and path[-1] == node:
                    path.pop()
                continue
            if colors[node] == 1:
                errors.append(f"occurrence hierarchy cycle detected at {node}")
                continue
            if colors[node] == 2:
                continue
            colors[node] = 1
            path.append(node)
            stack.append((node, True))
            for child in children.get(node, []):
                if child in known_occurrences:
                    if colors[child] == 1:
                        errors.append("occurrence hierarchy cycle: " + " -> ".join(path + [child]))
                    elif colors[child] == 0:
                        stack.append((child, False))
    reachable = set()
    stack = list(children.get(None, []))
    while stack:
        node = stack.pop()
        if node in reachable:
            continue
        reachable.add(node)
        stack.extend(children.get(node, []))
    orphaned = sorted(known_occurrences - reachable)
    if orphaned:
        errors.append(f"occurrences are not reachable from a root: {orphaned}")
    if len(children.get(None, [])) != 1:
        message = "contract must declare exactly one root occurrence"
        if product.get("maturity") in {"production_candidate", "released"}:
            errors.append(message)
        else:
            warnings.append(message)

    ground_by_config = Counter()
    for index, ground in enumerate(grounds):
        for key in ("configuration_id", "occurrence_id", "datum", "intent"):
            if not present(ground.get(key)):
                errors.append(f"grounding[{index}].{key} is required")
        if ground.get("configuration_id") not in config_ids:
            errors.append(f"grounding[{index}] references unknown configuration")
        if ground.get("occurrence_id") not in known_occurrences:
            errors.append(f"grounding[{index}] references unknown occurrence")
        ground_by_config[ground.get("configuration_id")] += 1
    if product.get("maturity") in {"production_candidate", "released"}:
        for config_id in config_ids:
            if ground_by_config[config_id] != 1:
                errors.append(f"configuration {config_id} requires exactly one intentional ground declaration")

    joint_ids = []
    for index, joint in enumerate(joints):
        joint_ids.append(joint.get("joint_id"))
        for key in ("joint_id", "occurrence_a", "occurrence_b", "type", "expected_remaining_dof"):
            if not present(joint.get(key)) and joint.get(key) != 0:
                errors.append(f"joints[{index}].{key} is required")
        if not isinstance(joint.get("test_case_ids"), list) or not joint.get("test_case_ids"):
            errors.append(f"joints[{index}].test_case_ids must name at least one test")
        for key in ("occurrence_a", "occurrence_b"):
            if joint.get(key) not in known_occurrences:
                errors.append(f"joints[{index}].{key} references unknown occurrence")
    duplicates = [key for key, count in Counter(joint_ids).items() if key and count > 1]
    if duplicates:
        errors.append(f"duplicate joint IDs: {duplicates}")

    test_ids = [t.get("id") for t in test_cases]
    if len(test_ids) != len(set(test_ids)):
        errors.append("test case IDs must be unique")
    tests_by_id = {}
    for index, test in enumerate(test_cases):
        tests_by_id[test.get("id")] = test
        for key in ("id", "kind", "configuration_id", "status", "expected", "actual", "evidence"):
            if not present(test.get(key)):
                errors.append(f"test_cases[{index}].{key} is required")
        if test.get("kind") not in TEST_KINDS:
            errors.append(f"test_cases[{index}].kind must be one of {sorted(TEST_KINDS)}")
        if test.get("status") not in TEST_STATUSES:
            errors.append(f"test_cases[{index}].status must be one of {sorted(TEST_STATUSES)}")
        if test.get("configuration_id") not in config_ids:
            errors.append(f"test_cases[{index}] references unknown configuration")
        if not evidence_list(test.get("evidence")):
            errors.append(f"test_cases[{index}].evidence must be a non-empty list")
        if test.get("kind") == "swept_motion":
            for key in ("coverage", "sampling_or_analytical_method", "refinement_rule"):
                if not present(test.get(key)):
                    errors.append(f"swept-motion test {test.get('id')} requires {key}")
        if product.get("maturity") in {"production_candidate", "released"} and test.get("status") != "pass":
            errors.append(f"release-like test {test.get('id')} must have status=pass")
    for joint in joints:
        joint_tests = joint.get("test_case_ids")
        if not isinstance(joint_tests, list):
            joint_tests = []
        unknown = sorted(set(joint_tests) - set(test_ids))
        if unknown:
            errors.append(f"joint {joint.get('joint_id')} references unknown test cases {unknown}")
        for test_id in joint_tests:
            if product.get("maturity") in {"production_candidate", "released"} and tests_by_id.get(test_id, {}).get("status") != "pass":
                errors.append(f"joint {joint.get('joint_id')} references non-passing test {test_id}")

    for index, interface in enumerate(interfaces):
        for key in (
            "interface_id", "configuration_id", "occurrence_a", "datum_a",
            "occurrence_b", "datum_b", "function", "classification",
            "standard_and_edition", "worst_case_min", "worst_case_max",
            "thermal_coating_load_basis", "test_case_id", "status", "evidence",
        ):
            if not present(interface.get(key)):
                errors.append(f"interfaces[{index}].{key} is required")
        if interface.get("classification") not in INTERFACE_CLASSES:
            errors.append(f"interfaces[{index}].classification must be one of {sorted(INTERFACE_CLASSES)}")
        for key in ("worst_case_min", "worst_case_max"):
            value = interface.get(key)
            if present(value) and not LENGTH.fullmatch(str(value).strip()):
                errors.append(f"interfaces[{index}].{key} must be a signed value with mm, µm/um, or in")
        if interface.get("configuration_id") not in config_ids:
            errors.append(f"interfaces[{index}] references unknown configuration")
        for key in ("occurrence_a", "occurrence_b"):
            if interface.get(key) not in known_occurrences:
                errors.append(f"interfaces[{index}].{key} references unknown occurrence")
        test_id = interface.get("test_case_id")
        if test_id not in test_ids:
            errors.append(f"interfaces[{index}] references unknown test case {test_id}")
        if product.get("maturity") in {"production_candidate", "released"}:
            if interface.get("status") != "pass":
                errors.append(f"interfaces[{index}] must have status=pass")
            if not evidence_list(interface.get("evidence")):
                errors.append(f"interfaces[{index}].evidence must be a non-empty list")

    release_like = product.get("maturity") in {"production_candidate", "released"}
    if release_like:
        required_lists = {
            "joints": joints,
            "interfaces": interfaces,
            "test_cases": test_cases,
            "approvals": approvals,
        }
        for required, value in required_lists.items():
            if not value:
                errors.append(f"{required} must not be empty for {product.get('maturity')}")
        for index, definition in enumerate(definitions):
            if definition.get("item_type") in {"buy", "standard", "ecad", "bulk", "consumable"} and not present(definition.get("component_record")):
                errors.append(f"definitions[{index}] requires a governed component_record")
        evidence_types = set()
        evidence_coverage = defaultdict(set)
        for index, item in enumerate(release_evidence):
            evidence_types.add(item.get("type"))
            memberships = item.get("configuration_ids")
            if not isinstance(memberships, list):
                errors.append(f"release_evidence[{index}].configuration_ids must be a list")
                memberships = []
            evidence_coverage[item.get("type")].update(memberships)
            for key in ("evidence_id", "type", "configuration_ids", "status", "artifact"):
                if not present(item.get(key)):
                    errors.append(f"release_evidence[{index}].{key} is required")
            if item.get("type") not in EVIDENCE_TYPES:
                errors.append(f"release_evidence[{index}].type must be one of {sorted(EVIDENCE_TYPES)}")
            if item.get("status") != "pass":
                errors.append(f"release_evidence[{index}] must have status=pass")
            unknown = sorted(set(memberships) - set(config_ids))
            if not memberships or unknown:
                errors.append(f"release_evidence[{index}] requires valid configuration_ids; unknown={unknown}")
            digest = item.get("source_hash")
            if not present(digest) or not SHA256.fullmatch(str(digest)):
                errors.append(f"release_evidence[{index}].source_hash must be a controlled SHA-256")
        missing_evidence = sorted(REQUIRED_EVIDENCE - evidence_types)
        if missing_evidence:
            errors.append(f"missing required release evidence types: {missing_evidence}")
        for evidence_type in REQUIRED_EVIDENCE:
            missing_configs = sorted(set(config_ids) - evidence_coverage[evidence_type])
            if missing_configs:
                errors.append(f"release evidence {evidence_type} does not cover configurations {missing_configs}")

        approved_roles = set()
        acceptance_coverage = set()
        for index, approval in enumerate(approvals):
            if not isinstance(approval, dict):
                errors.append(f"approvals[{index}] must be a structured object")
                continue
            for key in ("approver", "role", "date", "scope", "configuration_ids", "decision"):
                if not present(approval.get(key)):
                    errors.append(f"approvals[{index}].{key} is required")
            if not valid_date(approval.get("date")):
                errors.append(f"approvals[{index}].date must be ISO YYYY-MM-DD")
            if approval.get("decision") != "approved":
                errors.append(f"approvals[{index}].decision must be approved")
            memberships = approval.get("configuration_ids")
            if not isinstance(memberships, list):
                errors.append(f"approvals[{index}].configuration_ids must be a list")
                memberships = []
            unknown = sorted(set(memberships) - set(config_ids))
            if not memberships or unknown:
                errors.append(f"approvals[{index}] requires valid configuration_ids; unknown={unknown}")
            approved_roles.add(approval.get("role"))
            if approval.get("role") == product.get("acceptance_authority_role"):
                acceptance_coverage.update(memberships)
        if product.get("acceptance_authority_role") not in approved_roles:
            errors.append("approval from product.acceptance_authority_role is required")
        missing_approval_configs = sorted(set(config_ids) - acceptance_coverage)
        if missing_approval_configs:
            errors.append(f"acceptance-authority approval does not cover configurations {missing_approval_configs}")

    return {"verdict": "PASS" if not errors else "FAIL", "errors": errors, "warnings": warnings}


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
    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
