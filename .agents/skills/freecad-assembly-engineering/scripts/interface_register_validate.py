#!/usr/bin/env python3
"""Validate and reconcile the assembly interface/fit CSV.

The script checks controlled fields and references. It does not calculate a
tolerance stack or verify that recorded evidence is true.
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


REQUIRED = (
    "interface_id", "configuration", "occurrence_a", "datum_a",
    "occurrence_b", "datum_b", "function", "classification",
    "standard_and_edition", "nominal_condition", "worst_case_min",
    "worst_case_max", "thermal_coating_load_basis", "inspection_method",
    "test_case", "status", "evidence",
)
CLASSIFICATIONS = {
    "forbidden_interference", "intentional_contact", "clearance",
    "transition", "interference", "flexible_envelope",
}
LENGTH = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)\s*(?:mm|in|µm|um)$")
SENTINELS = {"", "tbd", "unknown", "n/a", "none", "pending", "open"}


def present(value):
    return isinstance(value, str) and value.strip().lower() not in SENTINELS


def validate(path, contract=None, release=False):
    errors = []
    rows = []
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing_columns = [name for name in REQUIRED if name not in (reader.fieldnames or [])]
        if missing_columns:
            errors.append(f"missing CSV columns: {missing_columns}")
        rows = list(reader)

    ids = []
    known_configs = known_occurrences = known_tests = None
    if contract:
        data = json.loads(Path(contract).read_text(encoding="utf-8"))
        known_configs = {item.get("id") for item in data.get("configurations", [])}
        known_occurrences = {item.get("occurrence_id") for item in data.get("occurrences", [])}
        known_tests = {item.get("id") for item in data.get("test_cases", [])}

    for index, row in enumerate(rows, start=2):
        ids.append(row.get("interface_id"))
        for field in REQUIRED:
            if not present(row.get(field)):
                errors.append(f"row {index}: {field} is not controlled")
        if row.get("classification") not in CLASSIFICATIONS:
            errors.append(f"row {index}: invalid classification {row.get('classification')!r}")
        for field in ("worst_case_min", "worst_case_max"):
            value = (row.get(field) or "").strip()
            if present(value) and not LENGTH.fullmatch(value):
                errors.append(f"row {index}: {field} must be a signed value with mm, µm/um, or in")
        if release and row.get("status") != "pass":
            errors.append(f"row {index}: release interface status must be pass")
        if known_configs is not None and row.get("configuration") not in known_configs:
            errors.append(f"row {index}: unknown configuration {row.get('configuration')!r}")
        if known_occurrences is not None:
            for field in ("occurrence_a", "occurrence_b"):
                if row.get(field) not in known_occurrences:
                    errors.append(f"row {index}: {field} references unknown occurrence")
        if known_tests is not None and row.get("test_case") not in known_tests:
            errors.append(f"row {index}: test_case references unknown test")

    duplicates = sorted({item for item in ids if item and ids.count(item) > 1})
    if duplicates:
        errors.append(f"duplicate interface IDs: {duplicates}")
    if release and not rows:
        errors.append("release interface register must contain at least one row")

    return {"verdict": "PASS" if not errors else "FAIL", "rows": len(rows), "errors": errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("register", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(args.register, args.contract, args.release)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
