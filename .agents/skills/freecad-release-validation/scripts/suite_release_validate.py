#!/usr/bin/env python3
"""Fail-closed semantic gate across the production FreeCAD skill suite."""

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

HASH = re.compile(r"^[0-9a-fA-F]{64}$")
PASSING = {"PASS", "RELEASED", "FINITE_EXHAUSTIVE_PASS", "SAMPLED_PASS"}
BASE_DOMAINS = {
    "parametric-model", "release-validation", "product-definition",
    "tolerance-capability", "dfm", "manufacturing-plan",
    "bom-configuration", "reliability-risk",
}
SCOPED_DOMAINS = {
    "analysis": {"engineering-analysis"},
    "assembly": {"assembly-engineering", "assembly-visualization"},
    "robotics": {"robotics-mechanism", "robot-motion-dynamics"},
    "cam": {"cam-planning"},
    "additive": {"additive-manufacturing"},
    "purchased_components": {"component-sourcing"},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def present(value):
    return value is not None and value not in ("", [], {})


def iso_date(value):
    try:
        dt.date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def required_domains(scope):
    domains = set(BASE_DOMAINS)
    for flag, additions in SCOPED_DOMAINS.items():
        if scope.get(flag) is True:
            domains.update(additions)
    return domains


def load_bound_file(root, record, prefix, errors):
    relative = record.get(f"{prefix}_path")
    expected = record.get(f"{prefix}_sha256")
    if not isinstance(relative, str) or not relative:
        errors.append(f"{prefix}_path is required")
        return None
    if not isinstance(expected, str) or not HASH.fullmatch(expected):
        errors.append(f"{prefix}_sha256 must be a SHA-256")
        return None
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        errors.append(f"unsafe {prefix}_path {relative}")
        return None
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{prefix}_path escapes release root")
        return None
    if not path.is_file():
        errors.append(f"missing {prefix} file {relative}")
        return None
    if digest(path) != expected.lower():
        errors.append(f"{prefix} hash mismatch for {relative}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        errors.append(f"{prefix} file is not valid JSON: {relative}")
        return None


def validate(data, release_root):
    errors, warnings = [], []
    metrics = {}
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["suite contract must be an object"], "warnings": [], "metrics": {}}
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    product = data.get("product")
    if not isinstance(product, dict):
        errors.append("product must be an object")
        product = {}
    for key in ("part_number", "revision", "configuration", "maturity", "acceptance_authority_role"):
        if not present(product.get(key)):
            errors.append(f"product.{key} is required")
    if product.get("maturity") not in {"production_candidate", "released"}:
        errors.append("suite release gate only accepts production_candidate or released maturity")

    scope = data.get("scope")
    if not isinstance(scope, dict):
        errors.append("scope must be an object")
        scope = {}
    for flag in SCOPED_DOMAINS:
        if not isinstance(scope.get(flag), bool):
            errors.append(f"scope.{flag} must be boolean")
    required = required_domains(scope)

    children = data.get("domains")
    if not isinstance(children, list):
        errors.append("domains must be a list")
        children = []
    ids = [item.get("id") for item in children if isinstance(item, dict)]
    if len(ids) != len(set(ids)) or any(not present(item) for item in ids):
        errors.append("domain IDs must be present and unique")
    child_by_id = {item.get("id"): item for item in children if isinstance(item, dict)}
    missing = sorted(required - set(child_by_id))
    if missing:
        errors.append(f"required suite domains are absent: {missing}")

    root = Path(release_root)
    passed = 0
    for index, child in enumerate(children):
        if not isinstance(child, dict):
            errors.append(f"domains[{index}] must be an object")
            continue
        domain_id = child.get("id")
        applicable = child.get("applicable")
        if not isinstance(applicable, bool):
            errors.append(f"domains[{index}].applicable must be boolean")
            continue
        if domain_id in required and not applicable:
            errors.append(f"required domain {domain_id} cannot be marked not applicable")
        if not applicable:
            waiver = child.get("waiver")
            if not isinstance(waiver, dict):
                errors.append(f"non-applicable domain {domain_id} requires a controlled waiver")
                continue
            for key in ("reason", "authority_role", "approval_date", "configuration", "evidence_sha256"):
                if not present(waiver.get(key)):
                    errors.append(f"domain {domain_id} waiver.{key} is required")
            if waiver.get("authority_role") != product.get("acceptance_authority_role"):
                errors.append(f"domain {domain_id} waiver authority is not the acceptance authority")
            if waiver.get("configuration") != product.get("configuration"):
                errors.append(f"domain {domain_id} waiver configuration mismatch")
            if not iso_date(waiver.get("approval_date")):
                errors.append(f"domain {domain_id} waiver approval_date must be ISO")
            if present(waiver.get("evidence_sha256")) and not HASH.fullmatch(str(waiver["evidence_sha256"])):
                errors.append(f"domain {domain_id} waiver evidence must be a SHA-256")
            continue

        contract = load_bound_file(root, child, "contract", errors)
        report = load_bound_file(root, child, "report", errors)
        if contract is None or report is None:
            continue
        contract_hash = child.get("contract_sha256")
        if report.get("contract_sha256") != contract_hash:
            errors.append(f"domain {domain_id} report is not bound to its contract hash")
        if report.get("validator_id") != child.get("validator_id"):
            errors.append(f"domain {domain_id} validator identity mismatch")
        verdict = report.get("verdict", report.get("status"))
        if verdict != child.get("verdict"):
            errors.append(f"domain {domain_id} declared verdict differs from report")
        if verdict not in PASSING:
            errors.append(f"domain {domain_id} has non-passing verdict {verdict!r}")
        identity_scope = child.get("identity_scope")
        if identity_scope not in {"product", "component"}:
            errors.append(f"domain {domain_id} identity_scope is invalid")
        report_identity = report.get("product")
        if identity_scope == "product":
            if not isinstance(report_identity, dict):
                errors.append(f"domain {domain_id} report lacks product identity")
            else:
                for key in ("part_number", "revision", "configuration"):
                    if report_identity.get(key) != product.get(key):
                        errors.append(f"domain {domain_id} {key} does not match suite product")
        if verdict in PASSING:
            passed += 1

    derivatives = data.get("derivatives")
    if not isinstance(derivatives, list) or not derivatives:
        errors.append("derivatives must contain controlled lineage records")
        derivatives = []
    for index, item in enumerate(derivatives):
        if not isinstance(item, dict):
            errors.append(f"derivatives[{index}] must be an object")
            continue
        for key in (
            "path", "sha256", "artifact_type", "derived_from_sha256",
            "configuration", "generator", "generator_version", "generation_record_sha256",
        ):
            if not present(item.get(key)):
                errors.append(f"derivatives[{index}].{key} is required")
        for key in ("sha256", "derived_from_sha256", "generation_record_sha256"):
            if present(item.get(key)) and not HASH.fullmatch(str(item[key])):
                errors.append(f"derivatives[{index}].{key} must be a SHA-256")
        if item.get("configuration") != product.get("configuration"):
            errors.append(f"derivatives[{index}] configuration mismatch")
        relative = Path(str(item.get("path", "")))
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"derivatives[{index}] has unsafe path")
        else:
            path = root / relative
            if not path.is_file():
                errors.append(f"derivatives[{index}] file is missing")
            elif digest(path) != str(item.get("sha256", "")).lower():
                errors.append(f"derivatives[{index}] file hash mismatch")

    approvals = data.get("approvals")
    if not isinstance(approvals, list):
        errors.append("approvals must be a list")
        approvals = []
    approved_roles = {
        item.get("role")
        for item in approvals
        if isinstance(item, dict)
        and item.get("decision") == "approved"
        and item.get("configuration") == product.get("configuration")
        and iso_date(item.get("date"))
    }
    required_roles = {
        product.get("acceptance_authority_role"),
        "quality authority",
        "manufacturing authority",
    }
    if not required_roles.issubset(approved_roles):
        errors.append(f"approvals lack configured roles {sorted(str(item) for item in required_roles)}")

    metrics["required_domain_count"] = len(required)
    metrics["passing_domain_count"] = passed
    metrics["derivative_count"] = len(derivatives)
    if errors:
        verdict = "FAIL"
    elif product.get("maturity") == "released":
        verdict = "RELEASED"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "product": product,
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    parser.add_argument("--release-root", required=True, type=Path)
    args = parser.parse_args()
    report = validate(
        json.loads(args.contract.read_text(encoding="utf-8")),
        args.release_root,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] in {"PASS", "RELEASED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
