#!/usr/bin/env python3
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "tolerance_capability_validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def base():
    return json.loads((ROOT / "assets" / "tolerance-capability-contract.json").read_text())


def controlled():
    data = base()
    data["record_state"] = "controlled_evidence"
    return data


def expect(data, verdict, phrase=None):
    report = MODULE.validate(data)
    assert report["verdict"] == verdict, report
    if phrase:
        assert any(phrase in x for x in report["errors"]), report


expect(base(), "DRAFT")
expect(controlled(), "PASS")
case = controlled(); case["process_scope"]["machine_id"] = ""; expect(case, "FAIL", "machine_id")
for sentinel in ("TBD", "unknown", "unassigned", "N/A", "replace-me"):
    case = controlled(); case["process_scope"]["machine_id"] = sentinel; expect(case, "FAIL", "machine_id")
case = controlled(); case["capability_studies"][0]["sample_size"] = 8; expect(case, "FAIL", "sample_size")
case = controlled(); case["capability_studies"][0]["stability_evidence"] = ""; expect(case, "FAIL", "stability")
case = controlled(); case["capability_studies"][0]["cpk"] = 9; expect(case, "FAIL", "CPK")
case = controlled(); case["capability_studies"][0]["ppk"] = 9; expect(case, "FAIL", "PPK")
case = controlled(); case["capability_studies"][0]["sigma_overall"] = -999; expect(case, "FAIL", "sigma_overall")
case = controlled(); case["capability_studies"][0]["cpk"] = 0.1; case["capability_studies"][0]["minimum_cpk"] = 1.33; expect(case, "FAIL", "CPK")
case = controlled(); case["capability_studies"][0]["mean"] = 19.985; expect(case, "FAIL", "below the approved threshold")
case = controlled(); case["measurement_systems"][0]["expanded_uncertainty"] = None; expect(case, "FAIL", "expanded_uncertainty")
case = controlled(); case["measurement_systems"][0]["expanded_uncertainty"] = float("nan"); expect(case, "FAIL", "expanded_uncertainty")
case = controlled(); case["measurement_systems"][0]["msa_evidence"] = ""; expect(case, "FAIL", "msa_evidence")
case = controlled(); case["measurement_systems"][0]["guard_band"] = 0.006; expect(case, "FAIL", "guard band")
case = controlled(); case["characteristics"][0]["process_state"] = ""; expect(case, "FAIL", "process_state")
case = controlled(); case["characteristics"][0]["capability_id"] = "MISSING"; expect(case, "FAIL", "does not resolve")
case = controlled(); case["compensation"]["used"] = True; expect(case, "FAIL", "controlled_derivative_id")
case = controlled(); case["compensation"]["nominal_model_remains_authoritative"] = False; expect(case, "FAIL", "authoritative")
case = controlled(); case["capability_studies"][0]["basis"] = "fai_100_percent"; expect(case, "FAIL", "cannot claim Cpk")
case = controlled(); case["release"]["approver_role"] = "designer"; expect(case, "FAIL", "acceptance_authority_role")
case = controlled(); case["product"]["maturity"] = "released"; expect(case, "FAIL", "baseline_id")
case = controlled(); case["product"]["maturity"] = "prototype"; case["release"] = {}; expect(case, "DRAFT")
expect(None, "FAIL", "JSON object")
print("tolerance capability validator regression tests: PASS")
