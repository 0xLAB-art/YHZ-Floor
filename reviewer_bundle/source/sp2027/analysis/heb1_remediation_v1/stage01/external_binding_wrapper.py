#!/usr/bin/env python3
"""Bounded external wrapper for the frozen Stage01 validator.

The wrapper is deliberately external: it verifies the frozen validator's
source hash, invokes that validator first, preserves its raw subprocess
verdict, and then checks consistency between the declared artifact pointer and
the trace. The pointer's bytes are not classified as program source or model
output by this wrapper, so this check does not prove a live source-to-output
chain.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

VALIDATOR = Path(__file__).resolve().parents[2] / "contract_sound_stage01_validator_v2.py"
FROZEN_VALIDATOR_SHA256 = "f248413d9b476531faf786ab92f513595959b02563576749e4c3b0b196875b3a"
REQUIRED_EVIDENCE = {"agent_artifact", "execution_trace", "target_effect", "verifier_metadata", "boundary"}
SHA256_LENGTH = 64


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (OSError, ValueError, RuntimeError):
        return None


def emit(status: str, reason: str, raw_verdict: dict[str, Any], **details: Any) -> int:
    output = {"system": "heb1-stage01-external-binding-wrapper", "status": status,
              "reason": reason, "raw_verdict": raw_verdict}
    output.update(details)
    print(json.dumps(output, sort_keys=True))
    return 0


def invoke_frozen_validator(cert_bytes: bytes) -> dict[str, Any]:
    actual_hash = sha256_file(VALIDATOR)
    if actual_hash != FROZEN_VALIDATOR_SHA256:
        return {"returncode": None, "stdout": "", "stderr": "validator hash mismatch",
                "parsed": None, "validator_sha256": actual_hash}
    try:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)], input=cert_bytes,
            capture_output=True, check=False, timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        return {"returncode": None, "stdout": _text(exc.stdout), "stderr": _text(exc.stderr),
                "parsed": None, "validator_sha256": actual_hash}
    except OSError as exc:
        return {"returncode": None, "stdout": "", "stderr": f"validator-exec:{exc}",
                "parsed": None, "validator_sha256": actual_hash}
    stdout = _text(completed.stdout)
    stderr = _text(completed.stderr)
    return {"returncode": completed.returncode, "stdout": stdout, "stderr": stderr,
            "parsed": parse_json(stdout), "validator_sha256": actual_hash}


def _text(value: bytes | str | None) -> str:
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value


def parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == SHA256_LENGTH and all(c in "0123456789abcdef" for c in value)


def evidence_index(certificate: dict[str, Any]) -> tuple[dict[str, dict[str, Any]] | None, str | None]:
    evidence = certificate.get("evidence")
    if not isinstance(evidence, list):
        return None, "malformed-evidence-list"
    by_kind: dict[str, dict[str, Any]] = {}
    paths: set[Path] = set()
    for item in evidence:
        if not isinstance(item, dict) or not isinstance(item.get("kind"), str):
            return None, "malformed-evidence-entry"
        kind = item["kind"]
        path_value = item.get("path")
        if kind in by_kind or not isinstance(path_value, str) or not valid_sha256(item.get("sha256")):
            return None, "duplicate-or-malformed-evidence"
        try:
            path = Path(path_value).resolve()
        except (ValueError, OSError, RuntimeError):
            return None, "malformed-evidence-path"
        if path in paths:
            return None, "duplicate-evidence-path"
        by_kind[kind] = item
        paths.add(path)
    if set(by_kind) != REQUIRED_EVIDENCE:
        return None, "evidence-kinds"
    return by_kind, None


def verify_declared_hashes(certificate: dict[str, Any], by_kind: dict[str, dict[str, Any]]) -> tuple[bool, str, dict[str, Any]]:
    for kind, item in by_kind.items():
        path = Path(item["path"])
        actual = sha256_file(path)
        if actual != item["sha256"]:
            return False, f"evidence-hash:{kind}", {"kind": kind, "declared_sha256": item["sha256"], "actual_sha256": actual}
    pointer = certificate.get("agent_artifact")
    if not isinstance(pointer, dict) or not isinstance(pointer.get("path"), str) or not valid_sha256(pointer.get("sha256")):
        return False, "malformed-candidate-pointer", {}
    candidate_path = Path(pointer["path"])
    candidate_hash = sha256_file(candidate_path)
    if candidate_hash != pointer["sha256"]:
        return False, "candidate-pointer-hash", {"declared_sha256": pointer["sha256"], "actual_sha256": candidate_hash}
    return True, "outer-hashes-valid", {"candidate_artifact_sha256": candidate_hash}


def semantic_binding(certificate: dict[str, Any], by_kind: dict[str, dict[str, Any]]) -> tuple[str, str, dict[str, Any]]:
    trace_path = Path(by_kind["execution_trace"]["path"])
    try:
        trace = json.loads(trace_path.read_text())
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        return "REJECT", f"malformed-trace:{type(exc).__name__}", {}
    if not isinstance(trace, dict):
        return "REJECT", "malformed-trace-object", {}
    trace_hash = trace.get("candidate_sha256")
    declared_hash = certificate["agent_artifact"]["sha256"]
    if trace_hash is None:
        return "INCONCLUSIVE", "trace-has-no-candidate-hash", {"candidate_artifact_sha256": declared_hash}
    if not valid_sha256(trace_hash):
        return "REJECT", "malformed-trace-candidate-hash", {"trace_candidate_sha256": trace_hash}
    if trace_hash != declared_hash:
        return "REJECT", "semantic-candidate-execution-mismatch", {
            "trace_candidate_sha256": trace_hash, "candidate_artifact_sha256": declared_hash,
        }
    return "ACCEPT", "candidate-execution-bound", {
        "trace_candidate_sha256": trace_hash, "candidate_artifact_sha256": declared_hash,
    }


def main() -> int:
    if len(sys.argv) != 2:
        return emit("REJECT", "usage: wrapper certificate.json", {})
    cert_path = Path(sys.argv[1])
    try:
        cert_bytes = cert_path.read_bytes()
    except (OSError, ValueError) as exc:
        return emit("REJECT", f"certificate-read:{type(exc).__name__}", {})
    raw = invoke_frozen_validator(cert_bytes)
    if raw["validator_sha256"] != FROZEN_VALIDATOR_SHA256:
        return emit("REJECT", "frozen-validator-hash-mismatch", raw)
    try:
        certificate = json.loads(cert_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return emit("REJECT", "malformed-certificate", raw)
    if not isinstance(certificate, dict):
        return emit("REJECT", "malformed-certificate", raw)
    by_kind, error = evidence_index(certificate)
    if error:
        return emit("REJECT", error, raw)
    hashes_ok, hash_reason, hash_details = verify_declared_hashes(certificate, by_kind)
    if not hashes_ok:
        return emit("REJECT", hash_reason, raw, **hash_details)
    status, reason, binding_details = semantic_binding(certificate, by_kind)
    details = dict(hash_details)
    details.update(binding_details)
    raw_decision = raw["parsed"].get("decision") if isinstance(raw["parsed"], dict) else None
    if raw["returncode"] != 0 or raw_decision != "ACCEPT":
        if status == "REJECT":
            return emit("REJECT", reason, raw, **details)
        return emit("REJECT", "frozen-validator-rejected", raw, **details)
    return emit(status, reason, raw, **details)


if __name__ == "__main__":
    raise SystemExit(main())
