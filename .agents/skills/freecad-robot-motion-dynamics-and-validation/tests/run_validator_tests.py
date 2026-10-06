#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "motion_dynamics_validate.py")
MODULE = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MODULE)


def base():
    return json.loads((ROOT / "assets" / "motion-dynamics-contract.json").read_text())


def controlled():
    data = base()
    data["record_state"] = "controlled_evidence"
    return data


def expect(data, verdict, phrase=None):
    report = MODULE.validate(data)
    assert report["verdict"] == verdict, report
    if phrase: assert any(phrase in x for x in report["errors"]), report


expect(base(), "DRAFT")
expect(controlled(), "PASS")
case = controlled(); case["links"][0]["mass_kg"] = 0; expect(case, "FAIL", "mass_kg")
case = controlled(); case["links"][0]["mass_kg"] = float("nan"); expect(case, "FAIL", "finite")
case = controlled(); case["links"][0]["source_hash"] = "bad"; expect(case, "FAIL", "source_hash")
case = controlled(); case["links"][0]["inertia_kg_m2"][0][1] = 0.1; expect(case, "FAIL", "symmetric")
case = controlled(); case["links"][0]["inertia_kg_m2"] = [[1,0,0],[0,0.1,0],[0,0,0.1]]; expect(case, "FAIL", "principal moments")
case = controlled(); case["links"] = ["not-an-object"]; expect(case, "FAIL", "must be an object")
case = controlled(); case["model"]["co_simulation"]["exchange_variables_frames_units"] = ""; expect(case, "FAIL", "exchange_variables")
case = controlled(); case["model"]["actuator_drive_controller_evidence"] = ""; expect(case, "FAIL", "actuator")
case = controlled(); case["trajectory"]["sample_rate_hz"] = 0; expect(case, "FAIL", "sample_rate")
case = controlled(); case["solver"]["version"] = "TBD"; expect(case, "FAIL", "solver.version")
case = controlled(); case["solver"]["time_step_s"] = 0; expect(case, "FAIL", "time_step")
case = controlled(); case["verification"]["constraint_residual_observed"] = float("inf"); expect(case, "FAIL", "finite")
case = controlled(); case["verification"]["constraint_residual_observed"] = 1e-3; expect(case, "FAIL", "constraint residual")
case = controlled(); case["verification"]["time_step_sensitivity_evidence"] = ""; expect(case, "FAIL", "time_step_sensitivity")
case = controlled(); case["load_reconciliation"]["fea_load_transfer"]["source_hash"] = "bad"; expect(case, "FAIL", "source_hash")
case = controlled(); case["load_reconciliation"]["fea_load_transfer"]["configuration"] = "OTHER"; expect(case, "FAIL", "product.configuration")
case = controlled(); case["physical_correlation"]["channels"][0]["measured"] = 0.5; expect(case, "FAIL", "quantitative comparison")
case = controlled(); case["physical_correlation"]["accepted_by_role"] = "designer"; expect(case, "FAIL", "acceptance_authority_role")
case = controlled(); case["physical_correlation"]["state"] = "failed"; expect(case, "FAIL", "failed physical")
case = controlled(); case["physical_correlation"]["state"] = "planned"; expect(case, "FAIL", "production maturity")
case = controlled(); case["product"]["maturity"] = "released"; case["physical_correlation"]["state"] = "planned"; expect(case, "FAIL", "production maturity")
case = controlled(); case["release"]["approver_role"] = "designer"; expect(case, "FAIL", "acceptance_authority_role")
case = controlled(); case["product"]["maturity"] = "prototype"; case["release"] = {}; expect(case, "DRAFT")
expect(None, "FAIL", "JSON object")
print("motion dynamics validator regression tests: PASS")
