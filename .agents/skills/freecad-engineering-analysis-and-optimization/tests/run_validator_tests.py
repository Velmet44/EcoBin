#!/usr/bin/env python3
"""Regression tests for analysis and optimization validators."""

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


analysis_validator = load_module("analysis_contract_validate", ROOT / "scripts" / "analysis_contract_validate.py")
optimization_validator = load_module("optimization_study_validate", ROOT / "scripts" / "optimization_study_validate.py")


def asset(name):
    return json.loads((ROOT / "assets" / name).read_text(encoding="utf-8"))


class AnalysisContractTests(unittest.TestCase):
    def setUp(self):
        self.data = asset("analysis-contract.template.json")

    def assert_error_contains(self, data, text):
        result = analysis_validator.validate(data)
        self.assertEqual("FAIL", result["verdict"], result)
        self.assertTrue(any(text in error for error in result["errors"]), result)

    def test_template_is_valid_conditional_contract(self):
        result = analysis_validator.validate(self.data)
        self.assertEqual("CONDITIONAL", result["verdict"], result)
        self.assertEqual([], result["errors"])

    def test_fully_reviewed_evidence_can_pass_without_claiming_release(self):
        data = copy.deepcopy(self.data)
        data["validation"] = {"status": "pass", "evidence": ["TP-BRKT-042 report rev A"]}
        data["open_actions"][0]["status"] = "closed"
        data["approval"].update({
            "analysis_verdict": "PASS",
            "independent_review": "pass",
            "release_decision": "withheld",
            "date": "2026-07-25",
            "residual_risks": [],
        })
        result = analysis_validator.validate(data)
        self.assertEqual("PASS", result["verdict"], result)
        self.assertEqual([], result["errors"])

    def test_empty_study_cannot_pass(self):
        data = copy.deepcopy(self.data)
        for field in (
            "requirements",
            "geometry_idealizations",
            "materials",
            "load_cases",
            "boundary_conditions",
            "analysis_cases",
            "open_actions",
        ):
            data[field] = []
        data["validation"] = {
            "status": "not_required",
            "rationale": "adversarial empty-study probe",
            "scope": "entire study",
            "approved_by": "analysis authority",
            "approval_date": "2026-07-25",
        }
        data["approval"].update({
            "analysis_verdict": "PASS",
            "independent_review": "pass",
            "release_decision": "withheld",
            "date": "2026-07-25",
            "residual_risks": [],
        })
        result = analysis_validator.validate(data)
        self.assertEqual("FAIL", result["verdict"], result)
        self.assertTrue(
            any("must contain at least one" in error for error in result["errors"]),
            result,
        )

    def test_pass_requires_release_driving_case(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["release_driving"] = False
        data["validation"] = {"status": "pass", "evidence": ["TP-BRKT-042 report rev A"]}
        data["open_actions"][0]["status"] = "closed"
        data["approval"].update({
            "analysis_verdict": "PASS",
            "independent_review": "pass",
            "release_decision": "withheld",
            "date": "2026-07-25",
            "residual_risks": [],
        })
        self.assert_error_contains(data, "at least one release-driving")

    def test_not_required_validation_needs_controlled_waiver(self):
        data = copy.deepcopy(self.data)
        data["validation"] = {"status": "not_required"}
        self.assert_error_contains(data, "validation.rationale")

    def test_reaction_imbalance_rejects_case(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["verification"]["reaction_balance_percent"] = 3.0
        self.assert_error_contains(data, "reaction balance")

    def test_two_mesh_levels_are_not_convergence_evidence(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["verification"]["mesh_convergence"] = data["analysis_cases"][0]["verification"]["mesh_convergence"][:2]
        self.assert_error_contains(data, "at least three levels")

    def test_nonconverged_mesh_rejects_pass_case(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["verification"]["mesh_convergence"][-1]["value"] = 0.49
        self.assert_error_contains(data, "final mesh change")

    def test_converged_displacement_cannot_mask_unconverged_governing_stress(self):
        data = copy.deepcopy(self.data)
        data["requirements"].append({
            "id": "REQ-STR-002",
            "description": "Bracket stress shall not exceed the design allowable",
            "source": "BRKT-042 product requirements rev C",
            "acceptance": {
                "quantity": "governing_stress",
                "operator": "<=",
                "limit": 160.0,
                "unit": "MPa",
            },
        })
        data["load_cases"][0]["requirement_ids"].append("REQ-STR-002")
        data["analysis_cases"][0]["results"].append({
            "requirement_id": "REQ-STR-002",
            "quantity": "governing_stress",
            "value": 145.0,
            "unit": "MPa",
            "criterion_met": True,
            "evidence": "stress-results.csv",
        })
        self.assert_error_contains(data, "lack converged mesh evidence: ['governing_stress']")

    def test_each_release_result_can_bind_to_its_own_convergence_study(self):
        data = copy.deepcopy(self.data)
        data["requirements"].append({
            "id": "REQ-STR-002",
            "description": "Bracket stress shall not exceed the design allowable",
            "source": "BRKT-042 product requirements rev C",
            "acceptance": {
                "quantity": "governing_stress",
                "operator": "<=",
                "limit": 160.0,
                "unit": "MPa",
            },
        })
        data["load_cases"][0]["requirement_ids"].append("REQ-STR-002")
        data["analysis_cases"][0]["results"].append({
            "requirement_id": "REQ-STR-002",
            "quantity": "governing_stress",
            "value": 145.0,
            "unit": "MPa",
            "criterion_met": True,
            "evidence": "stress-results.csv",
        })
        displacement_levels = data["analysis_cases"][0]["verification"]["mesh_convergence"]
        stress_levels = copy.deepcopy(displacement_levels)
        for level, value in zip(stress_levels, (140.0, 144.0, 145.0)):
            level["quantity"] = "governing_stress"
            level["value"] = value
            level["unit"] = "MPa"
        data["analysis_cases"][0]["verification"]["mesh_convergence"] = [
            {"quantity": "tip_displacement", "levels": displacement_levels},
            {"quantity": "governing_stress", "levels": stress_levels},
        ]
        result = analysis_validator.validate(data)
        self.assertEqual("CONDITIONAL", result["verdict"], result)
        self.assertEqual([], result["errors"])

    def test_result_cannot_disagree_with_requirement(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["results"][0]["value"] = 0.7
        self.assert_error_contains(data, "criterion_met disagrees")

    def test_release_cannot_bypass_review_or_open_major_action(self):
        data = copy.deepcopy(self.data)
        data["approval"].update({
            "analysis_verdict": "PASS",
            "release_decision": "approved_by_authority",
            "date": "2026-07-25",
        })
        result = analysis_validator.validate(data)
        self.assertEqual("FAIL", result["verdict"], result)
        joined = "\n".join(result["errors"])
        self.assertIn("independent_review=pass", joined)
        self.assertIn("open blocker/major", joined)

    def test_vague_solver_version_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["solver"]["version"] = "TBD"
        self.assert_error_contains(data, "solver.version")

    def test_loose_reaction_balance_limit_requires_approved_exception(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["verification"]["reaction_balance_limit_percent"] = 5.0
        self.assert_error_contains(data, "acceptance_limit_justifications.reaction_balance")

    def test_loose_analytical_comparison_limit_requires_approved_exception(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["verification"]["analytical_comparison"]["acceptance_percent"] = 25.0
        self.assert_error_contains(data, "acceptance_limit_justifications.analytical_comparison")

    def test_loose_convergence_limit_requires_approved_exception(self):
        data = copy.deepcopy(self.data)
        data["analysis_cases"][0]["verification"]["convergence_acceptance_percent"] = 8.0
        self.assert_error_contains(data, "acceptance_limit_justifications.mesh_convergence")

    def test_dated_approved_exceptions_allow_project_specific_limits(self):
        data = copy.deepcopy(self.data)
        verification = data["analysis_cases"][0]["verification"]
        verification["reaction_balance_limit_percent"] = 5.0
        verification["analytical_comparison"]["acceptance_percent"] = 25.0
        verification["convergence_acceptance_percent"] = 8.0
        verification["acceptance_limit_justifications"] = {
            key: {
                "justification": "Approved low-consequence screening tolerance per project procedure ENG-12",
                "approved_by": "chief_analysis_engineer",
                "approval_date": "2026-07-24",
            }
            for key in ("reaction_balance", "analytical_comparison", "mesh_convergence")
        }
        result = analysis_validator.validate(data)
        self.assertEqual("CONDITIONAL", result["verdict"], result)
        self.assertEqual([], result["errors"])


class OptimizationStudyTests(unittest.TestCase):
    def setUp(self):
        self.data = asset("optimization-study.template.json")

    def assert_error_contains(self, data, text):
        result = optimization_validator.validate(data)
        self.assertEqual("FAIL", result["verdict"], result)
        self.assertTrue(any(text in error for error in result["errors"]), result)

    def test_template_is_valid_planned_study(self):
        result = optimization_validator.validate(self.data)
        self.assertEqual("DRAFT", result["verdict"], result)
        self.assertEqual([], result["errors"])

    def test_shared_sentinel_placeholders_are_rejected(self):
        for sentinel in (
            "TBD", "unknown", "unassigned", "placeholder", "replace-me",
            "to be determined", "controlled-installed-version", "not set",
            "N/A", "none", "null", "YYYY-MM-DD", "XXX", "?",
        ):
            with self.subTest(sentinel=sentinel):
                data = copy.deepcopy(self.data)
                data["study"]["baseline_analysis_contract"] = sentinel
                self.assert_error_contains(data, "study.baseline_analysis_contract is required")

    def test_invalid_variable_bounds_fail(self):
        data = copy.deepcopy(self.data)
        data["variables"][0]["lower"] = 9.0
        self.assert_error_contains(data, "lower must be less than upper")

    def test_selected_candidate_requires_matching_confirmation(self):
        data = copy.deepcopy(self.data)
        data["selection"] = {
            "candidate_id": "CAND-7",
            "rationale": "best robust Pareto compromise",
            "approval_status": "selected_pending_confirmation",
        }
        self.assert_error_contains(data, "matching confirmation run")

    def test_confirmed_candidate_requires_all_confirmation_gates(self):
        data = copy.deepcopy(self.data)
        data["confirmation_runs"][0] = {
            "candidate_id": "CAND-7",
            "authoritative_rebuild": "pass",
            "independent_fine_mesh": "pass",
            "analytical_check": "pass",
            "dfm_review": "required",
            "status": "pass",
        }
        data["selection"] = {
            "candidate_id": "CAND-7",
            "rationale": "best robust Pareto compromise",
            "approval_status": "confirmed",
        }
        self.assert_error_contains(data, "dfm_review must be structured evidence")

    def test_completed_confirmation_can_pass(self):
        data = copy.deepcopy(self.data)
        data["record_state"] = "controlled_evidence"
        data["study"]["status"] = "complete"
        data["results"] = {
            "candidates": [{
                "id": "CAND-7",
                "variables": {"rib_thickness": 4.0, "web_height": 28.0},
                "objectives": {"OBJ-MASS": 0.82, "OBJ-STIFF": 0.31},
                "constraints": {"REQ-STR-001": 0.31, "REQ-DFM-004": 4.0},
                "feasible": True,
                "result_sha256": "a" * 64,
            }],
            "robustness": {
                "candidate_id": "CAND-7", "sample_count": 100,
                "constraint_pass_rate": 0.99, "report_sha256": "b" * 64,
            },
        }
        evidence = {
            "status": "pass", "report_sha256": "c" * 64,
            "configuration_hash": "d" * 64,
        }
        data["confirmation_runs"][0] = {
            "candidate_id": "CAND-7",
            "authoritative_rebuild": evidence,
            "independent_fine_mesh": {
                **evidence, "result_delta_percent": 1.2, "tolerance_percent": 3.0,
            },
            "analytical_check": {
                **evidence, "result_delta_percent": 2.0, "tolerance_percent": 5.0,
            },
            "dfm_review": evidence,
            "status": "pass",
        }
        data["selection"] = {
            "candidate_id": "CAND-7",
            "rationale": "best robust Pareto compromise",
            "approval_status": "confirmed",
            "objective_deltas_from_baseline": {
                "OBJ-MASS": -18.0, "OBJ-STIFF": -5.0,
            },
        }
        result = optimization_validator.validate(data)
        self.assertEqual("PASS", result["verdict"], result)
        self.assertEqual([], result["errors"])

    def test_selected_candidate_must_resolve_and_be_feasible(self):
        data = copy.deepcopy(self.data)
        data["selection"] = {
            "candidate_id": "INVENTED", "rationale": "none",
            "approval_status": "selected_pending_confirmation",
        }
        data["confirmation_runs"][0]["candidate_id"] = "INVENTED"
        self.assert_error_contains(data, "does not resolve")

    def test_quantitative_confirmation_tolerance_is_enforced(self):
        data = copy.deepcopy(self.data)
        data["record_state"] = "controlled_evidence"
        data["study"]["status"] = "complete"
        data["results"] = {
            "candidates": [{
                "id": "CAND-7",
                "variables": {"rib_thickness": 4.0, "web_height": 28.0},
                "objectives": {"OBJ-MASS": 0.82, "OBJ-STIFF": 0.31},
                "constraints": {"REQ-STR-001": 0.31, "REQ-DFM-004": 4.0},
                "feasible": True, "result_sha256": "a" * 64,
            }],
            "robustness": {
                "candidate_id": "CAND-7", "sample_count": 10,
                "constraint_pass_rate": 1.0, "report_sha256": "b" * 64,
            },
        }
        evidence = {"status": "pass", "report_sha256": "c" * 64, "configuration_hash": "d" * 64}
        data["confirmation_runs"][0] = {
            "candidate_id": "CAND-7", "status": "pass",
            "authoritative_rebuild": evidence,
            "independent_fine_mesh": {**evidence, "result_delta_percent": 9, "tolerance_percent": 3},
            "analytical_check": {**evidence, "result_delta_percent": 1, "tolerance_percent": 3},
            "dfm_review": evidence,
        }
        data["selection"] = {
            "candidate_id": "CAND-7", "rationale": "candidate",
            "approval_status": "confirmed",
            "objective_deltas_from_baseline": {"OBJ-MASS": -1, "OBJ-STIFF": -1},
        }
        self.assert_error_contains(data, "exceeds its declared")


if __name__ == "__main__":
    unittest.main(verbosity=2)
