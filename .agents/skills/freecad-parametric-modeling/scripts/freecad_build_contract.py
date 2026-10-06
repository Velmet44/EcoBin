"""Reusable assertions for FreeCAD part-generation scripts.

Import this module from a script executed by FreeCAD/FreeCADCmd. It deliberately
contains no GUI dependency and never saves a document on its own.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import FreeCAD as App


class BuildContractError(RuntimeError):
    """Raised when a model violates a deterministic build requirement."""


def quantity(value: str) -> Any:
    """Parse a unit-bearing FreeCAD quantity and reject dimensionless input."""
    if not isinstance(value, str) or not value.strip():
        raise BuildContractError(f"Expected a unit-bearing string, got {value!r}")
    if not any(character.isalpha() or character in "°'\"" for character in value):
        raise BuildContractError(f"Quantity must include an explicit unit: {value!r}")
    parsed = App.Units.Quantity(value)
    return parsed


def require_keys(data: Mapping[str, Any], keys: Iterable[str], context: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise BuildContractError(f"{context} is missing required keys: {missing}")


def require_positive(value: Any, name: str) -> None:
    numeric = float(getattr(value, "Value", value))
    if numeric <= 0:
        raise BuildContractError(f"{name} must be positive, got {value!r}")


def recompute_or_raise(doc: Any, phase: str) -> None:
    """Recompute and fail when document objects expose invalid/error states."""
    doc.recompute()
    failures = []
    for obj in doc.Objects:
        states = [str(item) for item in getattr(obj, "State", [])]
        if any(item.lower() in {"invalid", "error"} for item in states):
            failures.append({"object": obj.Name, "label": obj.Label, "state": states})
    if failures:
        raise BuildContractError(f"{phase}: object failures: {failures}")


def assert_fully_constrained(sketch: Any) -> None:
    status = int(sketch.solve())
    fully_constrained = bool(getattr(sketch, "FullyConstrained", False))
    dof = int(sketch.getLastDoF()) if hasattr(sketch, "getLastDoF") else None
    if status != 0 or not fully_constrained:
        raise BuildContractError(
            f"{sketch.Name}: solver={status}, fully_constrained="
            f"{fully_constrained}, dof={dof}"
        )


def assert_single_valid_solid(obj: Any) -> dict[str, Any]:
    if not hasattr(obj, "Shape"):
        raise BuildContractError(f"{obj.Name} has no Shape")
    shape = obj.Shape
    if shape.isNull():
        raise BuildContractError(f"{obj.Name} has a null Shape")
    if not shape.isValid():
        raise BuildContractError(f"{obj.Name} has an invalid Shape")
    solids = list(shape.Solids)
    if len(solids) != 1:
        raise BuildContractError(
            f"{obj.Name} must contain one solid, found {len(solids)}"
        )
    if shape.Volume <= 0:
        raise BuildContractError(f"{obj.Name} has non-positive volume")
    box = shape.BoundBox
    center = shape.CenterOfMass
    return {
        "object": obj.Name,
        "label": obj.Label,
        "solid_count": len(solids),
        "volume_mm3": float(shape.Volume),
        "area_mm2": float(shape.Area),
        "bounding_box_mm": {
            "x": float(box.XLength),
            "y": float(box.YLength),
            "z": float(box.ZLength),
        },
        "center_of_mass_mm": {
            "x": float(center.x),
            "y": float(center.y),
            "z": float(center.z),
        },
    }


def software_versions() -> dict[str, Any]:
    version = list(App.Version())
    return {
        "freecad": version,
        "opencascade": App.ConfigGet("OCC_VERSION_COMPLETE")
        or App.ConfigGet("OCC_VERSION"),
    }


def write_report(path: str, payload: Mapping[str, Any]) -> None:
    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(dict(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
