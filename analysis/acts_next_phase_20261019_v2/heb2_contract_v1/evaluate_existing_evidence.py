#!/usr/bin/env python3
"""Apply the frozen Contract V2 to already-produced evidence corpora.

This stage performs **no execution**.  It evaluates certificates that were
produced earlier, under a contract that was preregistered and hash-frozen
before those certificates existed.  Verification of the signed records needs
only the public trust bundle, so corpora whose issuer keys are gone can still
be re-evaluated exactly.

A separate freeze manifest and a fail-closed preflight cover this evaluation
stage; the evidence itself is not modified.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PHASE_ROOT = HERE.parent
STAGE1_ROOT = PHASE_ROOT / "stage1_e2a"
REPO_ROOT = PHASE_ROOT.parents[2]
STAGE1_REL = "sp2027/analysis/acts_next_phase_20261019_v2/stage1_e2a"
HEB2_REL = "sp2027/analysis/acts_next_phase_20261019_v2/heb2_contract_v1"
FREEZE_PATH = HERE / "FREEZE_EVALUATION.json"

sys.path.insert(0, str(STAGE1_ROOT))
sys.path.insert(0, str(HERE))

from e2a import canonical, remediation  # noqa: E402

from contract import (  # noqa: E402
    SEMANTIC_COMPLETION,
    SEMANTIC_OUTPUT,
    ContractV2,
    soundness_violations,
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
    cases_dir = STAGE1_ROOT / "frozen" / "cases"
    case_files = {path.name: sha256_file(path) for path in sorted(cases_dir.iterdir())
                  if path.is_file()}
    components = {name: declared(f"{STAGE1_REL}/e2a/{name}.py") for name in STAGE1_COMPONENTS}
    components["contract_v2"] = declared(f"{HEB2_REL}/contract.py")
    components["soundness_check_v2"] = declared(f"{HEB2_REL}/soundness_check_v2.py")
    manifest = {
        "schema": "acts-integrity-remediation/1",
        "protocol": declared(f"{HEB2_REL}/PREREGISTRATION.md"),
        "measurement_runner": declared(f"{HEB2_REL}/evaluate_existing_evidence.py"),
        "components": components,
        "labels_trust": {
            "labels": declared(f"{STAGE1_REL}/frozen/labels.json"),
            "trust": declared(f"{STAGE1_REL}/frozen/trust_policy.json"),
        },
        "case_inventory": {
            "root": f"{STAGE1_REL}/frozen/cases",
            "files": case_files,
            "count": len(case_files),
        },
    }
    FREEZE_PATH.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return FREEZE_PATH


def evaluate_corpus(name: str, run_dir: Path, trust_dir: Path) -> dict[str, Any]:
    """Evaluate one corpus's certificates under both semantics."""
    bundle_path = trust_dir / "issuers_public.json"
    policy_path = trust_dir / "trust_policy.json"
    contracts = {
        SEMANTIC_OUTPUT: ContractV2(bundle_path, policy_path, None, SEMANTIC_OUTPUT),
        SEMANTIC_COMPLETION: ContractV2(bundle_path, policy_path, None, SEMANTIC_COMPLETION),
    }
    rows = []
    for case_dir in sorted((run_dir / "cases").iterdir()):
        certificate_path = case_dir / "certificate.e2a.json"
        if not certificate_path.is_file():
            continue
        certificate = json.loads(certificate_path.read_text())
        bundle = {"case_id": certificate["case_id"], "certificate": certificate}
        observation = certificate.get("evidence", {}).get("observation")
        status = None
        if isinstance(observation, dict):
            status = observation["record"]["payload"].get("execution_status")
        row: dict[str, Any] = {"case_id": certificate["case_id"], "execution_status": status,
                               "decisions": {}, "soundness": {}}
        for semantic, contract in contracts.items():
            decision = contract.evaluate(bundle)
            row["decisions"][semantic] = {"decision": decision["decision"],
                                          "reason": decision["reason"]}
            # The soundness property constrains *accepted* bundles only; for a
            # bundle the contract refuses, the property is vacuous.
            row["soundness"][semantic] = (
                soundness_violations(bundle, semantic, bundle_path, policy_path)
                if decision["decision"] == "ATTRIBUTED_SUCCESS" else [])
        row["semantic_changes_decision"] = (
            row["decisions"][SEMANTIC_OUTPUT]["decision"]
            != row["decisions"][SEMANTIC_COMPLETION]["decision"])
        rows.append(row)
    changes = [row for row in rows if row["semantic_changes_decision"]]
    return {
        "corpus": name,
        "run_dir": str(run_dir),
        "trust_dir": str(trust_dir),
        "cases": len(rows),
        "attributed_output": sum(1 for row in rows
                                  if row["decisions"][SEMANTIC_OUTPUT]["decision"] == "ATTRIBUTED_SUCCESS"),
        "attributed_completion": sum(1 for row in rows
                                     if row["decisions"][SEMANTIC_COMPLETION]["decision"] == "ATTRIBUTED_SUCCESS"),
        "semantic_changes": [
            {"case_id": row["case_id"], "execution_status": row["execution_status"],
             "output": row["decisions"][SEMANTIC_OUTPUT],
             "completion": row["decisions"][SEMANTIC_COMPLETION]}
            for row in changes
        ],
        "changes_confined_to_non_completed_executions":
            all(row["execution_status"] != "EXECUTED" for row in changes),
        "soundness_violations": [
            {"case_id": row["case_id"], "semantic": semantic, "violations": violations}
            for row in rows for semantic, violations in row["soundness"].items() if violations
        ],
        "soundness_scope": "accepted bundles only; the property is vacuous for refused bundles",
        "rows": rows,
    }


def main() -> int:
    if FREEZE_PATH.exists():
        raise SystemExit(f"refusing to overwrite {FREEZE_PATH}")
    if len(sys.argv) != 3:
        raise SystemExit("usage: evaluate_existing_evidence.py <corpora.json> <out.json>")
    spec = json.loads(Path(sys.argv[1]).read_text())
    out_path = Path(sys.argv[2])

    freeze_path = write_freeze()
    verifier = remediation.manifest_verifier()
    preflight = verifier.verify_manifest(freeze_path, REPO_ROOT)
    (HERE / "preflight_report_evaluation.json").write_text(
        json.dumps(preflight.as_dict(), sort_keys=True, indent=2) + "\n")
    if not preflight.passed:
        print(json.dumps(preflight.as_dict(), sort_keys=True, indent=2))
        raise SystemExit("preflight failed; evaluation aborted")

    corpora = [evaluate_corpus(item["name"], Path(item["run_dir"]), Path(item["trust_dir"]))
               for item in spec["corpora"]]
    results = {
        "schema": "acts-heb2-evaluation/1",
        "preflight": preflight.as_dict(),
        "freeze_sha256": sha256_file(freeze_path),
        "corpora": corpora,
        "total_soundness_violations": sum(len(c["soundness_violations"]) for c in corpora),
    }
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "corpora": [{"corpus": c["corpus"], "cases": c["cases"],
                     "attributed_output": c["attributed_output"],
                     "attributed_completion": c["attributed_completion"],
                     "semantic_changes": [s["case_id"] for s in c["semantic_changes"]],
                     "confined": c["changes_confined_to_non_completed_executions"]}
                    for c in corpora],
        "total_soundness_violations": results["total_soundness_violations"],
    }, indent=2, sort_keys=True))
    return 0 if results["total_soundness_violations"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())