#!/usr/bin/env python3
import importlib.util
import sys
import types
from pathlib import Path


class Quantity:
    def __init__(self, value):
        self.Value = float(value.split()[0])


freecad = types.SimpleNamespace(
    Units=types.SimpleNamespace(Quantity=Quantity),
    Version=lambda: ("1", "1", "2"),
    ConfigGet=lambda key: "7.9.1",
)
sys.modules["FreeCAD"] = freecad

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "contract", ROOT / "scripts" / "freecad_build_contract.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fails(callable_, phrase):
    try:
        callable_()
    except MODULE.BuildContractError as exc:
        assert phrase in str(exc), exc
    else:
        raise AssertionError(f"expected BuildContractError containing {phrase!r}")


assert MODULE.quantity("12 mm").Value == 12
fails(lambda: MODULE.quantity("12"), "explicit unit")
fails(lambda: MODULE.require_keys({"a": 1}, ("a", "b"), "input"), "missing")
fails(lambda: MODULE.require_positive(0, "width"), "positive")


class Object:
    Name = "Body"
    Label = "Body"
    State = []


class Document:
    Objects = [Object()]
    def recompute(self):
        return None


MODULE.recompute_or_raise(Document(), "build")
bad = Document()
bad.Objects[0].State = ["Error"]
fails(lambda: MODULE.recompute_or_raise(bad, "build"), "object failures")

print("parametric build contract regression tests: PASS")
