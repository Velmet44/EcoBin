"""Audit a FreeCAD document without modifying or saving it.

Execute with FreeCADCmd. The script checks recompute/object states, sketches,
release targets, and optional envelope expectations. Run the GUI Check Geometry
with BOP enabled as an additional release step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

import FreeCAD as App


def software_versions() -> dict[str, Any]:
    return {
        "freecad": list(App.Version()),
        "opencascade": App.ConfigGet("OCC_VERSION_COMPLETE")
        or App.ConfigGet("OCC_VERSION"),
    }


def object_states(doc: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    objects = []
    failures = []
    for obj in doc.Objects:
        states = [str(item) for item in getattr(obj, "State", [])]
        item = {
            "name": obj.Name,
            "label": obj.Label,
            "type_id": obj.TypeId,
            "state": states,
        }
        objects.append(item)
        if any(state.lower() in {"invalid", "error"} for state in states):
            failures.append(item)
    return objects, failures


def file_sha256(path: str | Path) -> str:
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def sketch_report(
    doc: Any,
    allow_under_constrained: bool,
    allowed_under_constrained_names: Iterable[str] = (),
) -> tuple[list, list]:
    sketches = []
    failures = []
    allowed = set(allowed_under_constrained_names)
    for obj in doc.Objects:
        if not obj.isDerivedFrom("Sketcher::SketchObject"):
            continue
        solve_status = int(obj.solve())
        fully_constrained = bool(getattr(obj, "FullyConstrained", False))
        dof = int(obj.getLastDoF()) if hasattr(obj, "getLastDoF") else None
        external_count = (
            int(obj.getExternalGeometryCount())
            if hasattr(obj, "getExternalGeometryCount")
            else None
        )
        item = {
            "name": obj.Name,
            "label": obj.Label,
            "solve_status": solve_status,
            "fully_constrained": fully_constrained,
            "degrees_of_freedom": dof,
            "external_geometry_count": external_count,
        }
        sketches.append(item)
        reasons = []
        if solve_status != 0:
            reasons.append(f"solver status {solve_status}")
        named_exception = obj.Name in allowed or obj.Label in allowed
        if (
            not fully_constrained
            and not allow_under_constrained
            and not named_exception
        ):
            reasons.append(f"under-constrained ({dof} DoF)")
        if reasons:
            failures.append({"object": obj.Name, "reasons": reasons})
    return sketches, failures


def dependency_cycles(doc: Any) -> list[list[str]]:
    graph = {
        obj.Name: [
            linked.Name
            for linked in getattr(obj, "OutList", [])
            if hasattr(linked, "Name")
        ]
        for obj in doc.Objects
    }
    cycles: list[list[str]] = []
    visiting: list[str] = []
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visiting:
            start = visiting.index(name)
            cycle = visiting[start:] + [name]
            if cycle not in cycles:
                cycles.append(cycle)
            return
        if name in visited:
            return
        visiting.append(name)
        for linked in graph.get(name, []):
            visit(linked)
        visiting.pop()
        visited.add(name)

    for object_name in graph:
        visit(object_name)
    return cycles


def resolve_targets(doc: Any, names: Iterable[str]) -> list[Any]:
    requested = list(names)
    if requested:
        targets = []
        for name in requested:
            obj = doc.getObject(name)
            if obj is None:
                labels = doc.getObjectsByLabel(name)
                if len(labels) == 1:
                    obj = labels[0]
                elif len(labels) > 1:
                    raise ValueError(f"Target label is ambiguous: {name!r}")
            if obj is None:
                raise ValueError(f"Target not found: {name!r}")
            targets.append(obj)
        return targets

    bodies = [
        obj
        for obj in doc.Objects
        if obj.isDerivedFrom("PartDesign::Body")
        and hasattr(obj, "Shape")
        and not obj.Shape.isNull()
    ]
    if bodies:
        return bodies

    final_shapes = []
    for obj in doc.Objects:
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue
        if len(getattr(obj.Shape, "Solids", [])) == 0:
            continue
        if len(getattr(obj, "InList", [])) == 0:
            final_shapes.append(obj)
    if final_shapes:
        return final_shapes
    raise ValueError("No release target found; pass --target explicitly")


def shape_report(obj: Any, allow_multi_solid: bool) -> tuple[dict, list[str]]:
    shape = obj.Shape
    reasons = []
    null = bool(shape.isNull())
    valid = False if null else bool(shape.isValid())
    solids = [] if null else list(shape.Solids)
    shells = [] if null else list(shape.Shells)
    closed = False if null else bool(shape.isClosed())
    volume = 0.0 if null else float(shape.Volume)
    area = 0.0 if null else float(shape.Area)

    if null:
        reasons.append("null shape")
    if not valid:
        reasons.append("invalid B-rep")
    if not allow_multi_solid and len(solids) != 1:
        reasons.append(f"expected one solid, found {len(solids)}")
    if len(solids) > 0 and not closed:
        reasons.append("shape containing solids is not closed")
    if volume <= 0:
        reasons.append("non-positive volume")

    if null:
        bbox = center = placement = None
    else:
        box = shape.BoundBox
        com = shape.CenterOfMass
        bbox = {
            "xmin": float(box.XMin),
            "ymin": float(box.YMin),
            "zmin": float(box.ZMin),
            "x_length": float(box.XLength),
            "y_length": float(box.YLength),
            "z_length": float(box.ZLength),
        }
        center = {"x": float(com.x), "y": float(com.y), "z": float(com.z)}
        base = obj.Placement.Base
        placement = {
            "base_mm": {
                "x": float(base.x),
                "y": float(base.y),
                "z": float(base.z),
            },
            "rotation_quaternion": list(obj.Placement.Rotation.Q),
        }

    item = {
        "name": obj.Name,
        "label": obj.Label,
        "type_id": obj.TypeId,
        "shape_type": None if null else shape.ShapeType,
        "is_null": null,
        "is_valid": valid,
        "is_closed": closed,
        "solid_count": len(solids),
        "shell_count": len(shells),
        "face_count": 0 if null else len(shape.Faces),
        "edge_count": 0 if null else len(shape.Edges),
        "vertex_count": 0 if null else len(shape.Vertexes),
        "volume_mm3": volume,
        "area_mm2": area,
        "bounding_box_mm": bbox,
        "center_of_mass_mm": center,
        "placement": placement,
        "manual_bop_check_required": True,
    }
    return item, reasons


def audit_document(
    doc: Any,
    target_names: Iterable[str] = (),
    allow_multi_solid: bool = False,
    allow_under_constrained: bool = False,
    allowed_under_constrained_names: Iterable[str] = (),
    expected_body_count: int | None = None,
    expected_sketch_count: int | None = None,
    expected_volume_min: float | None = None,
    expected_volume_max: float | None = None,
    expected_bbox: list[float] | None = None,
    bbox_tolerance: float = 0.0,
) -> dict[str, Any]:
    recompute_result = doc.recompute()
    objects, state_failures = object_states(doc)
    sketches, sketch_failures = sketch_report(
        doc, allow_under_constrained, allowed_under_constrained_names
    )
    bodies = [obj for obj in doc.Objects if obj.isDerivedFrom("PartDesign::Body")]
    count_failures = []
    if recompute_result is False:
        count_failures.append("document recompute returned False")
    if expected_body_count is not None and len(bodies) != expected_body_count:
        count_failures.append(
            f"expected {expected_body_count} Body object(s), found {len(bodies)}"
        )
    if expected_sketch_count is not None and len(sketches) != expected_sketch_count:
        count_failures.append(
            f"expected {expected_sketch_count} sketch(es), found {len(sketches)}"
        )
    cycles = dependency_cycles(doc)
    dependency_failures = [
        {"cycle": cycle, "reason": "cyclic document dependency"} for cycle in cycles
    ]
    targets = resolve_targets(doc, target_names)
    target_reports = []
    target_failures = []
    for obj in targets:
        item, reasons = shape_report(obj, allow_multi_solid)
        target_reports.append(item)
        if expected_volume_min is not None and item["volume_mm3"] < expected_volume_min:
            reasons.append(
                f"volume {item['volume_mm3']} below {expected_volume_min} mm^3"
            )
        if expected_volume_max is not None and item["volume_mm3"] > expected_volume_max:
            reasons.append(
                f"volume {item['volume_mm3']} above {expected_volume_max} mm^3"
            )
        if expected_bbox is not None:
            actual = item["bounding_box_mm"]
            if actual is None:
                reasons.append("cannot compare bounding box of null shape")
            else:
                for axis, expected in zip(
                    ("x_length", "y_length", "z_length"), expected_bbox
                ):
                    delta = abs(actual[axis] - expected)
                    if delta > bbox_tolerance:
                        reasons.append(
                            f"{axis}={actual[axis]} differs from {expected} "
                            f"by {delta} mm (tolerance {bbox_tolerance})"
                        )
        if reasons:
            target_failures.append({"object": obj.Name, "reasons": reasons})

    failures = {
        "document": count_failures,
        "dependencies": dependency_failures,
        "object_states": state_failures,
        "sketches": sketch_failures,
        "targets": target_failures,
    }
    failure_count = sum(len(items) for items in failures.values())
    return {
        "status": "PASS" if failure_count == 0 else "FAIL",
        "failure_count": failure_count,
        "software": software_versions(),
        "document": {
            "name": doc.Name,
            "label": doc.Label,
            "file": doc.FileName,
            "object_count": len(doc.Objects),
            "body_count": len(bodies),
            "sketch_count": len(sketches),
            "recompute_result": recompute_result,
        },
        "dependency_cycles": cycles,
        "objects": objects,
        "sketches": sketches,
        "targets": target_reports,
        "failures": failures,
        "limitations": [
            "Run GUI Part Check Geometry with BOP check for final release.",
            "Semantic feature intent and topological-reference correctness need review.",
            "Geometry checks do not prove strength, tolerance, DFM, or compliance.",
        ],
    }


def script_argv() -> list[str]:
    args = sys.argv[1:]
    return args[args.index("--pass") + 1 :] if "--pass" in args else args


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="FCStd document")
    parser.add_argument(
        "--target", action="append", default=[], help="Object name/label"
    )
    parser.add_argument("--output", required=True, help="JSON report")
    parser.add_argument("--allow-multi-solid", action="store_true")
    parser.add_argument("--allow-under-constrained", action="store_true")
    parser.add_argument(
        "--allow-under-constrained-sketch",
        action="append",
        default=[],
        help="Approved under-constrained sketch name/unique label",
    )
    parser.add_argument("--expected-body-count", type=int)
    parser.add_argument("--expected-sketch-count", type=int)
    parser.add_argument("--expected-volume-min", type=float)
    parser.add_argument("--expected-volume-max", type=float)
    parser.add_argument(
        "--expected-bbox",
        type=float,
        nargs=3,
        metavar=("X", "Y", "Z"),
        help="Expected target bounding-box lengths in mm",
    )
    parser.add_argument("--bbox-tolerance", type=float, default=0.0)
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing audit report"
    )
    return parser.parse_args(script_argv())


def main() -> int:
    args = parse_args()
    doc = None
    try:
        input_path = str(Path(args.input).expanduser().resolve())
        output_path = Path(args.output).expanduser().resolve()
        if output_path.exists() and not args.force:
            raise ValueError(f"output exists; pass --force to replace: {output_path}")
        doc = App.openDocument(input_path)
        report = audit_document(
            doc,
            target_names=args.target,
            allow_multi_solid=args.allow_multi_solid,
            allow_under_constrained=args.allow_under_constrained,
            allowed_under_constrained_names=args.allow_under_constrained_sketch,
            expected_body_count=args.expected_body_count,
            expected_sketch_count=args.expected_sketch_count,
            expected_volume_min=args.expected_volume_min,
            expected_volume_max=args.expected_volume_max,
            expected_bbox=args.expected_bbox,
            bbox_tolerance=args.bbox_tolerance,
        )
        report["source_sha256"] = file_sha256(input_path)
        output_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(
            f"{report['status']}: {report['failure_count']} failure(s); "
            f"report={output_path}"
        )
        return 0 if report["status"] == "PASS" else 2
    except Exception as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 3
    finally:
        if doc is not None:
            App.closeDocument(doc.Name)


if __name__ == "__main__":
    raise SystemExit(main())
