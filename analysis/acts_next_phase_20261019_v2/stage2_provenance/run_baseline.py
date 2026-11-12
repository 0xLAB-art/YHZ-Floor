#!/usr/bin/env python3
"""Offline Stage 2 comparison against installed provenance verifiers.

This does not translate ACTS decisions into supply-chain claims. It measures:
1. Whether Cosign independently verifies each exact signed HEB-1 blob.
2. Whether one-byte-equivalent JSON tampering is rejected.
3. Whether native in-toto and SLSA CLIs ingest the HEB-1 envelope directly.

All operations are offline and read-only with respect to Stage 1 artifacts.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
STAGE1 = ROOT / "stage1_e2a"
RUN = STAGE1 / "runs" / "20261020T065943Z_confirmatory"
BUNDLE = STAGE1 / "frozen" / "issuers_public.json"
DELIVERABLES = ROOT / "research" / "deliverables"
COSIGN = DELIVERABLES / ".bin" / "cosign"
SLSA = DELIVERABLES / ".bin" / "slsa-verifier"
IN_TOTO_VERIFY = DELIVERABLES / ".venv" / "bin" / "in-toto-verify"
OUT = Path(__file__).with_name("baseline_results.json")
SEP = (",", ":")


def canonical_record(record: dict) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=SEP) + "\n").encode()


def canonical_context(context: dict) -> bytes:
    return json.dumps(context, sort_keys=True, separators=SEP, ensure_ascii=False).encode()


def run(command: list[str], cwd: Path | None = None, timeout: int = 30) -> dict:
    environment = dict(os.environ)
    environment.update({
        "HTTP_PROXY": "http://127.0.0.1:9",
        "HTTPS_PROXY": "http://127.0.0.1:9",
        "ALL_PROXY": "http://127.0.0.1:9",
        "NO_PROXY": "",
    })
    try:
        p = subprocess.run(
            command, cwd=cwd, text=True, capture_output=True, timeout=timeout,
            env=environment,
        )
        return {
            "returncode": p.returncode,
            "stdout": p.stdout[:2000],
            "stderr": p.stderr[:2000],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": 124,
            "stdout": (exc.stdout or "")[:2000] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[:2000] if isinstance(exc.stderr, str) else "",
            "timed_out": True,
        }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    issuers = json.loads(BUNDLE.read_text())["issuers"]
    by_id = {item["key_id"]: item for item in issuers}
    by_role = {item["role"]: item for item in issuers}
    raw_results = [json.loads(line) for line in (RUN / "raw_results.jsonl").read_text().splitlines()]

    output: dict = {
        "schema": "acts-stage2-provenance-baseline/1",
        "mode": "offline-read-only",
        "run": str(RUN.relative_to(ROOT)),
        "run_raw_results_sha256": sha256(RUN / "raw_results.jsonl"),
        "tools": {},
        "cases": [],
    }
    output["tools"]["cosign"] = run([str(COSIGN), "version"])
    output["tools"]["slsa_verifier"] = run([str(SLSA), "version"])
    output["tools"]["in_toto"] = run([str(IN_TOTO_VERIFY), "--version"])

    with tempfile.TemporaryDirectory(prefix="acts-stage2-") as temp_name:
        temp = Path(temp_name)
        pem_by_role: dict[str, Path] = {}
        for role, issuer in by_role.items():
            pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(issuer["public_key_hex"]))
            pem_path = temp / f"{role}.pub.pem"
            pem_path.write_bytes(pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
            pem_by_role[role] = pem_path

        for result in raw_results:
            case_id = result["case_id"]
            case_dir = RUN / "cases" / case_id
            claim = json.loads((case_dir / "claim.e2a.json").read_text())
            cert = json.loads((case_dir / "certificate.e2a.json").read_text())
            envelopes = {"claim": claim}
            for evidence_name in ("observation", "reference"):
                if evidence_name in cert.get("evidence", {}):
                    envelopes[evidence_name] = cert["evidence"][evidence_name]
            checks = []
            for name, envelope in envelopes.items():
                record = envelope["record"]
                unsigned = {k: record[k] for k in (
                    "format", "domain", "kind", "context", "issuer_role", "key_id", "payload"
                )}
                issuer = by_id[record["key_id"]]
                record_blob = temp / f"{case_id}-{name}-record.json"
                record_blob.write_bytes(canonical_record(unsigned))
                signature = base64.b64encode(bytes.fromhex(record["signature_hex"])).decode()
                authentic = run([
                    str(COSIGN), "verify-blob", "--offline", "--insecure-ignore-tlog",
                    "--key", str(pem_by_role[issuer["role"]]), "--signature", signature,
                    str(record_blob),
                ])
                tampered = dict(unsigned)
                tampered["domain"] = str(tampered["domain"]) + "-tampered"
                record_blob.write_bytes(canonical_record(tampered))
                altered = run([
                    str(COSIGN), "verify-blob", "--offline", "--insecure-ignore-tlog",
                    "--key", str(pem_by_role[issuer["role"]]), "--signature", signature,
                    str(record_blob),
                ])
                checks.append({
                    "layer": "record", "name": name, "role": issuer["role"],
                    "authentic_rc": authentic["returncode"], "tampered_rc": altered["returncode"],
                })

                context_role = envelope["context"]["role"]
                context_blob = temp / f"{case_id}-{name}-context.json"
                context_blob.write_bytes(canonical_context(envelope["context"]))
                context_signature = base64.b64encode(bytes.fromhex(envelope["context_signature_hex"])).decode()
                context_authentic = run([
                    str(COSIGN), "verify-blob", "--offline", "--insecure-ignore-tlog",
                    "--key", str(pem_by_role[context_role]), "--signature", context_signature,
                    str(context_blob),
                ])
                changed_context = dict(envelope["context"])
                changed_context["attempt_id"] = str(changed_context["attempt_id"]) + "-tampered"
                context_blob.write_bytes(canonical_context(changed_context))
                context_altered = run([
                    str(COSIGN), "verify-blob", "--offline", "--insecure-ignore-tlog",
                    "--key", str(pem_by_role[context_role]), "--signature", context_signature,
                    str(context_blob),
                ])
                checks.append({
                    "layer": "context", "name": name, "role": context_role,
                    "authentic_rc": context_authentic["returncode"],
                    "tampered_rc": context_altered["returncode"],
                })

            native_in_toto = run([
                str(IN_TOTO_VERIFY), "--layout", str(case_dir / "claim.e2a.json"),
                "--verification-keys", str(pem_by_role["aggregator"]),
                "--link-dir", str(case_dir),
            ])
            candidate = case_dir / "candidate_output.json"
            native_slsa = run([
                str(SLSA), "verify-artifact", "--provenance-path", str(case_dir / "claim.e2a.json"),
                "--source-uri", "github.com/dragonked2/ACTS-Attack", str(candidate),
            ], timeout=5)
            output["cases"].append({
                "case_id": case_id,
                "case_class": result["case_class"],
                "acts_decision": result["e2a"]["decision"],
                "cosign_checks": checks,
                "in_toto_native": native_in_toto,
                "slsa_native": native_slsa,
            })

    all_checks = [check for case in output["cases"] for check in case["cosign_checks"]]
    output["summary"] = {
        "cases": len(output["cases"]),
        "acts_decisions": dict(Counter(case["acts_decision"] for case in output["cases"])),
        "cosign_authentic_checks": len(all_checks),
        "cosign_authentic_pass": sum(check["authentic_rc"] == 0 for check in all_checks),
        "cosign_tamper_controls": len(all_checks),
        "cosign_tamper_rejected": sum(check["tampered_rc"] != 0 for check in all_checks),
        "in_toto_native_accept": sum(case["in_toto_native"]["returncode"] == 0 for case in output["cases"]),
        "in_toto_native_reject": sum(case["in_toto_native"]["returncode"] != 0 for case in output["cases"]),
        "slsa_native_accept": sum(case["slsa_native"]["returncode"] == 0 for case in output["cases"]),
        "slsa_native_reject": sum(case["slsa_native"]["returncode"] != 0 for case in output["cases"]),
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()