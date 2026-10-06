#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "suite", ROOT / "scripts" / "suite_release_validate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def emit(root, name, payload):
    path = root / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(root):
    product = {
        "part_number": "PART-1", "revision": "A", "configuration": "BASE",
        "maturity": "production_candidate",
        "acceptance_authority_role": "design authority",
    }
    domains = []
    for domain in sorted(MODULE.BASE_DOMAINS):
        contract, contract_hash = emit(root, f"{domain}-contract.json", {"product": product})
        report_payload = {
            "validator_id": f"{domain}-validator", "contract_sha256": contract_hash,
            "verdict": "PASS", "product": product,
        }
        report, report_hash = emit(root, f"{domain}-report.json", report_payload)
        domains.append({
            "id": domain, "applicable": True, "identity_scope": "product",
            "validator_id": f"{domain}-validator", "verdict": "PASS",
            "contract_path": contract.name, "contract_sha256": contract_hash,
            "report_path": report.name, "report_sha256": report_hash,
        })
    derivative = root / "part.step"
    derivative.write_bytes(b"STEP")
    derivative_hash = hashlib.sha256(b"STEP").hexdigest()
    return {
        "schema_version": "1.0", "product": product,
        "scope": {key: False for key in MODULE.SCOPED_DOMAINS},
        "domains": domains,
        "derivatives": [{
            "path": "part.step", "sha256": derivative_hash,
            "artifact_type": "STEP AP242", "derived_from_sha256": "a" * 64,
            "configuration": "BASE", "generator": "FreeCAD",
            "generator_version": "1.1.2", "generation_record_sha256": "b" * 64,
        }],
        "approvals": [
            {"role": role, "decision": "approved", "configuration": "BASE", "date": "2026-07-25"}
            for role in ("design authority", "quality authority", "manufacturing authority")
        ],
    }


def expect(data, root, verdict, phrase=None):
    report = MODULE.validate(data, root)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in item for item in report["errors"]), report


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    base = fixture(root)
    expect(base, root, "PASS")
    case = copy.deepcopy(base); case["domains"].pop()
    expect(case, root, "FAIL", "absent")
    case = copy.deepcopy(base); case["domains"][0]["contract_sha256"] = "0" * 64
    expect(case, root, "FAIL", "hash mismatch")
    case = copy.deepcopy(base); case["domains"][0]["verdict"] = "FAIL"
    expect(case, root, "FAIL", "differs")
    case = copy.deepcopy(base)
    report_path = root / case["domains"][0]["report_path"]
    report_data = json.loads(report_path.read_text())
    report_data["product"]["configuration"] = "OTHER"
    report_path.write_text(json.dumps(report_data))
    case["domains"][0]["report_sha256"] = hashlib.sha256(report_path.read_bytes()).hexdigest()
    expect(case, root, "FAIL", "configuration")

print("suite semantic release gate regression tests: PASS")
