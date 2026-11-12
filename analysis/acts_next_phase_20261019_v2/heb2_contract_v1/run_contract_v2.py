#!/usr/bin/env python3
"""Run Contract V2 over the frozen 22-case inventory under both semantics.

Sequence (preregistration §5):
1. provision fresh issuer keys and a trust bundle for this stage;
2. write the freeze manifest and verify it fail-closed with the audited
   ``heb1_remediation_v1/integrity/manifest_verifier.py``;
3. execute the frozen inventory with the frozen trusted components;
4. evaluate every produced certificate under both preregistered semantics,
   over identical evidence;
5. run the mechanized soundness check.

One run.  No re-run with modified configuration.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PHASE_ROOT = HERE.parent
STAGE1_ROOT = PHASE_ROOT / "stage1_e2a"
REPO_ROOT = PHASE_ROOT.parents[2]
STAGE1_REL = "sp2027/analysis/acts_next_phase_20261019_v2/stage1_e2a"
HEB2_REL = "sp2027/analysis/acts_next_phase_20261019_v2/heb2_contract_v1"
RUNS_ROOT = HERE / "runs"
TRUST_DIR = HERE / "trust"
KEYS_DIR = Path("/tmp/acts_heb2_keys")
FREEZE_PATH = HERE / "FREEZE.json"

sys.path.insert(0, str(STAGE1_ROOT))
sys.path.insert(0, str(HERE))

from e2a import canonical, remediation  # noqa: E402
from e2a import prepare  # noqa: E402
from e2a import runner as e2a_runner  # noqa: E402

from contract import (  # noqa: E402
    SEMANTIC_COMPLETION,
    SEMANTIC_OUTPUT,
    ContractV2,
)

STAGE1_COMPONENTS = [
    "canonical", "remediation", "producers", "observer", "reference",
    "aggregator", "baseline", "cases", "truth", "adjudicate", "prepare",
]


def sha256_file(path: Path) -> str:
    return canonical.sha_file(path)


def declared(relative: str) -> dict[str, str]:
    return {"path": relative, "sha256": sha256_file(REPO_ROOT / relative)}


def write_freeze() -> Path:
    """Write the hash-pinned freeze manifest for this stage."""
    cases_dir = STAGE1_ROOT / "frozen" / "cases"
    case_files = {path.name: sha256_file(path) for path in sorted(cases_dir.iterdir())
                  if path.is_file()}
    components = {name: declared(f"{STAGE1_REL}/e2a/{name}.py") for name in STAGE1_COMPONENTS}
    components["contract_v2"] = declared(f"{HEB2_REL}/contract.py")
    components["soundness_check"] = declared(f"{HEB2_REL}/soundness_check.py")
    components["issuers_public"] = declared(f"{HEB2_REL}/trust/issuers_public.json")
    manifest = {
        "schema": "acts-integrity-remediation/1",
        "protocol": declared(f"{HEB2_REL}/PREREGISTRATION.md"),
        "measurement_runner": declared(f"{HEB2_REL}/run_contract_v2.py"),
        "components": components,
        "labels_trust": {
            "labels": declared(f"{STAGE1_REL}/frozen/labels.json"),
            "trust": declared(f"{HEB2_REL}/trust/trust_policy.json"),
        },
        "case_inventory": {
            "root": f"{STAGE1_REL}/frozen/cases",
            "files": case_files,
            "count": len(case_files),
        },
    }
    FREEZE_PATH.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return FREEZE_PATH


def evaluate_arms(run_dir: Path, bundle_path: Path, policy_path: Path) -> list[dict[str, Any]]:
    """Evaluate every produced certificate under both semantics."""
    contracts = {
        SEMANTIC_OUTPUT: ContractV2(bundle_path, policy_path, run_dir / "ledger_output.jsonl",
                                    SEMANTIC_OUTPUT),
        SEMANTIC_COMPLETION: ContractV2(bundle_path, policy_path, run_dir / "ledger_completion.jsonl",
                                        SEMANTIC_COMPLETION),
    }
    rows = []
    for case_dir in sorted((run_dir / "cases").iterdir()):
        certificate_path = case_dir / "certificate.e2a.json"
        if not certificate_path.is_file():
            continue
        certificate = json.loads(certificate_path.read_text())
        bundle = {"case_id": certificate["case_id"], "certificate": certificate}
        observation_status = None
        observation = certificate.get("evidence", {}).get("observation")
        if isinstance(observation, dict):
            observation_status = observation["record"]["payload"].get("execution_status")
        row: dict[str, Any] = {
            "case_id": certificate["case_id"],
            "execution_status": observation_status,
            "decisions": {},
        }
        for semantic, contract in contracts.items():
            decision = contract.evaluate(bundle)
            row["decisions"][semantic] = {
                "decision": decision["decision"],
                "reason": decision["reason"],
                "reason_family": decision["reason_family"],
            }
        row["semantic_changes_decision"] = (
            row["decisions"][SEMANTIC_OUTPUT]["decision"]
            != row["decisions"][SEMANTIC_COMPLETION]["decision"])
        rows.append(row)
    return rows


def main() -> int:
    if FREEZE_PATH.exists():
        raise SystemExit(f"refusing to overwrite {FREEZE_PATH}")
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = RUNS_ROOT / (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "_v2")
    if run_dir.exists():
        raise SystemExit(f"run directory already exists: {run_dir}")

    if KEYS_DIR.exists():
        # The issuer directory must hold exactly the keys for this run: a stale
        # key would be picked up by role lookup while the trust bundle describes
        # only the current one.
        shutil.rmtree(KEYS_DIR)
    trust = prepare.provision_trust(KEYS_DIR, TRUST_DIR)
    keys_dir = Path(trust["keys_dir"])
    bundle_path = Path(trust["bundle"])
    policy_path = Path(trust["policy"])

    freeze_path = write_freeze()
    verifier = remediation.manifest_verifier()
    preflight = verifier.verify_manifest(freeze_path, REPO_ROOT)
    (HERE / "preflight_report.json").write_text(
        json.dumps(preflight.as_dict(), sort_keys=True, indent=2) + "\n")
    if not preflight.passed:
        print(json.dumps(preflight.as_dict(), sort_keys=True, indent=2))
        raise SystemExit("preflight failed; execution aborted")

    e2a_runner.execute_run(run_dir, keys_dir, TRUST_DIR)
    arm_rows = evaluate_arms(run_dir, bundle_path, policy_path)

    differences = [row for row in arm_rows if row["semantic_changes_decision"]]
    confined = all(row["execution_status"] != "EXECUTED" for row in differences)
    results = {
        "schema": "acts-heb2-contract-v2/1",
        "run_dir": str(run_dir),
        "preflight": preflight.as_dict(),
        "freeze_sha256": sha256_file(freeze_path),
        "trust_bundle_sha256": sha256_file(bundle_path),
        "trust_policy_sha256": sha256_file(policy_path),
        "cases": len(arm_rows),
        "semantic_changes": [
            {"case_id": row["case_id"], "execution_status": row["execution_status"],
             "output": row["decisions"][SEMANTIC_OUTPUT],
             "completion": row["decisions"][SEMANTIC_COMPLETION]}
            for row in differences
        ],
        "semantic_change_confined_to_non_completed_executions": confined,
        "rows": arm_rows,
    }
    (run_dir / "contract_v2_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "cases": len(arm_rows),
        "semantic_changes": results["semantic_changes"],
        "confined": confined,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())