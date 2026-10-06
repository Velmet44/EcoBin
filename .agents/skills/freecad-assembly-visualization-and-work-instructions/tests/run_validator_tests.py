#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "instruction_package_validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def template():
    return json.loads((ROOT / "assets" / "visualization-instruction-contract.json").read_text())


def fixtures():
    data = template()
    data["record_state"] = "controlled_evidence"
    data["source"]["opencascade_version"] = "OCCT 7.9.1"
    data["artifacts"]["encoder_and_version"] = "ffmpeg 8.0"
    assembly = {
        "product": {"part_number": "ASM-001", "revision": "A"},
        "configurations": [{"id": "PRODUCTION"}],
        "occurrences": [{"occurrence_id": "OCC-BRACKET-01"}],
    }
    bom = {
        "product": {"revision": "A"},
        "occurrences": [{"id": "M-BRACKET-01", "quantity": 1}],
    }
    rows = [
        {
            "frame_index": str(index),
            "time_s": str(index * 0.5),
            "pose_id": pose,
            "joint_values": f"J1={index * 5} deg",
            "image_path": f"frames/{index:04d}.png",
            "root_fcstd_hash": "a" * 64,
            "configuration": "PRODUCTION",
        }
        for index, pose in enumerate(("POSE-START", "POSE-1", "POSE-MID", "POSE-3", "POSE-END"))
    ]
    temp = tempfile.TemporaryDirectory()
    artifact_root = Path(temp.name)
    for field in MODULE.ARTIFACT_FIELDS:
        path = artifact_root / f"{field}.dat"
        path.write_bytes(field.encode())
        data["artifacts"][field] = {
            "path": path.name,
            "sha256": hashlib.sha256(field.encode()).hexdigest(),
        }
    data["release"]["approval_date"] = "2026-07-25"
    return data, assembly, bom, rows, artifact_root, temp


def expect(data, verdict, phrase=None, companions=None):
    args = companions or (None, None, None, None)
    report = MODULE.validate(data, *args)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in item for item in report["errors"]), report


expect(template(), "DRAFT")
data, assembly, bom, rows, artifact_root, temp = fixtures()
companions = (assembly, bom, rows, artifact_root)
expect(data, "PASS", companions=companions)

case = json.loads(json.dumps(data)); case["source"]["root_fcstd_hash"] = "bad"
expect(case, "FAIL", "root_fcstd_hash", companions)
case = json.loads(json.dumps(data)); case["motion"]["expected_frame_count"] = 4
expect(case, "FAIL", "must be 5", companions)
case = json.loads(json.dumps(data)); case["instructions"][0]["occurrence_id"] = "INVENTED"
expect(case, "FAIL", "does not resolve in assembly", companions)
case = json.loads(json.dumps(data)); case["instructions"][0]["find_number"] = "999"
expect(case, "FAIL", "find number", companions)
case = json.loads(json.dumps(data)); case["instructions"][0]["view_or_frame"] = "INVENTED"
expect(case, "FAIL", "view_or_frame", companions)
case = json.loads(json.dumps(data)); case["exploded_views"][0]["occurrence_ids"] = ["INVENTED"]
expect(case, "FAIL", "does not resolve in assembly", companions)
bad_rows = json.loads(json.dumps(rows)); bad_rows[-1]["pose_id"] = "NOT-END"
expect(data, "FAIL", "critical poses", (assembly, bom, bad_rows, artifact_root))
case = json.loads(json.dumps(data)); case["artifacts"]["encoded_media"]["sha256"] = "0" * 64
expect(case, "FAIL", "does not match file content", companions)
case = json.loads(json.dumps(data)); case["release"]["approver_role"] = "drafter"
expect(case, "FAIL", "acceptance authority", companions)
expect(data, "FAIL", "requires --assembly-contract")
expect(None, "FAIL", "JSON object")

temp.cleanup()
print("instruction package validator regression tests: PASS")
