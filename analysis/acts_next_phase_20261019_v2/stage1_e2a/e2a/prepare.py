"""Pre-execution preparation: trust provisioning, frozen artefacts, freeze manifest.

This script runs **once**, before the confirmatory execution.  It:

1. provisions three fresh random Ed25519 issuer keys (one per trusted role)
   into a 0700 private directory, using the audited ``protected_signing``
   primitives.  The private keys are never hashed into the freeze manifest and
   never enter any research artifact;
2. writes the frozen public trust bundle and the frozen issuer policy;
3. writes the frozen case inventory (22 case files) and the frozen label
   table;
4. writes ``E2A_FREEZE.json`` in the schema required by the audited
   remediation preflight component
   (``heb1_remediation_v1/integrity/manifest_verifier.py``).

The freeze manifest is verified fail-closed by that audited component before
the runner is allowed to execute.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from e2a import canonical, cases, remediation
else:
    from . import canonical, cases, remediation

STAGE1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = STAGE1_ROOT.parents[3]
STAGE1_REL = "sp2027/analysis/acts_next_phase_20261019_v2/stage1_e2a"

COMPONENTS = [
    "canonical", "remediation", "producers", "observer", "reference",
    "aggregator", "baseline", "cases", "truth", "adjudicate", "prepare",
]


def provision_trust(keys_dir: Path, trust_dir: Path) -> dict[str, Any]:
    """Create fresh issuer keys and write the public bundle and the policy.

    Private keys must be readable only by their owner (0600) because the audited
    ``protected_signing.load_private_key`` rejects group/world-readable keys.
    Some mounts (e.g. fuseblk) silently ignore ``chmod`` and leave every file
    at 0777, which would make key loading fail at execution time.  On such
    mounts the keys are provisioned on a permission-enforcing tmpfs under
    ``/tmp`` and the effective keys directory is returned so callers can point
    the runner at it.
    """
    signing = remediation.protected_signing()
    keys_dir = Path(keys_dir)
    trust_dir = Path(trust_dir)
    trust_dir.mkdir(parents=True, exist_ok=True)

    def _can_chmod(path: Path) -> bool:
        probe = path / ".perm_probe"
        try:
            probe.write_text("x", encoding="utf-8")
            os.chmod(probe, 0o600)
            ok = (probe.stat().st_mode & 0o077) == 0
        except OSError:
            ok = False
        finally:
            try:
                probe.unlink()
            except OSError:
                pass
        return ok

    if _can_chmod(keys_dir.parent if keys_dir.parent.exists() else keys_dir):
        effective_keys = keys_dir
    else:
        effective_keys = Path(tempfile.mkdtemp(prefix="e2a_keys_"))
        os.chmod(effective_keys, 0o700)

    effective_keys.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(effective_keys, 0o700)
    except OSError:
        pass

    issuers = []
    for role in (remediation.ROLE_OBSERVER, remediation.ROLE_REFERENCE, remediation.ROLE_AGGREGATOR):
        issuers.append(signing.generate_issuer(effective_keys, role))
    bundle_path = trust_dir / "issuers_public.json"
    signing.write_public_bundle(bundle_path, issuers)

    policy = {
        "schema": "e2a-issuer-policy/1",
        "roles": {
            remediation.ROLE_OBSERVER: {"kinds": [canonical.OBSERVATION_KIND],
                                        "contexts": [canonical.POLICY_CONTEXT]},
            remediation.ROLE_REFERENCE: {"kinds": [canonical.REFERENCE_KIND],
                                         "contexts": [canonical.POLICY_CONTEXT]},
            remediation.ROLE_AGGREGATOR: {"kinds": [canonical.CLAIM_KIND],
                                          "contexts": [canonical.POLICY_CONTEXT]},
        },
        "notes": "The allow-list context is a fixed namespace string. The per-case six-field "
                 "binding is carried inside every signed payload and is additionally signed by "
                 "the audited context_validator component.",
    }
    (trust_dir / "trust_policy.json").write_text(json.dumps(policy, sort_keys=True, indent=2) + "\n")
    return {"bundle": str(bundle_path), "policy": str(trust_dir / "trust_policy.json"),
            "issuer_count": len(issuers),
            "key_ids": [issuer["key_id"] for issuer in issuers],
            "keys_dir": str(effective_keys)}


def write_frozen_artifacts(frozen_dir: Path, trust_dir: Path) -> dict[str, Any]:
    frozen_dir = Path(frozen_dir)
    cases_dir = frozen_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    frozen_dir.chmod(0o755)

    labels = cases.label_table()
    (frozen_dir / "labels.json").write_text(json.dumps(labels, sort_keys=True, indent=2) + "\n")
    (frozen_dir / "trust_policy.json").write_text(
        (Path(trust_dir) / "trust_policy.json").read_text(encoding="utf-8"))
    (frozen_dir / "issuers_public.json").write_text(
        (Path(trust_dir) / "issuers_public.json").read_text(encoding="utf-8"))

    index = []
    for ordinal, case in enumerate(cases.CASES, start=1):
        name = f"{ordinal:02d}_{case['case_id']}.json"
        path = cases_dir / name
        path.write_text(json.dumps(case, sort_keys=True, indent=2) + "\n")
        index.append({"ordinal": ordinal, "case_id": case["case_id"], "file": name,
                      "case_class": case["case_class"], "gt_success": case["gt_success"]})
    (frozen_dir / "case_index.json").write_text(json.dumps(
        {"schema": "e2a-case-index/1", "case_count": len(index), "cases": index},
        sort_keys=True, indent=2) + "\n")
    return {"labels": str(frozen_dir / "labels.json"),
            "policy": str(frozen_dir / "trust_policy.json"),
            "bundle": str(frozen_dir / "issuers_public.json"),
            "case_files": len(index)}


def _declared(root: Path, relative: str) -> dict[str, str]:
    return {"path": relative, "sha256": canonical.sha_file(root / relative)}


def write_manifest(stage1_root: Path, repo_root: Path, frozen_dir: Path) -> Path:
    stage1_root = Path(stage1_root)
    repo_root = Path(repo_root)
    cases_dir = Path(frozen_dir) / "cases"
    case_files = {path.name: canonical.sha_file(path) for path in sorted(cases_dir.iterdir())
                  if path.is_file()}
    components = {name: _declared(repo_root, f"{STAGE1_REL}/e2a/{name}.py")
                  for name in COMPONENTS}
    # The deviations log is part of the frozen artifact set (prereg v1.1 §12.9),
    # so that its content is hash-pinned by the audited manifest verifier.
    components["deviations_log"] = _declared(repo_root, f"{STAGE1_REL}/E2A_DEVIATIONS.md")
    manifest = {
        "schema": "acts-integrity-remediation/1",
        "protocol": _declared(repo_root, f"{STAGE1_REL}/E2A_PREREGISTRATION.md"),
        "measurement_runner": _declared(repo_root, f"{STAGE1_REL}/e2a/runner.py"),
        "components": components,
        "labels_trust": {
            "labels": _declared(repo_root, f"{STAGE1_REL}/frozen/labels.json"),
            "trust": _declared(repo_root, f"{STAGE1_REL}/frozen/trust_policy.json"),
        },
        "case_inventory": {
            "root": f"{STAGE1_REL}/frozen/cases",
            "files": case_files,
            "count": len(case_files),
        },
    }
    manifest_path = stage1_root / "E2A_FREEZE.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return manifest_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="E2A pre-execution preparation")
    parser.add_argument("--stage1-root", type=Path, default=STAGE1_ROOT)
    parser.add_argument("--keys", type=Path, default=STAGE1_ROOT / "keys")
    parser.add_argument("--trust", type=Path, default=STAGE1_ROOT / "frozen")
    parser.add_argument("--frozen", type=Path, default=STAGE1_ROOT / "frozen")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    trust = provision_trust(args.keys, args.trust)
    frozen = write_frozen_artifacts(args.frozen, args.trust)
    manifest_path = write_manifest(args.stage1_root, args.repo_root, args.frozen)

    # Fail-closed preflight using the audited remediation component.
    verifier = remediation.manifest_verifier()
    report = verifier.verify_manifest(manifest_path, args.repo_root)
    (args.stage1_root / "preflight_report_prestage.json").write_text(
        json.dumps(report.as_dict(), sort_keys=True, indent=2) + "\n")
    print(json.dumps({"trust": trust, "frozen": frozen, "manifest": str(manifest_path),
                      "preflight": report.as_dict(), "keys_dir": trust.get("keys_dir")},
                     sort_keys=True, indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
