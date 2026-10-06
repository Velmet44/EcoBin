#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "additive_contract_validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
H = "a" * 64


def template():
    return json.loads((ROOT / "assets" / "additive-manufacturing-contract.json").read_text())


def base():
    data = template()
    data["record_state"] = "controlled_evidence"
    data["feedstock_control"] = {
        "manufacturer": "PolymerCo", "material_specification": "AMS-AM-PA12",
        "lot_id": "LOT-42", "certificate_sha256": H, "receipt_date": "2026-07-01",
        "storage_condition": "sealed at <10% RH", "drying_or_conditioning_record": "DRY-42",
        "reuse_policy": "maximum two qualified cycles", "reuse_count": 0,
        "contamination_control": "dedicated sealed handling system",
    }
    evidence = {"id": "REC-1", "revision": "A", "sha256": H, "status": "approved"}
    data["equipment_control"] = {
        "qualification_record": evidence, "calibration_record": evidence,
        "maintenance_record": evidence, "last_maintenance_date": "2026-07-01",
        "next_due_date": "2027-07-01", "build_platform_id": "PLATE-7",
        "environment_monitoring": "LOG-77",
    }
    data["build_execution"] = {
        "build_id": "BUILD-77", "operator_id": "OP-11", "parameter_file_sha256": H,
        "support_file_sha256": H, "orientation_file_sha256": H,
        "machine_log_sha256": H, "monitoring_disposition": "accepted; no excursions",
        "build_start": "2026-07-20T08:00:00Z", "build_end": "2026-07-20T12:00:00Z",
        "part_serials": ["P001"],
    }
    data["qualification"]["coupon_results"] = [{
        "id": "C-1", "build_id": "BUILD-77", "orientation": "XY",
        "test_method": "ASTM D638", "result": 62.0, "unit": "MPa",
        "lower_limit": 55.0, "status": "pass", "report_sha256": H,
    }]
    data["postprocess_and_inspection"]["certificates"] = [evidence]
    data["personnel_and_ehs"] = {
        "operator_qualification": evidence, "site_process_qualification": evidence,
        "ppe_and_exposure_control": "EHS-11", "powder_or_resin_handling": "WI-EHS-12",
        "fire_explosion_control": "FIRE-PLAN-2", "waste_disposition": "WASTE-REC-7",
    }
    data["release"] = {
        "approvals": [
            {"role": "supplier quality", "status": "approved"},
            {"role": "quality authority", "status": "approved"},
            {"role": "additive manufacturing authority", "status": "approved"},
        ],
        "approval_date": "2026-07-25", "configuration": "PRODUCTION",
    }
    return data


def expect(data, verdict, phrase=None):
    report = MODULE.validate(data)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in item for item in report["errors"]), report


expect(template(), "DRAFT")
expect(base(), "PASS")
case = base(); case["feedstock_control"]["certificate_sha256"] = "bad"; expect(case, "FAIL", "certificate_sha256")
case = base(); case["feedstock_control"]["reuse_count"] = -1; expect(case, "FAIL", "reuse_count")
case = base(); case["equipment_control"]["calibration_record"]["status"] = "expired"; expect(case, "FAIL", "calibration_record.status")
case = base(); case["build_execution"]["machine_log_sha256"] = "bad"; expect(case, "FAIL", "machine_log")
case = base(); case["qualification"]["coupon_results"][0]["result"] = 50; expect(case, "FAIL", "below")
case = base(); case["qualification"]["coupon_results"][0]["build_id"] = "OTHER"; expect(case, "FAIL", "production build")
case = base(); case["postprocess_and_inspection"]["certificates"] = []; expect(case, "FAIL", "certificates")
case = base(); case["personnel_and_ehs"]["operator_qualification"] = {}; expect(case, "FAIL", "operator_qualification")
case = base(); case["release"]["approvals"].pop(); expect(case, "FAIL", "approved roles")
case = base(); case["state_chain"] = ["as-built"]; expect(case, "FAIL", "state_chain")
expect(None, "FAIL", "JSON object")
print("additive contract validator regression tests: PASS")
