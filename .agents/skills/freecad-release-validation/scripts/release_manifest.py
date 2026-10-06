#!/usr/bin/env python3
"""Create or verify a SHA-256 manufacturing-release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def create(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not root.is_dir():
        print(f"release root is not a directory: {root}", file=sys.stderr)
        return 3
    try:
        output.relative_to(root)
    except ValueError:
        print(f"manifest must be inside release root {root}: {output}", file=sys.stderr)
        return 3
    if output.exists() and not args.force:
        print(f"manifest exists; pass --force to replace: {output}", file=sys.stderr)
        return 3
    try:
        metadata = json.loads(Path(args.artifact_metadata).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read artifact metadata: {exc}", file=sys.stderr)
        return 3
    metadata_records = metadata.get("artifacts") if isinstance(metadata, dict) else None
    if not isinstance(metadata_records, dict):
        print("artifact metadata requires an artifacts object keyed by release-relative path", file=sys.stderr)
        return 3
    suite_gate = Path(args.suite_gate_report).expanduser().resolve()
    try:
        suite_payload = json.loads(suite_gate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read suite gate report: {exc}", file=sys.stderr)
        return 3
    if suite_payload.get("verdict") not in {"PASS", "RELEASED"}:
        print("suite semantic gate report is not passing", file=sys.stderr)
        return 3
    suite_identity = suite_payload.get("product", {})
    if suite_identity and (
        suite_identity.get("part_number") != args.part_number
        or suite_identity.get("revision") != args.revision
        or suite_identity.get("configuration") != args.configuration
    ):
        print("suite semantic gate product identity does not match manifest", file=sys.stderr)
        return 3
    files = []
    seen_paths = set()
    for raw in args.files:
        path = Path(raw).expanduser().resolve()
        if not path.is_file():
            print(f"not a file: {path}", file=sys.stderr)
            return 3
        try:
            relative = path.relative_to(root)
        except ValueError:
            print(f"file is outside release root {root}: {path}", file=sys.stderr)
            return 3
        if path == output:
            print("manifest cannot include itself", file=sys.stderr)
            return 3
        if relative.as_posix() in seen_paths:
            print(f"duplicate file argument: {relative}", file=sys.stderr)
            return 3
        seen_paths.add(relative.as_posix())
        record = metadata_records.get(relative.as_posix())
        if not isinstance(record, dict):
            print(f"artifact metadata missing for {relative}", file=sys.stderr)
            return 3
        required = (
            "artifact_type", "configuration", "generator", "generator_version",
            "generation_record_sha256", "derived_from_sha256",
        )
        if any(record.get(key) in (None, "") for key in required):
            print(f"incomplete artifact metadata for {relative}", file=sys.stderr)
            return 3
        if record.get("configuration") != args.configuration:
            print(f"artifact configuration mismatch for {relative}", file=sys.stderr)
            return 3
        if not SHA256_RE.fullmatch(str(record.get("generation_record_sha256", "")).lower()):
            print(f"invalid generation record hash for {relative}", file=sys.stderr)
            return 3
        parents = record.get("derived_from_sha256")
        if not isinstance(parents, list) or any(
            not SHA256_RE.fullmatch(str(item).lower()) for item in parents
        ):
            print(f"derived_from_sha256 must be a list of SHA-256 values for {relative}", file=sys.stderr)
            return 3
        files.append({
            "path": relative.as_posix(),
            "bytes": path.stat().st_size,
            "sha256": digest(path),
            **{key: record[key] for key in required},
        })
    try:
        suite_relative = suite_gate.relative_to(root).as_posix()
    except ValueError:
        print("suite gate report must be inside release root", file=sys.stderr)
        return 3
    if suite_relative not in seen_paths:
        print("suite gate report must be included in manifest files", file=sys.stderr)
        return 3
    payload = {
        "schema": 2,
        "part_number": args.part_number,
        "revision": args.revision,
        "configuration": args.configuration,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "release_root": root.name,
        "suite_gate_report": {
            "path": suite_relative,
            "sha256": digest(suite_gate),
            "verdict": suite_payload.get("verdict"),
        },
        "files": sorted(files, key=lambda item: item["path"]),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"PASS: wrote {len(files)} file record(s) to {output}")
    return 0


def verify(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve()
    root = Path(args.root).expanduser().resolve()
    try:
        payload: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read manifest: {exc}", file=sys.stderr)
        return 3
    failures = []
    if payload.get("schema") != 2:
        failures.append("unsupported or missing schema (expected 2)")
    if not isinstance(payload.get("part_number"), str) or not payload["part_number"]:
        failures.append("missing part_number")
    if not isinstance(payload.get("revision"), str) or not payload["revision"]:
        failures.append("missing revision")
    if not isinstance(payload.get("configuration"), str) or not payload["configuration"]:
        failures.append("missing configuration")
    if payload.get("release_root") != root.name:
        failures.append(
            f"release_root metadata {payload.get('release_root')!r} "
            f"does not match {root.name!r}"
        )
    entries = payload.get("files")
    if not isinstance(entries, list) or not entries:
        failures.append("manifest files must be a non-empty array")
        entries = []
    seen_paths = set()
    listed_paths = set()
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            failures.append(f"file entry {index} is not an object")
            continue
        relative_raw = item.get("path")
        if not isinstance(relative_raw, str) or not relative_raw:
            failures.append(f"file entry {index} has invalid path")
            continue
        relative = Path(relative_raw)
        if relative.is_absolute() or ".." in relative.parts:
            failures.append(f"unsafe manifest path: {relative_raw}")
            continue
        if relative.as_posix() in seen_paths:
            failures.append(f"duplicate manifest path: {relative_raw}")
            continue
        seen_paths.add(relative.as_posix())
        listed_paths.add(relative.as_posix())
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            failures.append(f"manifest path escapes release root: {relative_raw}")
            continue
        expected_bytes = item.get("bytes")
        expected_digest = item.get("sha256")
        for key in ("artifact_type", "configuration", "generator", "generator_version"):
            if not isinstance(item.get(key), str) or not item[key]:
                failures.append(f"missing {key}: {relative_raw}")
        if item.get("configuration") != payload.get("configuration"):
            failures.append(f"configuration mismatch: {relative_raw}")
        if not isinstance(item.get("generation_record_sha256"), str) or not SHA256_RE.fullmatch(
            item.get("generation_record_sha256", "").lower()
        ):
            failures.append(f"invalid generation_record_sha256: {relative_raw}")
        parents = item.get("derived_from_sha256")
        if not isinstance(parents, list) or any(
            not isinstance(parent, str) or not SHA256_RE.fullmatch(parent.lower())
            for parent in (parents or [])
        ):
            failures.append(f"invalid derived_from_sha256: {relative_raw}")
        if not isinstance(expected_bytes, int) or expected_bytes < 0:
            failures.append(f"invalid byte count: {relative_raw}")
            continue
        if not isinstance(expected_digest, str) or not SHA256_RE.fullmatch(
            expected_digest
        ):
            failures.append(f"invalid SHA-256: {relative_raw}")
            continue
        if not path.is_file():
            failures.append(f"missing: {relative_raw}")
            continue
        if path.stat().st_size != expected_bytes:
            failures.append(f"size mismatch: {relative_raw}")
        actual = digest(path)
        if actual != expected_digest:
            failures.append(f"checksum mismatch: {relative_raw}")

    suite_gate = payload.get("suite_gate_report")
    if not isinstance(suite_gate, dict):
        failures.append("missing suite_gate_report binding")
    else:
        gate_path = suite_gate.get("path")
        matching = next((item for item in entries if item.get("path") == gate_path), None)
        if matching is None:
            failures.append("suite gate report is not a listed artifact")
        elif matching.get("sha256") != suite_gate.get("sha256"):
            failures.append("suite gate report hash binding mismatch")
        if suite_gate.get("verdict") not in {"PASS", "RELEASED"}:
            failures.append("suite gate report verdict is not passing")

    if not args.allow_extra and root.is_dir():
        manifest_relative = None
        try:
            manifest_relative = manifest_path.relative_to(root).as_posix()
        except ValueError:
            pass
        actual_paths = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path.relative_to(root).as_posix() != manifest_relative
        }
        for extra in sorted(actual_paths - listed_paths):
            failures.append(f"unlisted extra file: {extra}")
    if failures:
        print(f"FAIL: {len(failures)} manifest issue(s)")
        for failure in failures:
            print(failure)
        return 2
    print(f"PASS: verified {len(entries)} file record(s)")
    return 0


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)
    create_parser = sub.add_parser("create")
    create_parser.add_argument("--root", required=True)
    create_parser.add_argument("--output", required=True)
    create_parser.add_argument("--part-number", required=True)
    create_parser.add_argument("--revision", required=True)
    create_parser.add_argument("--configuration", required=True)
    create_parser.add_argument("--artifact-metadata", required=True)
    create_parser.add_argument("--suite-gate-report", required=True)
    create_parser.add_argument("--force", action="store_true")
    create_parser.add_argument("files", nargs="+")
    create_parser.set_defaults(func=create)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--root", required=True)
    verify_parser.add_argument(
        "--allow-extra",
        action="store_true",
        help="Do not fail on files absent from the manifest",
    )
    verify_parser.add_argument("manifest")
    verify_parser.set_defaults(func=verify)
    return top


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
