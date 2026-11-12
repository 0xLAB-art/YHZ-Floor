#!/usr/bin/env python3
"""Write the Stage 1 integrity manifest and verify it with the audited preflight.

The manifest is written in the schema of the vetted remediation component
``heb1_remediation_v1/integrity/manifest_verifier.py``
(``acts-integrity-remediation/1``) and is verified with that same component,
unmodified.  The runner refuses to start unless the preflight passes.

Usage:
    python3 s1_freeze.py            # write the manifest and verify it
    python3 s1_freeze.py --verify   # verify the existing manifest only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import s1_common  # noqa: E402  (installs the remediation component paths)

from manifest_verifier import verify_manifest  # noqa: E402

STAGE1_ROOT = Path(__file__).resolve().parent
REPO_ROOT = s1_common.REPO_ROOT
INVENTORY_ROOT = STAGE1_ROOT / "s1_case_inventory"
MANIFEST_PATH = STAGE1_ROOT / "s1_integrity_manifest.json"

PROTOCOL = STAGE1_ROOT / "s1_protocol.md"
DEVIATIONS = STAGE1_ROOT / "s1_deviations.md"
RUNNER = STAGE1_ROOT / "s1_runner.py"
LABELS = STAGE1_ROOT / "s1_case_manifest.json"
TRUST = STAGE1_ROOT / "trust" / "public_bundle.json"

COMPONENTS = {
    "s1_common": STAGE1_ROOT / "s1_common.py",
    "s1_cases": STAGE1_ROOT / "s1_cases.py",
    "s1_make_cases": STAGE1_ROOT / "s1_make_cases.py",
    "s1_freeze": STAGE1_ROOT / "s1_freeze.py",
    "s1_summarize": STAGE1_ROOT / "s1_summarize.py",
    "s1_setup_trust": STAGE1_ROOT / "s1_setup_trust.py",
    "s1_trusted_observer": STAGE1_ROOT / "s1_trusted_observer.py",
    "s1_reference_verifier": STAGE1_ROOT / "s1_reference_verifier.py",
    "s1_verification": STAGE1_ROOT / "s1_verification.py",
    "s1_attribution_evaluator": STAGE1_ROOT / "s1_attribution_evaluator.py",
    "s1_baseline_evaluators": STAGE1_ROOT / "s1_baseline_evaluators.py",
    "s1_stage01_compat": STAGE1_ROOT / "s1_stage01_compat.py",
    "deviations_log": DEVIATIONS,
    "test_suite": STAGE1_ROOT / "test_s1_attribution.py",
    # Frozen historical components the experiment depends on (read-only).
    "frozen_stage01_validator": s1_common.FROZEN_STAGE01_VALIDATOR,
    "frozen_stage01_reference_verifier": s1_common.FROZEN_REFERENCE_VERIFIER,
    "frozen_fixture_generator": s1_common.FROZEN_FIXTURE_GENERATOR,
}


def rel(path: Path) -> str:
    return str(Path(path).resolve().relative_to(REPO_ROOT.resolve()))


def entry(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": s1_common.sha256_file(path)}


def inventory_files() -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(INVENTORY_ROOT.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"symlink in case inventory: {path}")
        if path.is_file():
            files[str(path.relative_to(INVENTORY_ROOT))] = s1_common.sha256_file(path)
    return files


def build_manifest() -> dict:
    files = inventory_files()
    missing = [p for p in (PROTOCOL, DEVIATIONS, RUNNER, LABELS, TRUST) if not p.is_file()]
    if missing:
        raise RuntimeError(f"cannot freeze; missing artefacts: {missing}")
    if not files:
        raise RuntimeError("cannot freeze; the case inventory is empty")
    components = {}
    for name, path in COMPONENTS.items():
        if not path.is_file():
            raise RuntimeError(f"cannot freeze; component missing: {name} -> {path}")
        components[name] = entry(path)
    return {
        "schema": "acts-integrity-remediation/1",
        "protocol": entry(PROTOCOL),
        "measurement_runner": entry(RUNNER),
        "components": components,
        "labels_trust": {"labels": entry(LABELS), "trust": entry(TRUST)},
        "case_inventory": {
            "root": rel(INVENTORY_ROOT),
            "files": files,
            "count": len(files),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true",
                        help="verify the existing manifest without rewriting it")
    args = parser.parse_args(argv)

    if not args.verify:
        manifest = build_manifest()
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(f"wrote {MANIFEST_PATH}")

    report = verify_manifest(MANIFEST_PATH, REPO_ROOT)
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
