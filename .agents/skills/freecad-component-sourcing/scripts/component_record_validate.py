#!/usr/bin/env python3
"""Validate a FreeCAD component provenance record.

This is a structural fail-closed check. It does not verify external truth,
dimensional accuracy, licensing, or engineering approval.
"""

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path


SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
CLASSES = {"standardized", "manufacturer_specific", "ecad"}
SOURCE_TYPES = {"manufacturer", "standard_generator", "supplier", "ecad", "curated_community", "uncontrolled_community"}
AUTHORITIES = {"reference", "envelope", "interface-verified", "release-candidate"}
APPROVALS = {"reference_only", "conditional", "approved_release_candidate", "rejected"}
REDISTRIBUTION = {"permitted", "conditional", "prohibited", "unresolved"}
SENTINELS = {"", "tbd", "unknown", "unassigned", "n/a", "na", "none", "null", "pending", "xxx", "?", "yyyy-mm-dd"}
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}


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
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def meaningful_list(value):
    if not isinstance(value, list) or not value:
        return False
    return all(
        (present(item) if not isinstance(item, dict) else any(present(v) for v in item.values()))
        for item in value
    )


def valid_iso_date(value):
    if not isinstance(value, str):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(data, source_file=None):
    errors = []
    warnings = []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["record root must be an object"], "warnings": []}
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    record_state = data.get("record_state")
    if record_state not in RECORD_STATES:
        errors.append(f"record_state must be one of {sorted(RECORD_STATES)}")

    for path in (
        "schema_version", "record_state", "component_id", "component_class", "description",
        "source.source_type", "source.publisher", "source.url_or_controlled_path",
        "source.accessed_at", "source.file_sha256", "source.license_or_terms_url",
        "source.redistribution", "geometry.units", "geometry.representation",
        "geometry.authority", "geometry.import_tool_and_version",
        "approval.status",
    ):
        if not present(get(data, path)):
            errors.append(f"missing controlled value: {path}")

    component_class = get(data, "component_class")
    if component_class not in CLASSES:
        errors.append(f"component_class must be one of {sorted(CLASSES)}")
    source_type = get(data, "source.source_type")
    if source_type not in SOURCE_TYPES:
        errors.append(f"source.source_type must be one of {sorted(SOURCE_TYPES)}")
    authority = get(data, "geometry.authority")
    if authority not in AUTHORITIES:
        errors.append(f"geometry.authority must be one of {sorted(AUTHORITIES)}")
    approval = get(data, "approval.status")
    if approval not in APPROVALS:
        errors.append(f"approval.status must be one of {sorted(APPROVALS)}")
    redistribution = get(data, "source.redistribution")
    if redistribution not in REDISTRIBUTION:
        errors.append(f"source.redistribution must be one of {sorted(REDISTRIBUTION)}")
    accessed_at = get(data, "source.accessed_at")
    if present(accessed_at) and not valid_iso_date(accessed_at):
        errors.append("source.accessed_at must be an ISO YYYY-MM-DD date")

    digest = get(data, "source.file_sha256")
    if present(digest) and not SHA256.fullmatch(str(digest)):
        errors.append("source.file_sha256 must be a 64-character hexadecimal SHA-256")

    if component_class == "standardized":
        for path in (
            "identity.standard_identifier", "identity.standard_edition",
            "identity.nominal_size", "identity.pitch", "identity.thread_tolerance",
            "identity.length", "identity.head_style", "identity.drive_style",
            "identity.material_or_property_class", "identity.finish",
        ):
            if not present(get(data, path)):
                errors.append(f"standardized component requires {path}")
    elif component_class == "manufacturer_specific":
        for path in (
            "identity.manufacturer", "identity.manufacturer_part_number",
            "identity.hardware_revision_or_variant", "source.document_number",
            "source.document_revision", "lifecycle_status",
        ):
            if not present(get(data, path)):
                errors.append(f"manufacturer-specific component requires {path}")
    elif component_class == "ecad":
        for path in (
            "ecad.project_or_board_id", "ecad.revision", "ecad.variant",
            "ecad.dnp_policy", "ecad.source_hash", "ecad.coordinate_transform",
        ):
            if not present(get(data, path)):
                errors.append(f"ECAD component requires {path}")
        ecad_hash = get(data, "ecad.source_hash")
        if present(ecad_hash) and not SHA256.fullmatch(str(ecad_hash)):
            errors.append("ecad.source_hash must be a 64-character hexadecimal SHA-256")
        absent_models = get(data, "ecad.absent_models")
        if not isinstance(absent_models, list):
            errors.append("ECAD component requires explicit ecad.absent_models list (empty only after checking)")
        transform = get(data, "ecad.coordinate_transform")
        if isinstance(transform, dict):
            for field in ("from_frame", "to_frame", "translation", "rotation"):
                if not present(transform.get(field)):
                    errors.append(f"ECAD coordinate_transform requires {field}")
        else:
            errors.append("ECAD coordinate_transform must be a structured object")

    release_claim = (
        record_state == "controlled_evidence"
        and (authority == "release-candidate" or approval == "approved_release_candidate")
    )
    evidence = get(data, "approval.evidence")
    verified = get(data, "geometry.verified_dimensions")
    if approval == "approved_release_candidate" and authority != "release-candidate":
        errors.append("approved_release_candidate requires geometry.authority release-candidate")
    if release_claim:
        if source_type in {"curated_community", "uncontrolled_community"}:
            errors.append("community source cannot be release-authoritative without a controlling manufacturer/standard/ECAD source")
        if redistribution == "conditional":
            exception = get(data, "source.redistribution_exception")
            if not isinstance(exception, dict) or not all(
                present(exception.get(key)) for key in ("scope", "approved_by", "date")
            ):
                errors.append("conditional redistribution requires exception scope, approved_by, and date")
            elif not valid_iso_date(exception.get("date")):
                errors.append("redistribution exception date must be ISO YYYY-MM-DD")
        elif redistribution != "permitted":
            errors.append("release candidate requires permitted redistribution or an approved conditional exception")
        if not meaningful_list(verified):
            errors.append("release candidate requires verified critical dimensions")
        else:
            for index, dimension in enumerate(verified):
                if not isinstance(dimension, dict):
                    errors.append(f"geometry.verified_dimensions[{index}] must be an object")
                    continue
                for key in (
                    "name", "nominal", "unit", "tolerance_plus", "tolerance_minus",
                    "measured", "method", "evidence_sha256",
                ):
                    if not present(dimension.get(key)):
                        errors.append(f"geometry.verified_dimensions[{index}].{key} is required")
                for key in ("nominal", "tolerance_plus", "tolerance_minus", "measured"):
                    if not finite(dimension.get(key)):
                        errors.append(f"geometry.verified_dimensions[{index}].{key} must be finite numeric")
                if present(dimension.get("evidence_sha256")) and not SHA256.fullmatch(str(dimension["evidence_sha256"])):
                    errors.append(f"geometry.verified_dimensions[{index}].evidence_sha256 must be a SHA-256")
        if not meaningful_list(evidence):
            errors.append("release candidate requires approval evidence")
        else:
            for index, item in enumerate(evidence):
                if not isinstance(item, dict) or not all(
                    present(item.get(key)) for key in ("id", "type", "sha256", "status")
                ):
                    errors.append(f"approval.evidence[{index}] requires id, type, sha256, and status")
                elif not SHA256.fullmatch(str(item.get("sha256"))):
                    errors.append(f"approval.evidence[{index}].sha256 must be a SHA-256")
                elif item.get("status") != "pass":
                    errors.append(f"approval.evidence[{index}].status must be pass")
        if not present(get(data, "approval.approver")) or not present(get(data, "approval.date")):
            errors.append("release candidate requires approver and approval date")
        if not valid_iso_date(get(data, "approval.date")):
            errors.append("approval.date must be an ISO date")
        if get(data, "approval.approver_role") != get(data, "approval.acceptance_authority_role"):
            errors.append("approval approver role must match acceptance authority")
        if get(data, "approval.configuration") != get(data, "configuration"):
            errors.append("approval configuration must match component configuration")
        mass = get(data, "geometry.mass_properties")
        if not isinstance(mass, dict):
            errors.append("release candidate requires geometry.mass_properties")
        else:
            for key in ("mass_kg", "center_of_gravity_mm", "inertia_kg_m2", "source_sha256"):
                if not present(mass.get(key)):
                    errors.append(f"geometry.mass_properties.{key} is required")
            if not finite(mass.get("mass_kg")) or mass.get("mass_kg", -1) <= 0:
                errors.append("geometry.mass_properties.mass_kg must be positive finite")
            for key in ("center_of_gravity_mm", "inertia_kg_m2"):
                values = mass.get(key)
                if not isinstance(values, list) or not values or any(not finite(value) for value in values):
                    errors.append(f"geometry.mass_properties.{key} must be finite numeric values")
            if present(mass.get("source_sha256")) and not SHA256.fullmatch(str(mass["source_sha256"])):
                errors.append("geometry.mass_properties.source_sha256 must be a SHA-256")

    if source_file:
        actual = hashlib.sha256(Path(source_file).read_bytes()).hexdigest()
        if str(digest).lower() != actual.lower():
            errors.append(f"source file SHA-256 mismatch: expected {digest}, got {actual}")
    elif release_claim:
        errors.append("release candidate requires --source-file for SHA-256 verification")
    elif present(digest):
        warnings.append("source file not supplied; recorded SHA-256 was syntax-checked only")

    controlling = get(data, "source.controlling_source_evidence")
    if source_type == "supplier" and authority in {"interface-verified", "release-candidate"}:
        if not meaningful_list(controlling):
            errors.append("supplier geometry above reference authority requires controlling manufacturer-drawing evidence")
    if source_type in {"curated_community", "uncontrolled_community"} and authority != "reference":
        warnings.append("non-primary source authority requires explicit controlling-drawing verification")

    if errors:
        verdict = "FAIL"
    elif record_state != "controlled_evidence":
        verdict = "DRAFT"
    elif approval == "approved_release_candidate":
        verdict = "PASS"
    else:
        verdict = "CONDITIONAL"
    return {"verdict": verdict, "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--source-file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = validate(json.loads(args.record.read_text(encoding="utf-8")), args.source_file)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
