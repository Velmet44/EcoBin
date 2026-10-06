#!/usr/bin/env python3
"""Schema and coverage regression tests that do not require FreeCAD."""

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sweep", ROOT / "scripts" / "freecad_parameter_sweep.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def release_case(name="size-80"):
    return {
        "name": name,
        "case_type": "release",
        "set": {"Parameters.B2": "80 mm"},
        "expected": {
            "audit_status": "PASS",
            "target": {"solid_count": 1, "volume_mm3": {"min": 1000}},
        },
    }


def write(payload):
    handle, name = tempfile.mkstemp(suffix=".json")
    Path(name).write_text(json.dumps(payload), encoding="utf-8")
    return Path(name)


def expect_error(payload, phrase):
    try:
        MODULE.load_cases(str(write(payload)))
    except ValueError as exc:
        assert phrase in str(exc), exc
    else:
        raise AssertionError(f"expected error containing {phrase!r}")


finite = {
    "coverage": {
        "kind": "finite_exhaustive",
        "definition": "all approved sizes",
        "declared_case_names": ["size-80"],
    },
    "cases": [release_case()],
}
cases, coverage = MODULE.load_cases(str(write(finite)))
assert len(cases) == 1 and coverage["kind"] == "finite_exhaustive"

bad = json.loads(json.dumps(finite))
bad["coverage"]["declared_case_names"] = ["invented"]
expect_error(bad, "exactly match")
bad = json.loads(json.dumps(finite))
bad["cases"][0]["set"] = {}
expect_error(bad, "set")
bad = json.loads(json.dumps(finite))
bad["cases"][0]["expected"]["target"] = {}
expect_error(bad, "quantitative")
bad = json.loads(json.dumps(finite))
bad["coverage"]["kind"] = "sampled"
expect_error(bad, "sampling_method")

sampled = {
    "coverage": {
        "kind": "sampled",
        "definition": "Latin-hypercube sample; not exhaustive",
        "sampling_method": "Latin hypercube",
        "seed": 42,
        "domain": {"width_mm": [80, 120]},
        "limitations": ["continuous values between samples are not proven"],
    },
    "cases": [release_case("sample-001")],
}
MODULE.load_cases(str(write(sampled)))

with tempfile.TemporaryDirectory() as directory:
    output = Path(directory) / "report.json"
    result = [{"name": "size-80", "status": "PASS"}]
    report = MODULE.write_checkpoint(
        output, "part.FCStd", "a" * 64, finite["coverage"], 1, result
    )
    assert report["status"] == "FINITE_EXHAUSTIVE_PASS"
    report = MODULE.write_checkpoint(
        output, "part.FCStd", "a" * 64, sampled["coverage"], 1, result
    )
    assert report["status"] == "SAMPLED_PASS"
    report = MODULE.write_checkpoint(
        output, "part.FCStd", "a" * 64, sampled["coverage"], 1,
        [{"name": "sample-001", "status": "FAIL"}],
    )
    assert report["status"] == "FAIL"

print("parameter sweep coverage regression tests: PASS")
