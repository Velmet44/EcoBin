"""Run non-destructive FreeCAD parameter cases from fresh document loads.

Case file example:
{
  "coverage": {
    "kind": "finite_exhaustive",
    "definition": "Every member of approved size set 80, 100, 120 mm",
    "declared_case_names": ["size-80", "size-100", "size-120"]
  },
  "cases": [
    {
      "name": "size-80",
      "case_type": "release",
      "set": {"Parameters.B2": "80 mm"},
      "expected": {
        "audit_status": "PASS",
        "body_count": 1,
        "sketch_count": 6,
        "target": {
          "solid_count": 1,
          "volume_mm3": {"min": 1000, "max": 50000},
          "bounding_box_mm": {"x_length": {"equals": 80, "tolerance": 0.001}}
        }
      }
    }
  ]
}

For Spreadsheet objects, the segment after the dot is a cell address. For other
objects it is a direct property name. The source FCStd is never saved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import FreeCAD as App
except ImportError:  # Allows schema/unit tests outside a FreeCAD runtime.
    App = None

try:
    from freecad_model_audit import audit_document, file_sha256, software_versions
except ImportError:  # Loaded lazily by the FreeCAD CLI in production.
    audit_document = file_sha256 = software_versions = None


def script_argv() -> list[str]:
    args = sys.argv[1:]
    return args[args.index("--pass") + 1 :] if "--pass" in args else args


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Source FCStd")
    parser.add_argument("--cases", required=True, help="JSON case file")
    parser.add_argument(
        "--target", action="append", default=[], help="Object name/label"
    )
    parser.add_argument("--output", required=True, help="JSON report")
    parser.add_argument("--allow-multi-solid", action="store_true")
    parser.add_argument("--allow-under-constrained", action="store_true")
    parser.add_argument("--allow-under-constrained-sketch", action="append", default=[])
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing sweep report"
    )
    return parser.parse_args(script_argv())


def load_cases(path: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list) or not cases:
        raise ValueError("Case file must contain a non-empty 'cases' array")
    names = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("name"), str):
            raise ValueError("Each case needs a string 'name'")
        if case["name"] in names:
            raise ValueError(f"Duplicate case name: {case['name']!r}")
        names.add(case["name"])
        if case.get("case_type") not in {"release", "negative_regression"}:
            raise ValueError(
                f"Case {case['name']!r} needs case_type release or negative_regression"
            )
        if not isinstance(case.get("set"), dict) or not case.get("set"):
            raise ValueError(f"Case {case['name']!r} has invalid 'set' mapping")
        if not isinstance(case.get("expected"), dict) or not case.get("expected"):
            raise ValueError(f"Case {case['name']!r} has invalid 'expected' mapping")
        if case["case_type"] == "release":
            expected = case["expected"]
            if "audit_status" not in expected:
                raise ValueError(
                    f"Release case {case['name']!r} requires expected.audit_status"
                )
            target = expected.get("target")
            critical = {
                "solid_count", "volume_mm3", "area_mm2", "bounding_box_mm"
            }
            if not isinstance(target, dict) or not critical.intersection(target):
                raise ValueError(
                    f"Release case {case['name']!r} requires quantitative target assertions"
                )
    coverage = data.get("coverage", {})
    if not isinstance(coverage, dict):
        raise ValueError("'coverage' must be an object")
    kind = coverage.get("kind")
    if kind not in {"finite_exhaustive", "sampled"}:
        raise ValueError(
            "coverage.kind must be finite_exhaustive or sampled"
        )
    if not isinstance(coverage.get("definition"), str) or not coverage["definition"].strip():
        raise ValueError("coverage.definition must be a controlled non-empty statement")
    release_names = {
        case["name"] for case in cases if case["case_type"] == "release"
    }
    if not release_names:
        raise ValueError("At least one release case is required")
    if kind == "finite_exhaustive":
        declared = coverage.get("declared_case_names")
        if not isinstance(declared, list) or set(declared) != release_names or len(declared) != len(release_names):
            raise ValueError(
                "finite_exhaustive declared_case_names must exactly match release cases"
            )
    else:
        for field in ("sampling_method", "seed", "domain", "limitations"):
            if field not in coverage or coverage[field] in (None, "", [], {}):
                raise ValueError(f"sampled coverage requires coverage.{field}")
        if not isinstance(coverage.get("seed"), int) or isinstance(coverage.get("seed"), bool):
            raise ValueError("coverage.seed must be an integer")
    return cases, coverage


def set_value(doc: Any, path: str, value: Any) -> None:
    if "." not in path:
        raise ValueError(f"Set path must be Object.Property or Sheet.Cell: {path!r}")
    object_name, field = path.split(".", 1)
    obj = doc.getObject(object_name)
    if obj is None:
        labels = doc.getObjectsByLabel(object_name)
        if len(labels) == 1:
            obj = labels[0]
    if obj is None:
        raise ValueError(f"Object not found for set path: {path!r}")
    if obj.TypeId == "Spreadsheet::Sheet":
        obj.set(field, str(value))
        return
    if field not in obj.PropertiesList:
        raise ValueError(f"Property not found for set path: {path!r}")
    setattr(obj, field, value)


def check_numeric(label: str, actual: float, specification: Any) -> list[str]:
    if not isinstance(specification, dict):
        return [f"{label} expectation must be an object"]
    failures = []
    if "min" in specification and actual < float(specification["min"]):
        failures.append(f"{label}={actual} below {specification['min']}")
    if "max" in specification and actual > float(specification["max"]):
        failures.append(f"{label}={actual} above {specification['max']}")
    if "equals" in specification:
        tolerance = float(specification.get("tolerance", 0.0))
        delta = abs(actual - float(specification["equals"]))
        if delta > tolerance:
            failures.append(
                f"{label}={actual} differs from {specification['equals']} "
                f"by {delta} (tolerance {tolerance})"
            )
    if not {"min", "max", "equals"}.intersection(specification):
        failures.append(f"{label} expectation has no min, max, or equals")
    return failures


def expected_failures(report: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    failures = []
    expected_status = str(expected.get("audit_status", "PASS")).upper()
    if report["status"] != expected_status:
        failures.append(
            f"audit status {report['status']} does not equal {expected_status}"
        )
    for key in ("body_count", "sketch_count", "object_count"):
        if key in expected and report["document"][key] != int(expected[key]):
            failures.append(
                f"{key}={report['document'][key]} does not equal {expected[key]}"
            )
    required = expected.get("required_object_names", [])
    existing = {item["name"] for item in report["objects"]}
    for name in required:
        if name not in existing:
            failures.append(f"required object is absent: {name}")

    target_spec = expected.get("target")
    if target_spec is not None:
        if not report["targets"]:
            failures.append("target expectations provided but no target was audited")
            return failures
        target = report["targets"][0]
        for key in (
            "solid_count",
            "shell_count",
            "face_count",
            "edge_count",
            "vertex_count",
        ):
            if key in target_spec and target[key] != int(target_spec[key]):
                failures.append(
                    f"target {key}={target[key]} does not equal {target_spec[key]}"
                )
        if "volume_mm3" in target_spec:
            failures.extend(
                check_numeric(
                    "target volume_mm3",
                    target["volume_mm3"],
                    target_spec["volume_mm3"],
                )
            )
        if "area_mm2" in target_spec:
            failures.extend(
                check_numeric(
                    "target area_mm2", target["area_mm2"], target_spec["area_mm2"]
                )
            )
        for axis, specification in target_spec.get("bounding_box_mm", {}).items():
            bbox = target["bounding_box_mm"]
            if bbox is None or axis not in bbox:
                failures.append(f"target bounding-box value is absent: {axis}")
            else:
                failures.extend(
                    check_numeric(
                        f"target bounding_box_mm.{axis}", bbox[axis], specification
                    )
                )
    return failures


def write_checkpoint(
    path: Path,
    source: str,
    source_sha256: str,
    coverage: dict[str, Any],
    case_count: int,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    failed = sum(result["status"] != "PASS" for result in results)
    completed = len(results) >= case_count
    if not completed:
        overall_status = "IN_PROGRESS"
    elif failed:
        overall_status = "FAIL"
    elif coverage.get("kind") == "finite_exhaustive":
        overall_status = "FINITE_EXHAUSTIVE_PASS"
    else:
        overall_status = "SAMPLED_PASS"
    payload = {
        "status": overall_status,
        "source": source,
        "source_sha256": source_sha256,
        "software": software_versions() if software_versions is not None else {
            "runtime": "schema-test-only"
        },
        "coverage": coverage,
        "case_count": case_count,
        "completed_case_count": len(results),
        "failed_case_count": failed,
        "cases": results,
        "limitations": [
            "Finite enumerated cases can be exhaustive only for the declared set.",
            "A sampled continuous range is not proof for every real-valued input.",
            "Cases validate stated assertions, not semantic feature identity.",
            "Visually review topology-changing cases and manufacturing constraints.",
        ],
    }
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def main() -> int:
    args = parse_args()
    try:
        if App is None or any(
            item is None for item in (audit_document, file_sha256, software_versions)
        ):
            raise RuntimeError("run this script inside the supported FreeCAD runtime")
        input_path = str(Path(args.input).expanduser().resolve())
        cases, coverage = load_cases(args.cases)
        output_path = Path(args.output).expanduser().resolve()
        if output_path.exists() and not args.force:
            raise ValueError(f"output exists; pass --force to replace: {output_path}")
        source_sha256 = file_sha256(input_path)
    except Exception as exc:
        print(f"sweep setup error: {exc}", file=sys.stderr)
        return 3

    results = []
    for case in cases:
        doc = None
        try:
            doc = App.openDocument(input_path)
            for path, value in case.get("set", {}).items():
                set_value(doc, path, value)
            report = audit_document(
                doc,
                target_names=args.target,
                allow_multi_solid=args.allow_multi_solid,
                allow_under_constrained=args.allow_under_constrained,
                allowed_under_constrained_names=args.allow_under_constrained_sketch,
            )
            assertions = expected_failures(report, case.get("expected", {}))
            case_result = {
                "name": case["name"],
                "set": case.get("set", {}),
                "expected": case.get("expected", {}),
                "status": "PASS" if not assertions else "FAIL",
                "audit_status": report["status"],
                "audit_failure_count": report["failure_count"],
                "assertion_failures": assertions,
                "document": report["document"],
                "targets": report["targets"],
                "failures": report["failures"],
            }
        except Exception as exc:
            case_result = {
                "name": case["name"],
                "set": case.get("set", {}),
                "status": "ERROR",
                "error": str(exc),
            }
        finally:
            if doc is not None:
                App.closeDocument(doc.Name)
        results.append(case_result)
        try:
            payload = write_checkpoint(
                output_path,
                input_path,
                source_sha256,
                coverage,
                len(cases),
                results,
            )
        except OSError as exc:
            print(f"sweep output error: {exc}", file=sys.stderr)
            return 3

    failed = payload["failed_case_count"]
    print(f"{payload['status']}: {failed}/{len(cases)} case(s) failed; {output_path}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
