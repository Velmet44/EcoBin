#!/usr/bin/env python3
"""Screen posted mill/lathe G-code for obvious modal and profile conflicts.

This is not a parser for every controller dialect, a collision simulator, or a
machine-safety certification. Unknown syntax must be reviewed against the exact
controller manual by an authorized machinist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"([A-Z])([+-]?(?:\d+(?:\.\d*)?|\.\d+))", re.IGNORECASE)
PAREN_COMMENT_RE = re.compile(r"\([^()]*\)")
MOTION_CODES = {"G0", "G1", "G2", "G3"}
FEED_MOTION_CODES = {"G1", "G2", "G3"}
UNIT_CODES = {"G20", "G21"}
DISTANCE_CODES = {"G90", "G91"}
PLANE_CODES = {"G17", "G18", "G19"}
WORK_OFFSETS = {f"G{number}" for number in range(54, 60)}
FEED_MODES = {"G93", "G94", "G95"}
SPINDLE_MODES = {"G96", "G97"}
AXES = {"X", "Y", "Z"}


def normalize_code(letter: str, number: str) -> str:
    value = float(number)
    if value.is_integer():
        return f"{letter.upper()}{int(value)}"
    normalized = f"{value:.6f}".rstrip("0").rstrip(".")
    return f"{letter.upper()}{normalized}"


def strip_comments(line: str) -> str:
    previous = None
    while previous != line:
        previous = line
        line = PAREN_COMMENT_RE.sub(" ", line)
    return line.split(";", 1)[0].upper()


def load_profile(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Machine profile must be a JSON object")
    return data


def add_finding(
    findings: list[dict[str, Any]],
    severity: str,
    code: str,
    message: str,
    line: int | None = None,
) -> None:
    item: dict[str, Any] = {
        "severity": severity,
        "code": code,
        "message": message,
    }
    if line is not None:
        item["line"] = line
    findings.append(item)


def valid_controlled_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and "TBD" not in value.upper()
        and "REPLACE" not in value.upper()
    )


def validate_profile(
    profile: dict[str, Any], findings: list[dict[str, Any]], generic: bool
) -> bool:
    if generic:
        add_finding(
            findings,
            "WARNING",
            "GENERIC_SCREEN",
            "No controlled machine contract is enforced; result cannot be PASS.",
        )
        return False
    required_text = ("profile_id", "machine", "controller", "process")
    for key in required_text:
        if not valid_controlled_text(profile.get(key)):
            add_finding(
                findings,
                "ERROR",
                "PROFILE_UNCONFIGURED",
                f"Machine profile field {key!r} is missing or a placeholder.",
            )
    post = profile.get("postprocessor")
    if not isinstance(post, dict):
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile needs a controlled postprocessor object.",
        )
    else:
        for key in ("id", "revision"):
            if not valid_controlled_text(post.get(key)):
                add_finding(
                    findings,
                    "ERROR",
                    "PROFILE_UNCONFIGURED",
                    f"Postprocessor field {key!r} is missing or a placeholder.",
                )
    if str(profile.get("units", "")).lower() not in {
        "mm",
        "metric",
        "in",
        "inch",
    }:
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile units must be mm/metric or in/inch.",
        )
    for key in ("max_spindle_rpm", "max_tool_number"):
        value = profile.get(key)
        if not isinstance(value, (int, float)) or value <= 0:
            add_finding(
                findings,
                "ERROR",
                "PROFILE_UNCONFIGURED",
                f"Machine profile {key!r} must be a positive number.",
            )
    limits = profile.get("axis_limits_mm")
    for axis in ("x", "y", "z"):
        bounds = limits.get(axis) if isinstance(limits, dict) else None
        if (
            not isinstance(bounds, dict)
            or not isinstance(bounds.get("min"), (int, float))
            or not isinstance(bounds.get("max"), (int, float))
            or bounds["min"] >= bounds["max"]
        ):
            add_finding(
                findings,
                "ERROR",
                "PROFILE_UNCONFIGURED",
                f"Machine profile axis_limits_mm.{axis} needs numeric min < max.",
            )
    safe_z = profile.get("safe_z_machine_mm")
    z_bounds = limits.get("z") if isinstance(limits, dict) else None
    if not isinstance(safe_z, (int, float)):
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile safe_z_machine_mm must be numeric.",
        )
    elif (
        isinstance(z_bounds, dict)
        and isinstance(z_bounds.get("min"), (int, float))
        and isinstance(z_bounds.get("max"), (int, float))
        and not z_bounds["min"] <= safe_z <= z_bounds["max"]
    ):
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile safe_z_machine_mm lies outside Z axis limits.",
        )
    if profile.get("feed_mode") not in FEED_MODES:
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile feed_mode must be G93, G94, or G95.",
        )
    feed_limits = profile.get("feed_limits")
    if not isinstance(feed_limits, dict):
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile needs feed_limits keyed by the permitted feed mode.",
        )
    else:
        expected_feed_mode = profile.get("feed_mode")
        limit = feed_limits.get(expected_feed_mode)
        if not isinstance(limit, (int, float)) or limit <= 0:
            add_finding(
                findings,
                "ERROR",
                "PROFILE_UNCONFIGURED",
                f"Machine profile feed_limits.{expected_feed_mode} must be positive.",
            )
        if expected_feed_mode == "G95":
            linear = profile.get("max_linear_feed_rate")
            if not isinstance(linear, (int, float)) or linear <= 0:
                add_finding(
                    findings,
                    "ERROR",
                    "PROFILE_UNCONFIGURED",
                    "G95 profile requires positive max_linear_feed_rate.",
                )
    spindle_mode = profile.get("spindle_mode")
    if spindle_mode not in SPINDLE_MODES:
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile spindle_mode must be G96 or G97.",
        )
    if spindle_mode == "G96":
        css_limit = profile.get("max_css")
        if not isinstance(css_limit, (int, float)) or css_limit <= 0:
            add_finding(
                findings,
                "ERROR",
                "PROFILE_UNCONFIGURED",
                "G96 profile requires positive max_css.",
            )
    allowed_offsets = profile.get("allowed_work_offsets")
    if not isinstance(allowed_offsets, list) or not allowed_offsets:
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile needs at least one allowed_work_offsets entry.",
        )
    origins = profile.get("work_offset_origins_machine_mm")
    if not isinstance(origins, dict):
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNCONFIGURED",
            "Machine profile needs work_offset_origins_machine_mm.",
        )
    elif isinstance(allowed_offsets, list):
        for offset in allowed_offsets:
            origin = origins.get(str(offset).upper())
            if (
                not isinstance(origin, dict)
                or any(
                    not isinstance(origin.get(axis), (int, float))
                    for axis in ("x", "y", "z")
                )
            ):
                add_finding(
                    findings,
                    "ERROR",
                    "PROFILE_UNCONFIGURED",
                    f"Machine profile needs numeric machine origin for {offset}.",
                )
    return not any(
        item["severity"] == "ERROR" and item["code"] == "PROFILE_UNCONFIGURED"
        for item in findings
    )


def screen(text: str, profile: dict[str, Any], generic: bool = False) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    profile_ready = validate_profile(profile, findings, generic)
    seen_codes: set[str] = set()
    unit_modes: set[str] = set()
    feed_value: float | None = None
    spindle_value: float | None = None
    distance_mode: str | None = None
    unit_mode: str | None = None
    work_offset: str | None = None
    plane: str | None = None
    feed_mode: str | None = None
    spindle_mode: str | None = None
    motion_mode: str | None = None
    selected_tool: int | None = None
    tool_numbers: set[int] = set()
    spindle_running = False
    motion_count = 0
    first_motion_line: int | None = None
    program_end = False
    max_feed_seen = 0.0
    max_spindle_seen = 0.0
    max_effective_linear_feed = 0.0
    work_position_mm = {"x": 0.0, "y": 0.0, "z": 0.0}
    machine_position_mm = {"x": 0.0, "y": 0.0, "z": 0.0}

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        cleaned = strip_comments(raw_line)
        tokens = [
            (letter.upper(), number, normalize_code(letter, number))
            for letter, number in TOKEN_RE.findall(cleaned)
        ]
        codes = {code for letter, _, code in tokens if letter in {"G", "M"}}
        seen_codes.update(codes)

        for _, _, code in tokens:
            if code in UNIT_CODES:
                unit_mode = code
                unit_modes.add(code)
            elif code in DISTANCE_CODES:
                distance_mode = code
            elif code in PLANE_CODES:
                plane = code
            elif code in WORK_OFFSETS:
                work_offset = code
            elif code in FEED_MODES:
                feed_mode = code
            elif code in SPINDLE_MODES:
                spindle_mode = code
            elif code in MOTION_CODES:
                motion_mode = code

        for letter, number, _ in tokens:
            value = float(number)
            if letter == "F":
                feed_value = abs(value)
                max_feed_seen = max(max_feed_seen, feed_value)
                if feed_mode is None:
                    add_finding(
                        findings,
                        "ERROR",
                        "FEED_BEFORE_MODE",
                        "F word occurs before an explicit G93/G94/G95 mode.",
                        line_number,
                    )
                else:
                    feed_limit = profile.get("feed_limits", {}).get(feed_mode)
                    unit_scale = 25.4 if unit_mode == "G20" and feed_mode in {"G94", "G95"} else 1.0
                    normalized_feed = feed_value * unit_scale
                    if isinstance(feed_limit, (int, float)) and normalized_feed > float(feed_limit):
                        add_finding(
                            findings,
                            "ERROR",
                            "FEED_LIMIT",
                            f"Observed {feed_mode} F{feed_value:g} resolves to "
                            f"{normalized_feed:g}, above profile limit {float(feed_limit):g}.",
                            line_number,
                        )
            elif letter == "S":
                spindle_value = abs(value)
                max_spindle_seen = max(max_spindle_seen, spindle_value)
                if spindle_mode is None:
                    add_finding(
                        findings,
                        "ERROR",
                        "SPINDLE_SPEED_BEFORE_MODE",
                        "S word occurs before an explicit G96/G97 spindle mode.",
                        line_number,
                    )
                elif spindle_mode == "G97":
                    max_spindle = profile.get("max_spindle_rpm")
                    if isinstance(max_spindle, (int, float)) and spindle_value > float(max_spindle):
                        add_finding(
                            findings,
                            "ERROR",
                            "SPINDLE_LIMIT",
                            f"Observed G97 S{spindle_value:g} exceeds "
                            f"{float(max_spindle):g} rpm.",
                            line_number,
                        )
                else:
                    max_css = profile.get("max_css")
                    if isinstance(max_css, (int, float)) and spindle_value > float(max_css):
                        add_finding(
                            findings,
                            "ERROR",
                            "CSS_LIMIT",
                            f"Observed G96 S{spindle_value:g} exceeds CSS limit "
                            f"{float(max_css):g}.",
                            line_number,
                        )
            elif letter == "T":
                selected_tool = int(value)
                tool_numbers.add(selected_tool)
                max_tool = profile.get("max_tool_number")
                if isinstance(max_tool, (int, float)) and selected_tool > int(max_tool):
                    add_finding(
                        findings,
                        "ERROR",
                        "TOOL_NUMBER_LIMIT",
                        f"Observed T{selected_tool} exceeds profile limit {int(max_tool)}.",
                        line_number,
                    )

        axis_words = {
            letter.lower(): float(number)
            for letter, number, _ in tokens
            if letter in AXES
        }
        line_motion = bool(codes.intersection(MOTION_CODES)) or bool(
            axis_words and motion_mode
        )
        if line_motion:
            motion_count += 1
            if first_motion_line is None:
                first_motion_line = line_number
            if unit_mode is None:
                add_finding(
                    findings,
                    "ERROR",
                    "MOTION_BEFORE_UNITS",
                    "Motion occurs before an explicit G20/G21 unit mode.",
                    line_number,
                )
            if distance_mode is None:
                add_finding(
                    findings,
                    "ERROR",
                    "MOTION_BEFORE_DISTANCE_MODE",
                    "Motion occurs before an explicit G90/G91 mode.",
                    line_number,
                )
            if work_offset is None and "G53" not in codes:
                add_finding(
                    findings,
                    "ERROR",
                    "MOTION_BEFORE_WORK_OFFSET",
                    "Motion occurs before an explicit G54-G59 work offset.",
                    line_number,
                )
            if motion_mode in FEED_MOTION_CODES and feed_value is None:
                add_finding(
                    findings,
                    "ERROR",
                    "FEED_MOVE_WITHOUT_FEED",
                    "Feed motion occurs before an F value is established.",
                    line_number,
                )
            if unit_mode is not None and distance_mode is not None and axis_words:
                scale = 25.4 if unit_mode == "G20" else 1.0
                machine_coordinate_move = "G53" in codes
                if machine_coordinate_move and distance_mode != "G90":
                    add_finding(
                        findings,
                        "ERROR",
                        "G53_WITH_INCREMENTAL",
                        "G53 motion must use an explicitly supported absolute convention.",
                        line_number,
                    )
                origin = (
                    profile.get("work_offset_origins_machine_mm", {}).get(
                        work_offset, {}
                    )
                    if work_offset
                    else {}
                )
                for axis, raw_value in axis_words.items():
                    value_mm = raw_value * scale
                    if machine_coordinate_move:
                        target_machine = (
                            value_mm
                            if distance_mode == "G90"
                            else machine_position_mm[axis] + value_mm
                        )
                        machine_position_mm[axis] = target_machine
                    else:
                        target_work = (
                            value_mm
                            if distance_mode == "G90"
                            else work_position_mm[axis] + value_mm
                        )
                        work_position_mm[axis] = target_work
                        offset_value = origin.get(axis)
                        if isinstance(offset_value, (int, float)):
                            machine_position_mm[axis] = target_work + float(offset_value)
                        else:
                            add_finding(
                                findings,
                                "ERROR",
                                "WORK_OFFSET_ORIGIN_UNKNOWN",
                                f"Cannot resolve {work_offset} {axis.upper()} to machine coordinates.",
                                line_number,
                            )
                    bounds = profile.get("axis_limits_mm", {}).get(axis, {})
                    position = machine_position_mm[axis]
                    if (
                        isinstance(bounds, dict)
                        and isinstance(bounds.get("min"), (int, float))
                        and isinstance(bounds.get("max"), (int, float))
                        and not float(bounds["min"]) <= position <= float(bounds["max"])
                    ):
                        add_finding(
                            findings,
                            "ERROR",
                            "AXIS_TRAVEL_LIMIT",
                            f"{axis.upper()} machine position {position:g} mm is outside "
                            f"[{float(bounds['min']):g}, {float(bounds['max']):g}] mm.",
                            line_number,
                        )
            if (
                motion_mode in FEED_MOTION_CODES
                and feed_mode == "G95"
                and feed_value is not None
            ):
                if spindle_mode != "G97" or spindle_value is None:
                    add_finding(
                        findings,
                        "ERROR",
                        "G95_EFFECTIVE_FEED_UNKNOWN",
                        "G95 feed requires explicit G97 RPM to screen effective linear feed.",
                        line_number,
                    )
                else:
                    unit_scale = 25.4 if unit_mode == "G20" else 1.0
                    effective = feed_value * unit_scale * spindle_value
                    max_effective_linear_feed = max(
                        max_effective_linear_feed, effective
                    )
                    max_linear = profile.get("max_linear_feed_rate")
                    if isinstance(max_linear, (int, float)) and effective > float(max_linear):
                        add_finding(
                            findings,
                            "ERROR",
                            "EFFECTIVE_FEED_LIMIT",
                            f"G95 effective feed {effective:g} exceeds "
                            f"{float(max_linear):g} length/min.",
                            line_number,
                        )

        if codes.intersection({"M3", "M4"}):
            if spindle_value is None:
                add_finding(
                    findings,
                    "ERROR",
                    "SPINDLE_WITHOUT_SPEED",
                    "Spindle start occurs before an S value is established.",
                    line_number,
                )
            spindle_running = True
        if "M5" in codes:
            spindle_running = False
        if "M6" in codes and selected_tool is None:
            add_finding(
                findings,
                "ERROR",
                "TOOL_CHANGE_WITHOUT_TOOL",
                "M6 occurs before a T number is established.",
                line_number,
            )
        if "G43" in codes and not any(letter == "H" for letter, _, _ in tokens):
            add_finding(
                findings,
                "WARNING",
                "G43_WITHOUT_H_ON_LINE",
                "G43 has no H word on the same line; confirm controller convention.",
                line_number,
            )
        if codes.intersection({"M2", "M30"}):
            program_end = True

    if not text.strip():
        add_finding(findings, "ERROR", "EMPTY_PROGRAM", "Program is empty.")
    if not unit_modes:
        add_finding(findings, "ERROR", "NO_UNITS", "No G20/G21 unit mode found.")
    if len(unit_modes) > 1 and not profile.get("allow_unit_switch", False):
        add_finding(
            findings,
            "ERROR",
            "UNIT_SWITCH",
            f"Program uses multiple unit modes: {sorted(unit_modes)}.",
        )
    if not seen_codes.intersection(DISTANCE_CODES):
        add_finding(findings, "ERROR", "NO_DISTANCE_MODE", "No G90/G91 mode found.")
    if "G91" in seen_codes and not profile.get("allow_incremental_mode", False):
        add_finding(
            findings,
            "ERROR",
            "INCREMENTAL_MODE",
            "G91 incremental mode is present but not allowed by the profile.",
        )
    if not seen_codes.intersection(WORK_OFFSETS):
        add_finding(
            findings, "ERROR", "NO_WORK_OFFSET", "No G54-G59 work offset found."
        )
    if plane is None:
        add_finding(
            findings,
            "WARNING",
            "NO_EXPLICIT_PLANE",
            "No explicit G17/G18/G19 plane selection found.",
        )
    expected_feed_mode = profile.get("feed_mode")
    if expected_feed_mode and expected_feed_mode not in seen_codes:
        add_finding(
            findings,
            "ERROR",
            "FEED_MODE_MISMATCH",
            f"Profile requires explicit {expected_feed_mode} feed mode.",
        )
    unexpected_feed_modes = seen_codes.intersection(FEED_MODES) - {
        expected_feed_mode
    }
    if unexpected_feed_modes:
        add_finding(
            findings,
            "ERROR",
            "FEED_MODE_SWITCH",
            f"Program uses feed modes outside the profile: {sorted(unexpected_feed_modes)}.",
        )
    expected_spindle_mode = profile.get("spindle_mode")
    if expected_spindle_mode and expected_spindle_mode not in seen_codes:
        add_finding(
            findings,
            "ERROR",
            "SPINDLE_MODE_MISMATCH",
            f"Profile requires explicit {expected_spindle_mode} spindle mode.",
        )
    unexpected_spindle_modes = seen_codes.intersection(SPINDLE_MODES) - {
        expected_spindle_mode
    }
    if unexpected_spindle_modes:
        add_finding(
            findings,
            "ERROR",
            "SPINDLE_MODE_SWITCH",
            f"Program uses spindle modes outside the profile: {sorted(unexpected_spindle_modes)}.",
        )
    if "G96" in seen_codes:
        add_finding(
            findings,
            "ERROR",
            "CSS_REQUIRES_CONTROLLER_VERIFICATION",
            "G96 CSS cannot receive a production PASS from this lexical screen; "
            "verify diameter-dependent RPM and clamp behavior in the exact controller.",
        )
    if spindle_running:
        add_finding(
            findings,
            "ERROR",
            "SPINDLE_NOT_STOPPED",
            "No spindle stop was observed after the final spindle start.",
        )
    if not program_end:
        add_finding(
            findings,
            "ERROR",
            "NO_PROGRAM_END",
            "No M2 or M30 program end was found.",
        )

    profile_units = str(profile.get("units", "")).lower()
    expected_unit_code = {"mm": "G21", "metric": "G21", "in": "G20", "inch": "G20"}.get(
        profile_units
    )
    if expected_unit_code and unit_modes and expected_unit_code not in unit_modes:
        add_finding(
            findings,
            "ERROR",
            "PROFILE_UNIT_MISMATCH",
            f"Profile expects {profile_units!r} but program modes are "
            f"{sorted(unit_modes)}.",
        )

    allowed_offsets = {
        str(code).upper() for code in profile.get("allowed_work_offsets", [])
    }
    used_offsets = seen_codes.intersection(WORK_OFFSETS)
    if allowed_offsets and not used_offsets.issubset(allowed_offsets):
        add_finding(
            findings,
            "ERROR",
            "WORK_OFFSET_NOT_ALLOWED",
            f"Program uses {sorted(used_offsets - allowed_offsets)} outside "
            f"profile allowance {sorted(allowed_offsets)}.",
        )

    for required in profile.get("required_codes", []):
        code = str(required).upper()
        if code not in seen_codes:
            add_finding(
                findings,
                "ERROR",
                "MISSING_PROFILE_CODE",
                f"Profile-required code {code} is absent.",
            )
    for forbidden in profile.get("forbidden_codes", []):
        code = str(forbidden).upper()
        if code in seen_codes:
            add_finding(
                findings,
                "ERROR",
                "FORBIDDEN_PROFILE_CODE",
                f"Profile-forbidden code {code} is present.",
            )

    severity_order = {"ERROR": 0, "WARNING": 1, "INFO": 2}
    findings.sort(
        key=lambda item: (
            severity_order[item["severity"]],
            item.get("line", 0),
            item["code"],
        )
    )
    error_count = sum(item["severity"] == "ERROR" for item in findings)
    warning_count = sum(item["severity"] == "WARNING" for item in findings)
    if not profile_ready and not generic:
        status = "UNCONFIGURED"
    elif error_count:
        status = "FAIL"
    elif warning_count:
        status = "WARN"
    else:
        status = "PASS"
    return {
        "disclaimer": (
            "Lexical/modal screen only; requires controller-aware simulation and "
            "authorized machinist review/prove-out."
        ),
        "profile_id": profile.get("profile_id"),
        "summary": {
            "status": status,
            "errors": error_count,
            "warnings": warning_count,
            "motion_blocks": motion_count,
            "first_motion_line": first_motion_line,
            "unit_modes": sorted(unit_modes),
            "distance_mode_final": distance_mode,
            "work_offset_final": work_offset,
            "plane_final": plane,
            "feed_mode_final": feed_mode,
            "spindle_mode_final": spindle_mode,
            "max_feed_seen": max_feed_seen,
            "max_effective_linear_feed": max_effective_linear_feed,
            "max_spindle_seen": max_spindle_seen,
            "tool_numbers": sorted(tool_numbers),
            "machine_position_final_mm": machine_position_mm,
        },
        "findings": findings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program", help="Posted G-code path, or - for stdin")
    parser.add_argument("--profile", help="Controlled machine profile JSON")
    parser.add_argument(
        "--generic",
        action="store_true",
        help="Run an explicitly non-production generic screen without a profile",
    )
    parser.add_argument("--json-output", help="Write the complete JSON report")
    parser.add_argument(
        "--allow-warnings",
        action="store_true",
        help="Return zero for WARN in a planning-only workflow; production defaults fail closed",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Deprecated compatibility flag; warnings already return nonzero by default",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = (
            sys.stdin.read()
            if args.program == "-"
            else Path(args.program).read_text(encoding="utf-8", errors="replace")
        )
        profile = load_profile(args.profile)
        report = screen(text, profile, generic=args.generic)
        report["program_sha256"] = hashlib.sha256(
            text.encode("utf-8", errors="replace")
        ).hexdigest()
        report["profile_sha256"] = (
            hashlib.sha256(Path(args.profile).read_bytes()).hexdigest()
            if args.profile
            else None
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"preflight error: {exc}", file=sys.stderr)
        return 3

    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    summary = report["summary"]
    print(
        f"{summary['status']}: {summary['errors']} error(s), "
        f"{summary['warnings']} warning(s), "
        f"{summary['motion_blocks']} motion block(s)"
    )
    for item in report["findings"]:
        location = f" line {item['line']}" if "line" in item else ""
        print(f"{item['severity']} {item['code']}{location}: {item['message']}")
    print(report["disclaimer"])

    if summary["errors"]:
        return 2
    if summary["warnings"] and not args.allow_warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
