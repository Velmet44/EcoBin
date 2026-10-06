#!/usr/bin/env python3
"""Adversarial regression tests for the G-code preflight screen."""

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "gcode_preflight.py"
    spec = importlib.util.spec_from_file_location("gcode_preflight", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module()


def profile():
    return {
        "profile_id": "MC-001-REV-A",
        "machine": "controlled three-axis mill",
        "controller": "controlled controller revision",
        "process": "mill",
        "postprocessor": {"id": "POST-001", "revision": "A"},
        "units": "mm",
        "max_spindle_rpm": 12000,
        "max_tool_number": 20,
        "spindle_mode": "G97",
        "feed_mode": "G94",
        "feed_limits": {"G94": 500.0, "G95": 0.5, "G93": 20.0},
        "max_linear_feed_rate": 1000.0,
        "axis_limits_mm": {
            "x": {"min": -100.0, "max": 100.0},
            "y": {"min": -100.0, "max": 100.0},
            "z": {"min": -100.0, "max": 100.0},
        },
        "safe_z_machine_mm": 10.0,
        "allowed_work_offsets": ["G54"],
        "work_offset_origins_machine_mm": {
            "G54": {"x": 0.0, "y": 0.0, "z": 0.0}
        },
        "allow_unit_switch": False,
        "allow_incremental_mode": False,
        "required_codes": [],
        "forbidden_codes": ["G92"],
    }


VALID_PROGRAM = """\
G21 G90 G17 G54 G94 G97
T1 M6
S1000 M3
G0 X0 Y0 Z10
G1 Z0 F100
M5
M30
"""


class GcodePreflightTests(unittest.TestCase):
    def assert_error(self, report, code):
        self.assertNotEqual("PASS", report["summary"]["status"], report)
        self.assertTrue(
            any(
                finding["severity"] == "ERROR" and finding["code"] == code
                for finding in report["findings"]
            ),
            report,
        )

    def test_controlled_program_passes(self):
        report = validator.screen(VALID_PROGRAM, profile())
        self.assertEqual("PASS", report["summary"]["status"], report)

    def test_out_of_travel_move_fails(self):
        program = VALID_PROGRAM.replace("X0 Y0 Z10", "X999 Y0 Z10")
        report = validator.screen(program, profile())
        self.assert_error(report, "AXIS_TRAVEL_LIMIT")

    def test_g95_effective_feed_uses_rpm(self):
        data = profile()
        data["feed_mode"] = "G95"
        data["max_linear_feed_rate"] = 500.0
        program = VALID_PROGRAM.replace("G94", "G95").replace(
            "S1000", "S3000"
        ).replace("F100", "F0.2")
        report = validator.screen(program, data)
        self.assert_error(report, "EFFECTIVE_FEED_LIMIT")

    def test_every_tool_number_is_checked(self):
        program = VALID_PROGRAM.replace("T1 M6", "T99 M6\nT1 M6")
        report = validator.screen(program, profile())
        self.assert_error(report, "TOOL_NUMBER_LIMIT")

    def test_incremental_mode_is_release_error(self):
        program = VALID_PROGRAM.replace("G21 G90", "G21 G91")
        report = validator.screen(program, profile())
        self.assert_error(report, "INCREMENTAL_MODE")

    def test_missing_stop_and_end_are_errors(self):
        program = VALID_PROGRAM.replace("M5\nM30\n", "")
        report = validator.screen(program, profile())
        self.assert_error(report, "SPINDLE_NOT_STOPPED")
        self.assert_error(report, "NO_PROGRAM_END")

    def test_work_offset_origin_is_required(self):
        data = copy.deepcopy(profile())
        data["work_offset_origins_machine_mm"] = {}
        report = validator.screen(VALID_PROGRAM, data)
        self.assertEqual("UNCONFIGURED", report["summary"]["status"], report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
