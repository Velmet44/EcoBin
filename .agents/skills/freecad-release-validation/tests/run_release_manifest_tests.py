#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "manifest", ROOT / "scripts" / "release_manifest.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory) / "PART-1-A"
    root.mkdir()
    artifact = root / "part.step"
    artifact.write_bytes(b"STEP")
    gate = root / "suite-gate.json"
    gate.write_text(json.dumps({
        "verdict": "PASS",
        "product": {
            "part_number": "PART-1", "revision": "A", "configuration": "BASE",
        },
    }))
    metadata = root / "artifact-metadata.json"
    generation_hash = "a" * 64
    metadata.write_text(json.dumps({
        "artifacts": {
            name: {
                "artifact_type": artifact_type,
                "configuration": "BASE",
                "generator": "FreeCAD" if name == "part.step" else "suite_release_validate.py",
                "generator_version": "1.1.2" if name == "part.step" else "1.0",
                "generation_record_sha256": generation_hash,
                "derived_from_sha256": [] if name == "suite-gate.json" else ["b" * 64],
            }
            for name, artifact_type in (
                ("part.step", "STEP AP242"),
                ("suite-gate.json", "suite semantic gate report"),
            )
        }
    }))
    output = root / "release-manifest.json"
    args = argparse.Namespace(
        root=str(root), output=str(output), part_number="PART-1", revision="A",
        configuration="BASE", artifact_metadata=str(metadata),
        suite_gate_report=str(gate), force=False,
        files=[str(artifact), str(gate)],
    )
    assert MODULE.create(args) == 0
    verify = argparse.Namespace(
        manifest=str(output), root=str(root), allow_extra=True,
    )
    assert MODULE.verify(verify) == 0
    artifact.write_bytes(b"CHANGED")
    assert MODULE.verify(verify) == 2

print("release manifest lineage regression tests: PASS")
