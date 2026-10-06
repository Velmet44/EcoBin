#!/usr/bin/env python3
"""Regression tests for interface_register_validate.py."""

import csv
import importlib.util
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "interface_validator", ROOT / "scripts" / "interface_register_validate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_row(row):
    handle = tempfile.NamedTemporaryFile(mode="w", newline="", suffix=".csv", delete=False)
    writer = csv.DictWriter(handle, fieldnames=MODULE.REQUIRED)
    writer.writeheader()
    writer.writerow(row)
    handle.close()
    return Path(handle.name)


base = {
    "interface_id": "IF-001",
    "configuration": "BASE",
    "occurrence_a": "OCC-001",
    "datum_a": "A",
    "occurrence_b": "OCC-002",
    "datum_b": "B",
    "function": "sliding clearance",
    "classification": "clearance",
    "standard_and_edition": "ISO 286-1:2010",
    "nominal_condition": "0.3 mm",
    "worst_case_min": "0.1 mm",
    "worst_case_max": "0.5 mm",
    "thermal_coating_load_basis": "-20 to 60 C; coated",
    "inspection_method": "CMM",
    "test_case": "TEST-001",
    "status": "pass",
    "evidence": "fit-report.json",
}

path = write_row(base)
assert MODULE.validate(path, release=True)["verdict"] == "PASS"

case = dict(base)
case["worst_case_min"] = "TBD"
path = write_row(case)
assert MODULE.validate(path, release=True)["verdict"] == "FAIL"

case = dict(base)
case["classification"] = "looks okay"
path = write_row(case)
assert MODULE.validate(path, release=True)["verdict"] == "FAIL"

case = dict(base)
case["status"] = "planned"
path = write_row(case)
assert MODULE.validate(path, release=True)["verdict"] == "FAIL"

print("interface register validator regression tests: PASS")
