#!/usr/bin/env python3
"""Matched translation: run the identical E2A evidence through in-toto and SLSA.

Four arms, one corpus, one evidence set:

* ``acts``             — the frozen ACTS aggregator (reference decision);
* ``in_toto_native``   — an in-toto link + layout with no artifact rules and no
                         inspection: the upstream model as it comes;
* ``in_toto_delegated``— the same, plus one inspection that applies the ACTS
                         policy through an external program;
* ``slsa``             — a SLSA v1.0 provenance statement verified with
                         ``slsa-verifier``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = Path(__file__).resolve().parent
PHASE_ROOT = HERE.parent
STAGE1_ROOT = PHASE_ROOT / "stage1_e2a"
DELIVERABLES = PHASE_ROOT / "research" / "deliverables"
VENV = DELIVERABLES / ".venv"
HEB2_ROOT = PHASE_ROOT / "heb2_contract_v1"
CORPUS_RUN = HEB2_ROOT / "runs" / "20261020T091958Z_v2"
CORPUS_TRUST = HEB2_ROOT / "trust"
WORK_ROOT = HERE / "work"
RESULTS_PATH = HERE / "translation_results.json"

sys.path.insert(0, str(STAGE1_ROOT))
sys.path.insert(0, str(HEB2_ROOT))

from contract import SEMANTIC_COMPLETION, SEMANTIC_OUTPUT, ContractV2  # noqa: E402
from in_toto.models._signer import load_public_key_from_file  # noqa: E402

IN_TOTO_SIGN = VENV / "bin" / "in-toto-sign"
IN_TOTO_VERIFY = VENV / "bin" / "in-toto-verify"
SLSA_VERIFIER = DELIVERABLES / ".bin" / "slsa-verifier"
ADAPTER = HERE / "delegation_adapter.py"
STEP_NAME = "execute"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def link_body(case_id: str, case_dir: Path) -> dict[str, Any]:
    """The evidence, translated into an in-toto link."""
    observation = json.loads((case_dir / "observation.json").read_text())
    payload = observation["record"]["payload"]
    materials: dict[str, Any] = {}
    source_path = case_dir / "program_source.py"
    if source_path.is_file():
        materials["program_source.py"] = {"sha256": sha256_file(source_path)}
    instance_path = case_dir / "public_instance.json"
    if instance_path.is_file():
        materials["public_instance.json"] = {"sha256": sha256_file(instance_path)}
    products: dict[str, Any] = {}
    candidate_path = case_dir / "candidate_output.json"
    if candidate_path.is_file():
        products["candidate_output.json"] = {"sha256": sha256_file(candidate_path)}
    byproducts: dict[str, Any] = {
        "execution_status": payload.get("execution_status"),
        "observation_sha256": sha256_file(case_dir / "observation.json"),
    }
    reference_path = case_dir / "reference.json"
    if reference_path.is_file():
        byproducts["reference_sha256"] = sha256_file(reference_path)
    byproducts["context"] = observation["context"]
    return {
        "_type": "link",
        "name": STEP_NAME,
        "command": payload.get("command") or [],
        "environment": {},
        "materials": materials,
        "products": products,
        "byproducts": byproducts,
    }


def layout_body(keyid: str, key_dict: dict[str, Any], command: list[str],
                inspection: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """The claim, translated into an in-toto layout.

    The step authorises the key that signed the link and declares the command
    that was executed.  It carries **no** material or product rules: the ACTS
    contract's nine checks have no native in-toto counterpart, which is exactly
    what the native arm measures.
    """
    return {
        "_type": "layout",
        "steps": [{
            "_type": "step",
            "name": STEP_NAME,
            "pubkeys": [keyid],
            "expected_command": command,
            "expected_materials": [],
            "expected_products": [],
            "threshold": 1,
        }],
        "inspect": inspection or [],
        "keys": {keyid: key_dict},
        "expires": "2035-01-01T00:00:00Z",
        "readme": "matched translation of the ACTS attribution claim",
    }


def slsa_statement(case_id: str, case_dir: Path) -> dict[str, Any]:
    """The evidence, translated into a SLSA v1.0 provenance statement."""
    observation = json.loads((case_dir / "observation.json").read_text())
    payload = observation["record"]["payload"]
    candidate_path = case_dir / "candidate_output.json"
    subject_digest = (sha256_file(candidate_path) if candidate_path.is_file()
                      else sha256_bytes(b""))
    return {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "candidate_output.json", "digest": {"sha256": subject_digest}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://acts-attack.invalid/e2a-attribution/v1",
                "externalParameters": {
                    "target_id": observation["context"]["target_id"],
                    "attempt_id": observation["context"]["attempt_id"],
                    "epoch": observation["context"]["epoch"],
                    "case_id": case_id,
                },
                "internalParameters": {
                    "execution_status": payload.get("execution_status"),
                    "observation_sha256": sha256_file(case_dir / "observation.json"),
                },
            },
            "runDetails": {
                "builder": {"id": "https://acts-attack.invalid/e2a-aggregator/v1"},
                "metadata": {"invocationId": observation["context"]["attempt_id"]},
            },
        },
    }


def sign(path: Path, private_key: Path) -> subprocess.CompletedProcess:
    """Sign metadata with in-toto-sign.

    in-toto-sign writes link metadata into the *current working directory*, so
    the signing runs with the case directory as its working directory.
    """
    return subprocess.run([str(IN_TOTO_SIGN), "-f", str(path), "-k", str(private_key)],
                          capture_output=True, text=True, cwd=str(path.parent))


def verify(layout_path: Path, public_key: Path, link_dir: Path) -> dict[str, Any]:
    result = subprocess.run(
        [str(IN_TOTO_VERIFY), "--layout", str(layout_path),
         "--verification-keys", str(public_key), "--link-dir", str(link_dir)],
        capture_output=True, text=True, cwd=str(layout_path.parent))
    return {"returncode": result.returncode,
            "stdout": result.stdout[-1500:], "stderr": result.stderr[-1500:]}


def run_slsa(statement_path: Path, candidate_path: Path) -> dict[str, Any]:
    environment = dict(os.environ)
    environment.update({"HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
                        "ALL_PROXY": "http://127.0.0.1:9", "NO_PROXY": ""})
    try:
        result = subprocess.run(
            [str(SLSA_VERIFIER), "verify-artifact", "--provenance-path", str(statement_path),
             "--source-uri", "github.com/dragonked2/ACTS-Attack", str(candidate_path)],
            capture_output=True, text=True, timeout=60, env=environment)
    except subprocess.TimeoutExpired:
        return {"returncode": 124, "stdout": "", "stderr": "timeout"}
    return {"returncode": result.returncode,
            "stdout": result.stdout[-1500:], "stderr": result.stderr[-1500:]}


def main() -> int:
    parser = argparse.ArgumentParser(description="matched translation into native models")
    parser.add_argument("--limit", type=int, default=0, help="translate only the first N cases")
    parser.add_argument("--work", type=Path, default=WORK_ROOT)
    args = parser.parse_args()
    if RESULTS_PATH.exists():
        raise SystemExit(f"refusing to overwrite {RESULTS_PATH}")

    key = Ed25519PrivateKey.generate()
    args.work.mkdir(parents=True, exist_ok=True)
    private_key = args.work / "intoto_key.pem"
    private_key.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                              serialization.PrivateFormat.PKCS8,
                                              serialization.NoEncryption()))
    public_key = args.work / "intoto_key.pub.pem"
    public_key.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))

    case_dirs = sorted((CORPUS_RUN / "cases").iterdir())
    if args.limit:
        case_dirs = case_dirs[:args.limit]

    # The reference decision uses a *ledger-bearing* aggregator, processed in
    # the same order as the corpus run, so that the cross-case replay check is
    # active exactly as it was when the corpus was produced.
    acts_contracts = {
        semantic: ContractV2(CORPUS_TRUST / "issuers_public.json",
                             CORPUS_TRUST / "trust_policy.json",
                             args.work / f"acts_ledger_{semantic}.jsonl", semantic)
        for semantic in (SEMANTIC_OUTPUT, SEMANTIC_COMPLETION)
    }

    rows = []
    for case_dir in case_dirs:
        case_id = case_dir.name
        certificate = json.loads((case_dir / "certificate.e2a.json").read_text())
        bundle = {"case_id": certificate["case_id"], "certificate": certificate}
        acts = {}
        for semantic, contract in acts_contracts.items():
            decision = contract.evaluate(bundle)
            acts[semantic] = {"decision": decision["decision"], "reason": decision["reason"]}

        work = args.work / case_id
        link_dir = work / "links"
        link_dir.mkdir(parents=True, exist_ok=True)
        link_file = work / f"{STEP_NAME}.link"
        link_file.write_text(json.dumps(
            {"signatures": [], "signed": link_body(case_id, case_dir)}, indent=2) + "\n")
        sign(link_file, private_key)
        for produced in work.glob(f"{STEP_NAME}.*.link"):
            produced.rename(link_dir / produced.name)
        signed_links = list(link_dir.glob("*.link"))
        if not signed_links:
            raise RuntimeError(f"in-toto-sign produced no signed link for {case_id}")
        keyid = signed_links[0].stem.split(".")[-1]
        command = link_body(case_id, case_dir)["command"]
        key_dict = load_public_key_from_file(str(public_key))

        native_layout = work / "layout_native.json"
        native_layout.write_text(json.dumps(
            {"signatures": [], "signed": layout_body(keyid, key_dict, command)}, indent=2) + "\n")
        sign(native_layout, private_key)
        native = verify(native_layout, public_key, link_dir)

        inspection = [{
            "_type": "inspection",
            "name": "adjudicate",
            "run": [sys.executable, str(ADAPTER), str(case_dir / "certificate.e2a.json"),
                    str(CORPUS_TRUST / "issuers_public.json"),
                    str(CORPUS_TRUST / "trust_policy.json")],
        }]
        delegated_layout = work / "layout_delegated.json"
        delegated_layout.write_text(json.dumps(
            {"signatures": [], "signed": layout_body(keyid, key_dict, command, inspection)},
            indent=2) + "\n")
        sign(delegated_layout, private_key)
        delegated = verify(delegated_layout, public_key, link_dir)

        statement_path = work / "provenance.json"
        statement_path.write_text(json.dumps(
            {"signatures": [], "signed": slsa_statement(case_id, case_dir)}, indent=2) + "\n")
        slsa = run_slsa(statement_path, case_dir / "candidate_output.json")

        rows.append({
            "case_id": case_id,
            "gt_success": certificate.get("gt_success"),
            "acts": acts,
            "in_toto_native": {"accepted": native["returncode"] == 0,
                               "returncode": native["returncode"],
                               "stderr": native["stderr"][-400:]},
            "in_toto_delegated": {"accepted": delegated["returncode"] == 0,
                                  "returncode": delegated["returncode"],
                                  "stderr": delegated["stderr"][-400:]},
            "slsa": {"accepted": slsa["returncode"] == 0,
                     "returncode": slsa["returncode"],
                     "stderr": slsa["stderr"][-400:]},
        })

    results = {
        "schema": "acts-stage6-matched-translation/1",
        "corpus_run": str(CORPUS_RUN),
        "cases": len(rows),
        "adapter_loc": len(ADAPTER.read_text().splitlines()),
        "acts_aggregator_loc": len((STAGE1_ROOT / "e2a" / "aggregator.py").read_text().splitlines()),
        "rows": rows,
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "cases": len(rows),
        "in_toto_native_accepted": sum(r["in_toto_native"]["accepted"] for r in rows),
        "in_toto_delegated_accepted": sum(r["in_toto_delegated"]["accepted"] for r in rows),
        "slsa_accepted": sum(r["slsa"]["accepted"] for r in rows),
        "acts_output_accepted": sum(
            r["acts"][SEMANTIC_OUTPUT]["decision"] == "ATTRIBUTED_SUCCESS" for r in rows),
        "adapter_loc": results["adapter_loc"],
        "acts_aggregator_loc": results["acts_aggregator_loc"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())