#!/usr/bin/env python3
"""Fail-closed integrity preflight for future HEB/B2/IAR-C runs.

This is intentionally standalone.  It does not import, modify, or rerun any
historical experiment code.  A manifest describes an explicit, relative file
set and the runner must call :func:`preflight_then_execute` before execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

SCHEMA = "acts-integrity-remediation/1"
SHA256_HEX = 64


@dataclass(frozen=True)
class VerificationReport:
    passed: bool
    errors: tuple[str, ...]
    checked_files: int

    def as_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "errors": list(self.errors),
                "checked_files": self.checked_files}


class PreflightError(RuntimeError):
    """Raised when execution was requested without a clean preflight."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _hash_ok(value: Any) -> bool:
    return isinstance(value, str) and len(value) == SHA256_HEX and all(
        char in "0123456789abcdef" for char in value
    )


def _relative(root: Path, value: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value or "\x00" in value:
        errors.append(f"unsafe path for {label}")
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        errors.append(f"unsafe path for {label}: {value!r}")
        return None
    cursor = root
    for part in candidate.parts:
        cursor /= part
        if cursor.is_symlink():
            errors.append(f"symlink in path for {label}: {value!r}")
            return None
    resolved_root = root.resolve()
    resolved = (root / candidate).resolve(strict=False)
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        errors.append(f"path escapes repository for {label}: {value!r}")
        return None
    return resolved


def _declared_file(root: Path, spec: Any, label: str,
                   errors: list[str], seen: set[Path]) -> tuple[Path, str] | None:
    if not isinstance(spec, Mapping) or set(spec) != {"path", "sha256"}:
        errors.append(f"{label} must contain exactly path and sha256")
        return None
    path = _relative(root, spec["path"], label, errors)
    if not _hash_ok(spec["sha256"]):
        errors.append(f"invalid sha256 for {label}")
    if path is None or not _hash_ok(spec["sha256"]):
        return None
    if path in seen:
        errors.append(f"duplicate file declaration: {spec['path']}")
    seen.add(path)
    if not path.exists():
        errors.append(f"missing file for {label}: {spec['path']}")
    elif path.is_symlink() or not path.is_file():
        errors.append(f"not a regular non-symlink file for {label}: {spec['path']}")
    elif _sha256(path) != spec["sha256"]:
        errors.append(f"hash mismatch for {label}: {spec['path']}")
    return path, spec["sha256"]


def _inventory(root: Path, spec: Any, errors: list[str], seen: set[Path]) -> int:
    if not isinstance(spec, Mapping):
        errors.append("case_inventory must be an object")
        return 0
    if set(spec) != {"root", "files", "count"}:
        errors.append("case_inventory must contain exactly root, files, count")
        return 0
    case_root = _relative(root, spec["root"], "case_inventory.root", errors)
    files = spec["files"]
    if case_root is None:
        return 0
    if not case_root.is_dir():
        errors.append("case_inventory root is missing or not a directory")
        return 0
    if (not isinstance(files, Mapping) or isinstance(spec["count"], bool)
            or not isinstance(spec["count"], int)):
        errors.append("invalid case_inventory shape")
        return 0
    if spec["count"] != len(files):
        errors.append("case_inventory count does not equal declared file count")
    expected: dict[Path, str] = {}
    for rel, expected_hash in files.items():
        path = _relative(case_root, rel, f"case file {rel!r}", errors)
        if path is None or not _hash_ok(expected_hash):
            errors.append(f"invalid case file declaration: {rel!r}")
            continue
        if path in expected:
            errors.append(f"duplicate case file declaration: {rel!r}")
        expected[path] = expected_hash
        if path in seen:
            errors.append(f"case file overlaps declared component: {rel!r}")
        if not path.exists():
            errors.append(f"missing case file: {rel!r}")
        elif path.is_symlink() or not path.is_file():
            errors.append(f"case file is not a regular non-symlink file: {rel!r}")
        elif _sha256(path) != expected_hash:
            errors.append(f"case file hash mismatch: {rel!r}")
    actual: set[Path] = set()
    if case_root.exists():
        for path in case_root.rglob("*"):
            if path.is_symlink():
                errors.append(f"symlink in case inventory: {path.relative_to(case_root)}")
            elif path.is_file():
                actual.add(path.resolve())
    for path in sorted(actual - set(expected)):
        errors.append(f"unexpected case file: {path.relative_to(case_root)}")
    for path in sorted(set(expected) - actual):
        if path.exists():
            errors.append(f"declared case path is not a regular file: {path.relative_to(case_root)}")
    return len(expected)


def verify_manifest(manifest_path: Path, repo_root: Path) -> VerificationReport:
    """Verify a remediation manifest without executing any experiment code."""
    errors: list[str] = []
    checked = 0
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return VerificationReport(False, (f"cannot read manifest: {exc}",), 0)
    if not isinstance(raw, Mapping) or raw.get("schema") != SCHEMA:
        return VerificationReport(False, (f"schema must be {SCHEMA!r}",), 0)
    _check_sections(raw, errors)
    seen: set[Path] = set()
    for name in ("protocol", "measurement_runner"):
        if name in raw and _declared_file(repo_root, raw[name], name, errors, seen):
            checked += 1
    components = raw.get("components")
    if not isinstance(components, Mapping) or not components:
        errors.append("components must be a non-empty object")
    else:
        for name in sorted(components):
            if _declared_file(repo_root, components[name], f"component {name}", errors, seen):
                checked += 1
    labels_trust = raw.get("labels_trust")
    if not isinstance(labels_trust, Mapping) or set(labels_trust) != {"labels", "trust"}:
        errors.append("labels_trust must contain exactly labels and trust")
    else:
        for name in ("labels", "trust"):
            if _declared_file(repo_root, labels_trust[name], name, errors, seen):
                checked += 1
    checked += _inventory(repo_root, raw.get("case_inventory"), errors, seen)
    return VerificationReport(not errors, tuple(errors), checked)


def _check_sections(manifest: Mapping[str, Any], errors: list[str]) -> None:
    required = {"schema", "protocol", "measurement_runner", "components",
                "labels_trust", "case_inventory"}
    missing = required - set(manifest)
    if missing:
        errors.append("missing manifest sections: " + ", ".join(sorted(missing)))


def preflight_then_execute(manifest_path: Path, repo_root: Path,
                           execute: Callable[[], Any]) -> Any:
    """Run *execute* only after a successful, complete integrity preflight."""
    report = verify_manifest(manifest_path, repo_root)
    if not report.passed:
        raise PreflightError("integrity preflight failed: " + "; ".join(report.errors))
    return execute()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("repo_root", type=Path)
    args = parser.parse_args(argv)
    report = verify_manifest(args.manifest, args.repo_root)
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
