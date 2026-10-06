#!/usr/bin/env python3
"""Regression tests for component_record_validate.py."""

import copy
import importlib.util
import json
import tempfile
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "component_validator", ROOT / "scripts" / "component_record_validate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def base_record():
    record = json.loads((ROOT / "assets" / "component-record.json").read_text())
    record.update({
        "record_state": "controlled_evidence",
        "component_id": "ISO4762-M3x12-8.8",
        "component_class": "standardized",
        "description": "M3 x 12 socket head cap screw",
    })
    record["identity"].update({
        "standard_identifier": "ISO 4762",
        "standard_edition": "2004",
        "nominal_size": "M3",
        "pitch": "0.5 mm",
        "thread_tolerance": "6g",
        "length": "12 mm",
        "head_style": "socket head cap",
        "drive_style": "hexagon socket",
        "material_or_property_class": "8.8",
        "finish": "zinc plated",
    })
    record["source"].update({
        "source_type": "standard_generator",
        "publisher": "FreeCAD Fasteners Workbench",
        "url_or_controlled_path": "controlled://ISO4762-M3x12",
        "document_number": "ISO 4762",
        "document_revision": "2004",
        "model_revision": "pinned-commit",
        "accessed_at": "2026-07-24",
        "file_sha256": hashlib.sha256(b"controlled geometry").hexdigest(),
        "license_or_terms_url": "https://example.invalid/terms",
        "redistribution": "permitted",
    })
    record["geometry"].update({
        "authority": "release-candidate",
        "import_tool_and_version": "FreeCAD 1.1.2 / pinned add-on",
        "verified_dimensions": [{
            "name": "head diameter", "nominal": 5.5, "unit": "mm",
            "tolerance_plus": 0.1, "tolerance_minus": -0.1, "measured": 5.5,
            "method": "controlled geometry interrogation", "evidence_sha256": "b" * 64,
        }],
        "mass_properties": {
            "mass_kg": 0.001, "center_of_gravity_mm": [0, 0, 6],
            "inertia_kg_m2": [1e-7, 1e-7, 1e-8], "source_sha256": "c" * 64,
        },
    })
    record["approval"].update({
        "status": "approved_release_candidate",
        "evidence": [{"id": "QC-001", "type": "dimensional", "sha256": "b" * 64, "status": "pass"}],
        "approver": "design authority",
        "approver_role": "design authority",
        "acceptance_authority_role": "design authority",
        "configuration": "BASE",
        "date": "2026-07-24",
    })
    return record


def expect(record, verdict, phrase=None, with_source=True):
    with tempfile.NamedTemporaryFile() as source:
        source.write(b"controlled geometry")
        source.flush()
        report = MODULE.validate(record, source.name if with_source else None)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in message for message in report["errors"]), report


valid = base_record()
expect(valid, "PASS")

for field in ("pitch", "length", "material_or_property_class", "head_style", "drive_style"):
    case = copy.deepcopy(valid)
    case["identity"][field] = "TBD"
    expect(case, "FAIL", field)

case = copy.deepcopy(valid)
case["source"]["redistribution"] = "prohibited"
expect(case, "FAIL", "permitted redistribution")

case = copy.deepcopy(valid)
case["geometry"]["authority"] = "reference"
expect(case, "FAIL", "requires geometry.authority")

case = copy.deepcopy(valid)
case["component_class"] = "manufacturer_specific"
case["identity"].update({
    "manufacturer": "Exact Manufacturer",
    "manufacturer_part_number": "EXACT-001",
    "hardware_revision_or_variant": "revision B",
})
case["source"].update({
    "source_type": "manufacturer",
    "document_number": "DWG-001",
    "document_revision": "B",
})
case["lifecycle_status"] = "active"
expect(case, "PASS")
case["lifecycle_status"] = "unknown"
expect(case, "FAIL", "lifecycle_status")

template = json.loads((ROOT / "assets" / "component-record.json").read_text())
expect(template, "FAIL", "component_id", with_source=False)

case = copy.deepcopy(valid)
expect(case, "FAIL", "--source-file", with_source=False)

case = copy.deepcopy(valid)
case["geometry"]["verified_dimensions"][0]["measured"] = float("nan")
expect(case, "FAIL", "must be finite")

case = copy.deepcopy(valid)
case["approval"]["evidence"] = ["QC-001"]
expect(case, "FAIL", "requires id, type")

case = copy.deepcopy(valid)
case["approval"]["approver_role"] = "drafter"
expect(case, "FAIL", "acceptance authority")

with tempfile.NamedTemporaryFile() as source:
    source.write(b"hash-case-test")
    source.flush()
    case = copy.deepcopy(valid)
    case["source"]["file_sha256"] = hashlib.sha256(b"hash-case-test").hexdigest().upper()
    report = MODULE.validate(case, source.name)
    assert report["verdict"] == "PASS", report

print("component validator regression tests: PASS")
