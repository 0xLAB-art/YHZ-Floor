#!/usr/bin/env python3
"""Matched translation, corrected: the identical E2A evidence through the
upstream models, each given the guarantees it was designed to provide.

Arms
----
``acts``                    the frozen ACTS aggregator (reference decision);
``in_toto_default``         an in-toto link + a layout with one step and **no**
                             artifact rules and **no** inspection.  This is the
                             *minimally configured* deployment: it establishes
                             authenticity, functionary authorization, threshold
                             and command alignment, and nothing else;
``in_toto_policy``          the same, with in-toto's own artifact rules
                             (REQUIRE) **and** an inspection that runs an
                             **independent** verification policy — one that
                             imports nothing from the ACTS aggregator and
                             adjudicates the predicate with the project's frozen
                             Stage 01 reference verifier;
``in_toto_policy_stateful`` the same policy inspection, but with a shared,
                             file-backed ledger, so the inspection is stateful
                             across cases;
``in_toto_acts_integration`` an inspection that calls the ACTS aggregator
                             itself.  This is an **integration test**, not an
                             independent baseline;
``slsa``                    a SLSA v1.0 provenance statement verified with
                             ``slsa-verifier``.  Recorded with the stage at
                             which verification stopped.

The guarantee ladder (used for the per-case classification) is

    G0 no evidence binding -> G1 authenticity + authority -> G2 artifact rules
    -> G3 digest/context binding -> G4 independently recomputed predicate
    -> G5 cross-case replay protection
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PHASE_ROOT = HERE.parent
STAGE1_ROOT = PHASE_ROOT / "stage1_e2a"
DELIVERABLES = PHASE_ROOT / "research" / "deliverables"
VENV = DELIVERABLES / ".venv"
HEB2_ROOT = PHASE_ROOT / "heb2_contract_v1"
CORPUS_RUN = HEB2_ROOT / "runs" / "20261020T091958Z_v2"
CORPUS_TRUST = HEB2_ROOT / "trust"
WORK_ROOT = HERE / "work"
RESULTS_PATH = HERE / "translation_results_v2.json"
ADAPTER = HERE / "delegation_adapter.py"
INDEPENDENT_POLICY = HERE / "independent_policy.py"
STEP_NAME = "execute"
GUARANTEE_ORDER = ("G0", "G1", "G2", "G3", "G4", "G5")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def presented_evidence(certificate: dict[str, Any]) -> tuple[dict[str, Any] | None,
                                                             dict[str, Any] | None]:
    """The evidence **as presented in the certificate**, not as found on disk."""
    evidence = certificate.get("evidence") or {}
    return evidence.get("observation"), evidence.get("reference")


def link_body(certificate: dict[str, Any], observation: dict[str, Any] | None) -> dict[str, Any]:
    """The presented claim, translated into an in-toto link."""
    materials: dict[str, Any] = {}
    products: dict[str, Any] = {}
    command: list[str] = []
    byproducts: dict[str, Any] = {}
    if observation is not None:
        payload = observation["record"]["payload"]
        materials["program_source.py"] = {"sha256": payload["program_source_sha256"]}
        materials["public_instance.json"] = {"sha256": payload["public_target_digest"]}
        command = payload.get("command") or []
        byproducts["execution_status"] = payload.get("execution_status")
        byproducts["context"] = observation.get("context")
        byproducts["observation_sha256"] = sha256_bytes(
            json.dumps(observation, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        observed = payload.get("parse", {}).get("parsed_candidate_sha256")
        if observed is not None:
            products["candidate_output.json"] = {"sha256": observed}
    return {
        "_type": "link",
        "name": STEP_NAME,
        "command": command,
        "environment": {},
        "materials": materials,
        "products": products,
        "byproducts": byproducts,
    }


def layout_body(keyid: str, key_dict: dict[str, Any], command: list[str],
                rules: bool, inspection: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """The claim, translated into an in-toto layout.

    ``rules`` switches in in-toto's own artifact rules (REQUIRE), which bind
    *which* artifacts must be present.  in-toto's rules bind names; the
    digests and the policy are the inspection's business.
    """
    expected_materials = ([["REQUIRE", "program_source.py"],
                           ["REQUIRE", "public_instance.json"]] if rules else [])
    expected_products = ([["REQUIRE", "candidate_output.json"]] if rules else [])
    return {
        "_type": "layout",
        "steps": [{
            "_type": "step",
            "name": STEP_NAME,
            "pubkeys": [keyid],
            "expected_command": command,
            "expected_materials": expected_materials,
            "expected_products": expected_products,
            "threshold": 1,
        }],
        "inspect": inspection or [],
        "keys": {keyid: key_dict},
        "expires": "2035-01-01T00:00:00Z",
        "readme": "matched translation of the ACTS attribution claim",
    }


def slsa_statement(certificate: dict[str, Any], observation: dict[str, Any] | None) -> dict[str, Any]:
    """The presented claim, translated into a SLSA v1.0 provenance statement."""
    subject_digest = sha256_bytes(b"")
    context = {"target_id": "", "attempt_id": "", "epoch": 0}
    if observation is not None:
        payload = observation["record"]["payload"]
        context = observation.get("context", context)
        observed = payload.get("parse", {}).get("parsed_candidate_sha256")
        if observed is not None:
            subject_digest = observed
    return {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "candidate_output.json", "digest": {"sha256": subject_digest}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://acts-attack.invalid/e2a-attribution/v1",
                "externalParameters": {
                    "target_id": context.get("target_id"),
                    "attempt_id": context.get("attempt_id"),
                    "epoch": context.get("epoch"),
                },
                "internalParameters": {},
            },
            "runDetails": {
                "builder": {"id": "https://acts-attack.invalid/e2a-aggregator/v1"},
                "metadata": {"invocationId": context.get("attempt_id")},
            },
        },
    }


def sign(path: Path, private_key: Path) -> subprocess.CompletedProcess:
    """Sign metadata with in-toto-sign (which writes into the working directory)."""
    return subprocess.run([str(VENV / "bin" / "in-toto-sign"), "-f", str(path), "-k", str(private_key)],
                          capture_output=True, text=True, cwd=str(path.parent))


def verify(layout_path: Path, public_key: Path, link_dir: Path) -> dict[str, Any]:
    result = subprocess.run(
        [str(VENV / "bin" / "in-toto-verify"), "--layout", str(layout_path),
         "--verification-keys", str(public_key), "--link-dir", str(link_dir)],
        capture_output=True, text=True, cwd=str(layout_path.parent))
    return {"returncode": result.returncode,
            "stdout": result.stdout[-1500:], "stderr": result.stderr[-1500:]}


def run_slsa(statement_path: Path, candidate_path: Path) -> dict[str, Any]:
    """Verify the SLSA statement with network access, recording where it stops."""
    try:
        result = subprocess.run(
            [str(DELIVERABLES / ".bin" / "slsa-verifier"), "verify-artifact",
             "--provenance-path", str(statement_path),
             "--source-uri", "github.com/dragonked2/ACTS-Attack", str(candidate_path)],
            capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired:
        return {"returncode": 124, "stdout": "", "stderr": "timeout",
                "stage": "timeout"}
    stderr = result.stderr[-1500:]
    stage = "unknown"
    if "tuf refresh failed" in stderr or "tuf-repo-cdn" in stderr:
        stage = "trust-root-refresh"
    elif "rekor" in stderr.lower() or "no matching entries" in stderr.lower():
        stage = "provenance-acquisition-rekor"
    elif "certificate" in stderr.lower() or "identity" in stderr.lower():
        stage = "signature-or-identity"
    elif result.returncode == 0:
        stage = "verified"
    return {"returncode": result.returncode, "stdout": result.stdout[-1500:],
            "stderr": stderr, "stage": stage}


def main() -> int:
    parser = argparse.ArgumentParser(description="matched translation, corrected")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--work", type=Path, default=WORK_ROOT)
    args = parser.parse_args()
    if RESULTS_PATH.exists():
        raise SystemExit(f"refusing to overwrite {RESULTS_PATH}")

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from in_toto.models._signer import load_public_key_from_file

    key = Ed25519PrivateKey.generate()
    # A fresh work root per run: link files from an earlier run would otherwise
    # be picked up by in-toto-verify and corrupt the per-case link set.
    import time as _time
    run_work = args.work / _time.strftime("%Y%m%dT%H%M%SZ", _time.gmtime())
    run_work.mkdir(parents=True, exist_ok=True)
    args.work = run_work
    private_key = args.work / "intoto_key.pem"
    private_key.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                              serialization.PrivateFormat.PKCS8,
                                              serialization.NoEncryption()))
    public_key = args.work / "intoto_key.pub.pem"
    public_key.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    key_dict = load_public_key_from_file(str(public_key))

    sys.path.insert(0, str(HEB2_ROOT))
    from contract import ContractV2

    # The reference decision is ledger-bearing and processed in the corpus order,
    # so the cross-case replay check is active exactly as it was when the corpus
    # was produced.
    acts_contracts = {
        semantic: ContractV2(CORPUS_TRUST / "issuers_public.json",
                             CORPUS_TRUST / "trust_policy.json",
                             args.work / f"acts_ledger_{semantic}.jsonl", semantic)
        for semantic in ("output", "completion")
    }

    case_dirs = sorted((CORPUS_RUN / "cases").iterdir())
    if args.limit:
        case_dirs = case_dirs[:args.limit]

    rows = []
    for case_dir in case_dirs:
        case_id = case_dir.name
        certificate = json.loads((case_dir / "certificate.e2a.json").read_text())
        observation, reference = presented_evidence(certificate)
        bundle = {"case_id": certificate["case_id"], "certificate": certificate}

        work = args.work / case_id
        link_dir = work / "links"
        link_dir.mkdir(parents=True, exist_ok=True)
        link_file = work / f"{STEP_NAME}.link"
        link_file.write_text(json.dumps(
            {"signatures": [], "signed": link_body(certificate, observation)}, indent=2) + "\n")
        sign(link_file, private_key)
        for produced in work.glob(f"{STEP_NAME}.*.link"):
            produced.rename(link_dir / produced.name)
        signed_links = list(link_dir.glob("*.link"))
        if not signed_links:
            raise RuntimeError(f"in-toto-sign produced no signed link for {case_id}")
        keyid = signed_links[0].stem.split(".")[-1]
        command = link_body(certificate, observation)["command"]

        def write_layout(name: str, rules: bool, inspection: list[dict[str, Any]] | None) -> Path:
            path = work / name
            path.write_text(json.dumps(
                {"signatures": [], "signed": layout_body(keyid, key_dict, command, rules, inspection)},
                indent=2) + "\n")
            sign(path, private_key)
            return path

        default_layout = write_layout("layout_default.json", False, None)
        default_result = verify(default_layout, public_key, link_dir)

        policy_inspection = [{
            "_type": "inspection", "name": "adjudicate",
            "run": [sys.executable, str(INDEPENDENT_POLICY), str(case_dir),
                    str(CORPUS_TRUST / "issuers_public.json"),
                    str(CORPUS_TRUST / "trust_policy.json"), "-"],
        }]
        policy_layout = write_layout("layout_policy.json", True, policy_inspection)
        policy_result = verify(policy_layout, public_key, link_dir)

        stateful_inspection = [{
            "_type": "inspection", "name": "adjudicate",
            "run": [sys.executable, str(INDEPENDENT_POLICY), str(case_dir),
                    str(CORPUS_TRUST / "issuers_public.json"),
                    str(CORPUS_TRUST / "trust_policy.json"),
                    str(args.work / "shared_replay_ledger.jsonl")],
        }]
        stateful_layout = write_layout("layout_policy_stateful.json", True, stateful_inspection)
        stateful_result = verify(stateful_layout, public_key, link_dir)

        integration_inspection = [{
            "_type": "inspection", "name": "adjudicate",
            "run": [sys.executable, str(ADAPTER), str(case_dir / "certificate.e2a.json"),
                    str(CORPUS_TRUST / "issuers_public.json"),
                    str(CORPUS_TRUST / "trust_policy.json")],
        }]
        integration_layout = write_layout("layout_integration.json", True, integration_inspection)
        integration_result = verify(integration_layout, public_key, link_dir)

        statement_path = work / "provenance.json"
        statement_path.write_text(json.dumps(
            {"signatures": [], "signed": slsa_statement(certificate, observation)}, indent=2) + "\n")
        slsa = run_slsa(statement_path, case_dir / "candidate_output.json")

        acts = {}
        for semantic, contract in acts_contracts.items():
            decision = contract.evaluate(bundle)
            acts[semantic] = {"decision": decision["decision"], "reason": decision["reason"]}

        rows.append({
            "case_id": case_id,
            "acts": acts,
            "in_toto_default": {"accepted": default_result["returncode"] == 0,
                                "returncode": default_result["returncode"],
                                "stderr": default_result["stderr"][-400:]},
            "in_toto_policy": {"accepted": policy_result["returncode"] == 0,
                               "returncode": policy_result["returncode"],
                               "stderr": policy_result["stderr"][-400:]},
            "in_toto_policy_stateful": {"accepted": stateful_result["returncode"] == 0,
                                        "returncode": stateful_result["returncode"],
                                        "stderr": stateful_result["stderr"][-400:]},
            "in_toto_acts_integration": {"accepted": integration_result["returncode"] == 0,
                                         "returncode": integration_result["returncode"],
                                         "stderr": integration_result["stderr"][-400:]},
            "slsa": {"accepted": slsa["returncode"] == 0, "returncode": slsa["returncode"],
                     "stage": slsa["stage"], "stderr": slsa["stderr"][-400:]},
        })

    results = {
        "schema": "acts-stage6-matched-translation-v2/1",
        "corpus_run": str(CORPUS_RUN),
        "cases": len(rows),
        "guarantee_ladder": list(GUARANTEE_ORDER),
        "independent_policy_loc": len(INDEPENDENT_POLICY.read_text().splitlines()),
        "integration_adapter_loc": len(ADAPTER.read_text().splitlines()),
        "acts_aggregator_loc": len((STAGE1_ROOT / "e2a" / "aggregator.py").read_text().splitlines()),
        "rows": rows,
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "cases": len(rows),
        "acts_output_attributed": sum(
            r["acts"]["output"]["decision"] == "ATTRIBUTED_SUCCESS" for r in rows),
        "in_toto_default_accepted": sum(r["in_toto_default"]["accepted"] for r in rows),
        "in_toto_policy_accepted": sum(r["in_toto_policy"]["accepted"] for r in rows),
        "in_toto_policy_stateful_accepted": sum(
            r["in_toto_policy_stateful"]["accepted"] for r in rows),
        "in_toto_acts_integration_accepted": sum(
            r["in_toto_acts_integration"]["accepted"] for r in rows),
        "slsa_accepted": sum(r["slsa"]["accepted"] for r in rows),
        "slsa_stages": sorted({r["slsa"]["stage"] for r in rows}),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())