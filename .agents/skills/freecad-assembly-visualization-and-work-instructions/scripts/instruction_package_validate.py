#!/usr/bin/env python3
"""Validate assembly instructional media against its engineering sources."""

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

MATURITIES = {"concept", "prototype", "verification", "production_candidate", "released"}
RECORD_STATES = {"template", "fixture_only", "controlled_evidence"}
HASH = re.compile(r"^[0-9a-fA-F]{64}$")
SENTINELS = re.compile(
    r"^(?:tbd|todo|unknown|unassigned|unnamed(?:[_ -].*)?|project-recorded|"
    r"project-pinned|sample|example|placeholder|n/?a)$",
    re.IGNORECASE,
)
ARTIFACT_FIELDS = (
    "frame_manifest",
    "png_sequence_hash_manifest",
    "encoded_media",
    "techdraw_pdf",
    "instruction_manual",
)


def present(value):
    return value is not None and value != "" and value != [] and value != {}


def controlled_value(value):
    return present(value) and not (
        isinstance(value, str) and SENTINELS.fullmatch(value.strip())
    )


def finite_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def require(obj, fields, prefix, errors, controlled=False):
    if not isinstance(obj, dict):
        errors.append(f"{prefix} must be an object")
        return
    predicate = controlled_value if controlled else present
    for field in fields:
        if not predicate(obj.get(field)):
            errors.append(f"{prefix}.{field} is required")


def dependency_cycle(step_map):
    visiting, visited = set(), set()

    def visit(step_id):
        if step_id in visiting:
            return True
        if step_id in visited:
            return False
        visiting.add(step_id)
        for predecessor in step_map.get(step_id, []):
            if predecessor in step_map and visit(predecessor):
                return True
        visiting.remove(step_id)
        visited.add(step_id)
        return False

    return any(visit(step_id) for step_id in step_map)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_frame_manifest(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def validate(
    data,
    assembly=None,
    bom=None,
    frame_manifest=None,
    artifact_root=None,
):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return {"verdict": "FAIL", "errors": ["contract must be a JSON object"], "warnings": []}

    record_state = data.get("record_state")
    if record_state not in RECORD_STATES:
        errors.append(f"record_state must be one of {sorted(RECORD_STATES)}")
    controlled = record_state == "controlled_evidence"
    if data.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")

    product = data.get("product", {})
    require(
        product,
        ("assembly_number", "revision", "configuration", "maturity", "acceptance_authority_role"),
        "product",
        errors,
        controlled,
    )
    maturity = product.get("maturity")
    if maturity not in MATURITIES:
        errors.append(f"product.maturity must be one of {sorted(MATURITIES)}")
    candidate = controlled and maturity in {"production_candidate", "released"}

    source = data.get("source", {})
    require(
        source,
        (
            "root_fcstd_hash",
            "child_revision_manifest",
            "bom_revision",
            "freecad_version",
            "opencascade_version",
            "assembly_engineering_evidence",
            "collision_clearance_evidence",
        ),
        "source",
        errors,
        controlled,
    )
    if present(source.get("root_fcstd_hash")) and not HASH.fullmatch(str(source["root_fcstd_hash"])):
        errors.append("source.root_fcstd_hash must be a 64-character SHA-256")

    motion = data.get("motion", {})
    require(
        motion,
        (
            "time_start_s",
            "time_end_s",
            "output_step_s",
            "expected_frame_count",
            "fps",
            "global_error_tolerance",
            "drivers",
            "critical_pose_ids",
            "frame_manifest",
        ),
        "motion",
        errors,
    )
    start, end, step = motion.get("time_start_s"), motion.get("time_end_s"), motion.get("output_step_s")
    if all(finite_number(x) for x in (start, end, step)) and step > 0 and end >= start:
        intervals = (end - start) / step
        if not math.isclose(intervals, round(intervals), rel_tol=1e-9, abs_tol=1e-9):
            errors.append("motion.output_step_s must land exactly on time_end_s")
        expected = int(round(intervals)) + 1
        if motion.get("expected_frame_count") != expected:
            errors.append(f"motion.expected_frame_count must be {expected}")
    else:
        errors.append("motion requires finite end >= start and positive output_step_s")
    if not finite_number(motion.get("fps")) or motion.get("fps", 0) <= 0:
        errors.append("motion.fps must be a positive finite number")
    if not finite_number(motion.get("global_error_tolerance")) or motion.get("global_error_tolerance", 0) <= 0:
        errors.append("motion.global_error_tolerance must be a positive finite number")

    drivers = motion.get("drivers")
    driver_ids = set()
    if not isinstance(drivers, list) or not drivers:
        errors.append("motion.drivers must contain at least one driver")
    else:
        allowed = {"Revolute": {"Angular"}, "Slider": {"Linear"}, "Cylindrical": {"Angular", "Linear"}}
        for index, driver in enumerate(drivers):
            if not isinstance(driver, dict):
                errors.append(f"motion.drivers[{index}] must be an object")
                continue
            require(
                driver,
                ("joint_id", "joint_type", "motion_type", "formula", "unit"),
                f"motion.drivers[{index}]",
                errors,
                controlled,
            )
            if driver.get("motion_type") not in allowed.get(driver.get("joint_type"), set()):
                errors.append(f"motion.drivers[{index}] unsupported joint/motion combination")
            if driver.get("joint_id") in driver_ids:
                errors.append(f"duplicate motion driver joint {driver.get('joint_id')}")
            driver_ids.add(driver.get("joint_id"))

    require(
        data.get("camera", {}),
        ("projection", "camera_state_artifact", "resolution_px", "background", "display_state"),
        "camera",
        errors,
        controlled,
    )
    instructions = data.get("instructions", [])
    if not isinstance(instructions, list) or not instructions:
        errors.append("instructions must contain at least one step")
        instructions = []
    ids = {x.get("id") for x in instructions if isinstance(x, dict) and present(x.get("id"))}
    if len(ids) != len(instructions):
        errors.append("instruction IDs must be present and unique")
    for index, item in enumerate(instructions):
        if not isinstance(item, dict):
            errors.append(f"instructions[{index}] must be an object")
            continue
        require(
            item,
            (
                "id",
                "occurrence_id",
                "find_number",
                "quantity",
                "view_or_frame",
                "tool_and_fixture",
                "torque_or_process",
                "safety_esd_cleanliness",
                "inspection_acceptance",
                "rework_or_reversal",
            ),
            f"instructions[{index}]",
            errors,
            controlled,
        )
        if not isinstance(item.get("predecessors"), list):
            errors.append(f"instructions[{index}].predecessors must be a list")
        else:
            for predecessor in item["predecessors"]:
                if predecessor not in ids:
                    errors.append(f"instructions[{index}] predecessor {predecessor} does not resolve")
                if predecessor == item.get("id"):
                    errors.append(f"instructions[{index}] cannot depend on itself")
        if not isinstance(item.get("quantity"), int) or isinstance(item.get("quantity"), bool) or item.get("quantity", 0) <= 0:
            errors.append(f"instructions[{index}].quantity must be a positive integer")
    step_map = {
        item.get("id"): item.get("predecessors", [])
        for item in instructions
        if isinstance(item, dict) and present(item.get("id")) and isinstance(item.get("predecessors"), list)
    }
    if dependency_cycle(step_map):
        errors.append("instruction predecessor graph contains a cycle")

    views = data.get("exploded_views", [])
    if not isinstance(views, list):
        errors.append("exploded_views must be a list")
        views = []
    view_ids = set()
    for index, view in enumerate(views):
        if not isinstance(view, dict):
            errors.append(f"exploded_views[{index}] must be an object")
            continue
        require(
            view,
            (
                "id",
                "move_ids",
                "occurrence_ids",
                "instruction_steps",
                "design_placement_restored_evidence",
                "techdraw_page",
            ),
            f"exploded_views[{index}]",
            errors,
            controlled,
        )
        if view.get("id") in view_ids:
            errors.append(f"duplicate exploded view ID {view.get('id')}")
        view_ids.add(view.get("id"))
        for step_id in view.get("instruction_steps", []):
            if step_id not in ids:
                errors.append(f"exploded_views[{index}] instruction step {step_id} does not resolve")

    artifacts = data.get("artifacts", {})
    require(
        artifacts,
        ARTIFACT_FIELDS + ("derived_from_root_hash", "encoder_and_version", "visual_qa_report"),
        "artifacts",
        errors,
        controlled,
    )
    for field in ARTIFACT_FIELDS:
        record = artifacts.get(field)
        if not isinstance(record, dict):
            errors.append(f"artifacts.{field} must be an object with path and sha256")
            continue
        require(record, ("path", "sha256"), f"artifacts.{field}", errors, controlled)
        if present(record.get("sha256")) and not HASH.fullmatch(str(record["sha256"])):
            errors.append(f"artifacts.{field}.sha256 must be a 64-character SHA-256")
    for field in ("derived_from_root_hash", "visual_qa_report_hash"):
        if present(artifacts.get(field)) and not HASH.fullmatch(str(artifacts[field])):
            errors.append(f"artifacts.{field} must be a 64-character SHA-256")
    if present(source.get("root_fcstd_hash")) and artifacts.get("derived_from_root_hash") != source.get("root_fcstd_hash"):
        errors.append("instructional artifacts are stale: derived root hash does not match source")

    assembly_occurrences = {
        item.get("occurrence_id"): item
        for item in (assembly or {}).get("occurrences", [])
        if isinstance(item, dict)
    }
    bom_occurrences = {
        item.get("id"): item
        for item in (bom or {}).get("occurrences", [])
        if isinstance(item, dict)
    }
    release = data.get("release", {})
    reconciliations = release.get("bom_callout_reconciliation", [])
    reconciliation_by_occurrence = {
        item.get("occurrence_id"): item
        for item in reconciliations
        if isinstance(item, dict)
    } if isinstance(reconciliations, list) else {}

    rows = frame_manifest if isinstance(frame_manifest, list) else []
    frame_refs = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        frame_refs.update(
            str(row.get(key))
            for key in ("frame_index", "frame_id", "pose_id", "image_path")
            if controlled_value(row.get(key))
        )

    if candidate:
        if not isinstance(assembly, dict):
            errors.append("production candidate requires --assembly-contract")
        if not isinstance(bom, dict):
            errors.append("production candidate requires --bom-contract")
        if not rows:
            errors.append("production candidate requires a non-empty --frame-manifest")
        if artifact_root is None:
            errors.append("production candidate requires --artifact-root")
        if product.get("assembly_number") != (assembly or {}).get("product", {}).get("part_number"):
            errors.append("product assembly number does not match assembly contract")
        if product.get("revision") != (assembly or {}).get("product", {}).get("revision"):
            errors.append("product revision does not match assembly contract")
        assembly_configs = {
            item.get("id") for item in (assembly or {}).get("configurations", []) if isinstance(item, dict)
        }
        if product.get("configuration") not in assembly_configs:
            errors.append("product configuration does not resolve in assembly contract")
        if source.get("bom_revision") != (bom or {}).get("product", {}).get("revision"):
            errors.append("source BOM revision does not match BOM contract")

        if len(rows) != motion.get("expected_frame_count"):
            errors.append("frame manifest row count does not match motion.expected_frame_count")
        seen_indices, seen_times = set(), set()
        for index, row in enumerate(rows):
            try:
                frame_index = int(row.get("frame_index"))
                time_s = float(row.get("time_s"))
            except (TypeError, ValueError):
                errors.append(f"frame manifest row {index} has invalid frame_index/time_s")
                continue
            if frame_index != index:
                errors.append("frame manifest indices must be contiguous and ordered from zero")
            if frame_index in seen_indices or time_s in seen_times:
                errors.append("frame manifest frame indices and times must be unique")
            seen_indices.add(frame_index)
            seen_times.add(time_s)
            expected_time = start + index * step if all(finite_number(x) for x in (start, step)) else None
            if expected_time is not None and not math.isclose(time_s, expected_time, abs_tol=1e-9):
                errors.append(f"frame manifest row {index} time does not match deterministic sample")
            if row.get("root_fcstd_hash") != source.get("root_fcstd_hash"):
                errors.append(f"frame manifest row {index} has stale root hash")
            if row.get("configuration") != product.get("configuration"):
                errors.append(f"frame manifest row {index} has wrong configuration")
            if not controlled_value(row.get("joint_values")):
                errors.append(f"frame manifest row {index} lacks joint values")
        pose_ids = {row.get("pose_id") for row in rows}
        missing_poses = set(motion.get("critical_pose_ids") or []) - pose_ids
        if missing_poses:
            errors.append(f"frame manifest lacks critical poses {sorted(missing_poses)}")

        if not isinstance(reconciliations, list) or not reconciliations:
            errors.append("release.bom_callout_reconciliation must contain controlled mappings")
        for index, item in enumerate(reconciliations if isinstance(reconciliations, list) else []):
            require(
                item,
                ("occurrence_id", "bom_occurrence_id", "find_number", "quantity"),
                f"release.bom_callout_reconciliation[{index}]",
                errors,
                True,
            )
            if item.get("occurrence_id") not in assembly_occurrences:
                errors.append(f"release BOM mapping references unknown assembly occurrence {item.get('occurrence_id')}")
            bom_item = bom_occurrences.get(item.get("bom_occurrence_id"))
            if bom_item is None:
                errors.append(f"release BOM mapping references unknown BOM occurrence {item.get('bom_occurrence_id')}")
            elif bom_item.get("quantity") != item.get("quantity"):
                errors.append(f"release BOM mapping quantity does not match BOM occurrence {item.get('bom_occurrence_id')}")

        for index, item in enumerate(instructions):
            if not isinstance(item, dict):
                continue
            occurrence_id = item.get("occurrence_id")
            if occurrence_id not in assembly_occurrences:
                errors.append(f"instructions[{index}] occurrence {occurrence_id} does not resolve in assembly")
            mapping = reconciliation_by_occurrence.get(occurrence_id)
            if mapping is None:
                errors.append(f"instructions[{index}] lacks a BOM callout reconciliation")
            else:
                if str(item.get("find_number")) != str(mapping.get("find_number")):
                    errors.append(f"instructions[{index}] find number does not match BOM reconciliation")
                if item.get("quantity") != mapping.get("quantity"):
                    errors.append(f"instructions[{index}] quantity does not match BOM reconciliation")
            if item.get("view_or_frame") not in view_ids | frame_refs:
                errors.append(f"instructions[{index}] view_or_frame does not resolve")

        for index, view in enumerate(views):
            for occurrence_id in view.get("occurrence_ids", []):
                if occurrence_id not in assembly_occurrences:
                    errors.append(f"exploded_views[{index}] occurrence {occurrence_id} does not resolve in assembly")

        if artifact_root is not None:
            root = Path(artifact_root)
            for field in ARTIFACT_FIELDS:
                record = artifacts.get(field)
                if not isinstance(record, dict) or not controlled_value(record.get("path")):
                    continue
                path = root / record["path"]
                try:
                    path.resolve().relative_to(root.resolve())
                except ValueError:
                    errors.append(f"artifacts.{field}.path escapes artifact root")
                    continue
                if not path.is_file():
                    errors.append(f"artifacts.{field}.path does not exist")
                elif sha256_file(path) != str(record.get("sha256", "")).lower():
                    errors.append(f"artifacts.{field}.sha256 does not match file content")

        require(
            release,
            ("bom_callout_reconciliation", "cold_regeneration_evidence", "approver_role", "approval_date"),
            "release",
            errors,
            True,
        )
        if release.get("approver_role") != product.get("acceptance_authority_role"):
            errors.append("release approver role does not match product acceptance authority")
        if release.get("configuration") != product.get("configuration"):
            errors.append("release configuration does not match product configuration")
    elif maturity in {"production_candidate", "released"}:
        warnings.append("template/fixture record cannot be production evidence")
    else:
        warnings.append("non-production maturity: release completeness is not enforced")

    if errors:
        verdict = "FAIL"
    elif record_state != "controlled_evidence":
        verdict = "DRAFT"
    elif maturity in {"concept", "prototype"}:
        verdict = "DRAFT"
    elif maturity == "verification":
        verdict = "CONDITIONAL"
    elif maturity == "released":
        verdict = "RELEASED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "errors": errors, "warnings": warnings}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("contract")
    parser.add_argument("--assembly-contract")
    parser.add_argument("--bom-contract")
    parser.add_argument("--frame-manifest")
    parser.add_argument("--artifact-root")
    args = parser.parse_args()
    report = validate(
        load_json(args.contract),
        load_json(args.assembly_contract) if args.assembly_contract else None,
        load_json(args.bom_contract) if args.bom_contract else None,
        read_frame_manifest(Path(args.frame_manifest)) if args.frame_manifest else None,
        args.artifact_root,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] in {"PASS", "RELEASED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
