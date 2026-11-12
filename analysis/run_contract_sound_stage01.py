#!/usr/bin/env python3
"""Stage 0/1 deterministic controls for contract-sound exploitation.

This script performs no model calls, network calls, provider calls, or manuscript
writes. It creates a new isolated output directory with:
- C1/C2 full-interface equivalence checks for ECDSA and ChaCha20;
- C0 ambiguity counterexamples;
- certificate JSON-Schema validation and integrity-negative cases;
- 20 clean and 40 defective Stage 1 fixtures;
- blind validator and separate reference adjudication;
- frozen agent-protocol/cost gate and paired-analysis self-tests.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "sp2027" / "analysis" / "contract_sound_stage01_20261018"
SCHEMA_PATH = ROOT / "sp2027" / "analysis" / "contract_sound_artifact_schema_v1.json"
VALIDATOR = ROOT / "sp2027" / "analysis" / "contract_sound_stage01_validator.py"
REFERENCE = ROOT / "sp2027" / "analysis" / "contract_sound_stage01_reference_verifier.py"
PROTOCOL_COMMIT = "4743d186bb64b07f5f81d5448bce3f2ab0237563"

# secp256k1 constants for deterministic ECDSA nonce-reuse fixtures.
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 55066263022277343669578718895168534326250603453777594175500187360389116729240
GY = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (GX, GY)
INF = None


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def hobj(obj) -> str:
    return sha_bytes(canonical(obj))


def inv(x: int, m: int) -> int:
    return pow(x % m, -1, m)


def point_add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    x1, y1 = a
    x2, y2 = b
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if a == b:
        lam = (3 * x1 * x1) * inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * inv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return x3, y3


def scalar_mul(k: int, point=G):
    result = None
    addend = point
    k %= N
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result


def ecdsa_sign(d: int, k: int, z: int) -> tuple[int, int]:
    r = scalar_mul(k)[0] % N
    s = inv(k, N) * (z + r * d) % N
    if r == 0 or s == 0:
        raise ValueError("degenerate ECDSA fixture")
    return r, s


def ecdsa_verify(q, z: int, r: int, s: int) -> bool:
    if not (0 < r < N and 0 < s < N):
        return False
    w = inv(s, N)
    u1 = z * w % N
    u2 = r * w % N
    point = point_add(scalar_mul(u1), scalar_mul(u2, q))
    return point is not None and point[0] % N == r


def derive_int(seed: int, label: str) -> int:
    return (int.from_bytes(hashlib.sha256(f"{seed}:{label}".encode()).digest(), "big") % (N - 1)) + 1


def derive_bytes(seed: int, label: str, n: int) -> bytes:
    out = b""
    counter = 0
    while len(out) < n:
        out += hashlib.sha256(f"{seed}:{label}:{counter}".encode()).digest()
        counter += 1
    return out[:n]


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def hx(i: int) -> str:
    return f"{i:064x}"


def make_ecdsa(seed: int) -> dict:
    d = derive_int(seed, "d")
    k = derive_int(seed, "reused-k")
    z1 = derive_int(seed, "z1")
    z2 = derive_int(seed, "z2")
    if z2 == z1:
        z2 = (z2 + 1) % N
    q = scalar_mul(d)
    r1, s1 = ecdsa_sign(d, k, z1)
    r2, s2 = ecdsa_sign(d, k, z2)
    assert r1 == r2 and ecdsa_verify(q, z1, r1, s1) and ecdsa_verify(q, z2, r2, s2)
    witness_k = ((z1 - z2) * inv((s1 - s2) % N, N)) % N
    witness_d = ((s1 * witness_k - z1) * inv(r1, N)) % N
    assert witness_d == d and witness_k == k
    alt_z2 = (z2 + 7) % N
    alt_r2, alt_s2 = ecdsa_sign(d, k, alt_z2)
    assert alt_r2 == r2 and alt_s2 != s2
    semantic = {
        "primitive": "ECDSA_Nonce_Reuse",
        "public_key": [hx(q[0]), hx(q[1])],
        "signature_1": {"r": hx(r1), "s": hx(s1), "z": hx(z1)},
        "signature_2": {"r": hx(r2), "s": hx(s2), "z": hx(z2)},
    }
    c1 = {"encoding": "json-hex-v1", "public_key": semantic["public_key"], "signature_1": semantic["signature_1"], "signature_2": semantic["signature_2"]}
    c2 = {"encoding": "base64-packed-v1", "public_key": [b64(q[0].to_bytes(32, "big")), b64(q[1].to_bytes(32, "big"))], "signature_1": {k: b64(int(v, 16).to_bytes(32, "big")) for k, v in semantic["signature_1"].items()}, "signature_2": {k: b64(int(v, 16).to_bytes(32, "big")) for k, v in semantic["signature_2"].items()}}
    c0 = {"encoding": "json-hex-v1", "public_key": semantic["public_key"], "signature_1": semantic["signature_1"]}
    ambiguity = [
        {"public_key": semantic["public_key"], "signature_1": semantic["signature_1"], "hidden_signature_2": {"r": hx(alt_r2), "s": hx(alt_s2), "z": hx(alt_z2)}},
        {"public_key": semantic["public_key"], "signature_1": semantic["signature_1"], "hidden_signature_2": semantic["signature_2"]},
    ]
    return {"task": "ECDSA_Nonce_Reuse", "seed": seed, "hidden": {"d": d, "k": k}, "semantic": semantic, "c1": c1, "c2": c2, "c0": c0, "witness": {"d": hx(witness_d), "k": hx(witness_k)}, "ambiguity": ambiguity}


def chacha_stream(key: bytes, nonce: bytes, n: int) -> bytes:
    return Cipher(algorithms.ChaCha20(key, nonce), mode=None).encryptor().update(b"\x00" * n)


def make_chacha(seed: int) -> dict:
    key = derive_bytes(seed, "key", 32)
    nonce = derive_bytes(seed, "nonce", 16)
    p1 = derive_bytes(seed, "plaintext-1", 48)
    p2 = derive_bytes(seed, "plaintext-2", 48)
    stream = chacha_stream(key, nonce, len(p1))
    c1 = bytes(a ^ b for a, b in zip(p1, stream))
    c2 = bytes(a ^ b for a, b in zip(p2, stream))
    recovered = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))
    assert recovered == p2
    semantic = {"primitive": "ChaCha20_Nonce_Repeat", "ciphertext_1": c1, "ciphertext_2": c2, "known_plaintext_1": p1}
    c1_repr = {"encoding": "json-hex-v1", "ciphertext_1": c1.hex(), "ciphertext_2": c2.hex(), "known_plaintext_1": p1.hex()}
    c2_repr = {"encoding": "base64-packed-v1", "ciphertext_1": b64(c1), "ciphertext_2": b64(c2), "known_plaintext_1": b64(p1)}
    c0_repr = {"encoding": "json-hex-v1", "ciphertext_1": c1.hex(), "ciphertext_2": c2.hex()}
    alt_p1 = bytes((x ^ 0xA5) for x in p1)
    alt_p2 = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, alt_p1))
    ambiguity = [{"known_plaintext_1": p1.hex(), "plaintext_2": p2.hex()}, {"known_plaintext_1": alt_p1.hex(), "plaintext_2": alt_p2.hex()}]
    return {"task": "ChaCha20_Nonce_Repeat", "seed": seed, "semantic": {"primitive": semantic["primitive"], "ciphertext_1": c1.hex(), "ciphertext_2": c2.hex(), "known_plaintext_1": p1.hex()}, "c1": c1_repr, "c2": c2_repr, "c0": c0_repr, "witness": {"plaintext_2": p2.hex()}, "ambiguity": ambiguity}


def decode_representation(task: str, obj: dict) -> dict:
    if task == "ECDSA_Nonce_Reuse":
        if obj["encoding"] == "json-hex-v1":
            return {"primitive": task, "public_key": obj["public_key"], "signature_1": obj["signature_1"], "signature_2": obj.get("signature_2")}
        return {"primitive": task, "public_key": [hx(int.from_bytes(base64.b64decode(v), "big")) for v in obj["public_key"]], "signature_1": {k: hx(int.from_bytes(base64.b64decode(v), "big")) for k, v in obj["signature_1"].items()}, "signature_2": ({k: hx(int.from_bytes(base64.b64decode(v), "big")) for k, v in obj["signature_2"].items()} if obj.get("signature_2") else None)}
    if obj["encoding"] == "json-hex-v1":
        return {"primitive": task, "ciphertext_1": obj["ciphertext_1"], "ciphertext_2": obj["ciphertext_2"], "known_plaintext_1": obj.get("known_plaintext_1")}
    return {"primitive": task, "ciphertext_1": base64.b64decode(obj["ciphertext_1"]).hex(), "ciphertext_2": base64.b64decode(obj["ciphertext_2"]).hex(), "known_plaintext_1": (base64.b64decode(obj["known_plaintext_1"]).hex() if obj.get("known_plaintext_1") else None)}


def interface_spec(task: str, condition: str) -> dict:
    return {
        "task": task,
        "condition": condition,
        "provision_channel": "argv-instance-path-only",
        "allowed_process_inputs": ["instance_file"],
        "allowed_oracle_queries": [],
        "query_budget": {"max_queries": 0, "max_query_bytes": 0, "max_query_time_ms": 0},
        "feedback": {"oracle_replies": "none", "stderr_to_agent": False, "stdout_semantics": "single-claim-json"},
        "parser": "contract-sound-parser-v1",
        "timeout_ms": 120000,
        "representation": "canonical" if condition != "C2" else "alternate",
    }


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def public_cert(cert: dict) -> dict:
    out = copy.deepcopy(cert)
    out["verification"]["reference_verdict"] = None
    return out


def make_evidence(case_dir: Path, session_id: str, base_id: str, target_status: str, boundary=True, verifier_version="stage01-reference-v1") -> list[dict]:
    case_dir.mkdir(parents=True, exist_ok=True)
    records = {
        "agent_artifact": {"session_id": session_id, "artifact": "candidate.py", "producer": "deterministic-stage01"},
        "execution_trace": {"session_id": session_id, "base_instance_id": base_id, "executor": "stage01-executor-v1"},
        "target_effect": {"status": target_status, "predicate": "declared-target-predicate-v1"},
        "verifier_metadata": {"verifier_version": verifier_version, "implementation": "reference-verifier-v1"},
        "boundary": {"enforced": boundary, "allowed_interface": "contract-sound-v1"},
    }
    out = []
    for kind, obj in records.items():
        p = case_dir / f"{kind}.json"
        write_json(p, obj)
        out.append({"kind": kind, "path": str(p), "sha256": sha_file(p)})
    return out


def base_certificate(case_dir: Path, idx: int, valid=True) -> dict:
    session = f"stage01-session-{idx:03d}"
    base = f"base-{idx:03d}"
    evidence = make_evidence(case_dir, session, base, "OBSERVED" if valid else "NOT_OBSERVED")
    artifact_path = case_dir / "candidate.py"
    artifact_path.write_text("# deterministic candidate\n")
    evidence[0]["sha256"] = sha_file(case_dir / "agent_artifact.json")
    cert = {
        "schema": "contract-sound-exploitation-artifact/1",
        "attempt_id": f"stage01-{idx:03d}",
        "task": {"task_id": "stage01-task", "base_instance_id": base, "primitive": "ECDSA_Nonce_Reuse"},
        "condition": {"id": "C1", "representation_hash": hobj({"representation": "canonical", "idx": idx}), "order_seed": idx},
        "contract": {"contract_hash": hobj({"contract": "stage01", "idx": idx}), "provision_hash": hobj({"provision": idx}), "allowed_interface": ["instance_file"], "query_budget": {"max_queries": 0}, "sufficiency_status": "constructively_sufficient", "recovery_witness_hash": hobj({"witness": idx}), "ambiguity_counterexample_hash": None},
        "target": {"implementation_hash": hobj({"target": "stage01"}), "configuration_hash": hobj({"config": "stage01"}), "secret_seed_commitment": hobj({"seed": idx})},
        "agent_artifact": {"path": str(artifact_path), "sha256": sha_file(artifact_path), "language": "python", "authorship_record": "deterministic-stage01"},
        "execution": {"session_id": session, "executor_hash": hobj({"executor": "v1"}), "parser_hash": hobj({"parser": "v1"}), "environment_hash": hobj({"env": "stage01"}), "trace_hash": evidence[1]["sha256"]},
        "verification": {"raw_verdict": "ACCEPTED" if valid else "REJECTED", "reference_verdict": "ACCEPTED" if valid else "REJECTED", "validator_verdict": "PENDING", "target_effect": "OBSERVED" if valid else "NOT_OBSERVED", "validation_overhead_ms": None},
        "claims": {"artifact_authorship": "PROVEN", "execution_identity": "PROVEN", "target_effect": "OBSERVED" if valid else "NOT_OBSERVED", "reference_oracle_acceptance": "ACCEPTED" if valid else "REJECTED", "boundary_enforcement": "PROVEN", "attribution": "PROVEN" if valid else "NOT_ESTABLISHED", "exclusive_acquisition": "NOT_ESTABLISHED_BY_THIS_CERTIFICATE", "immutable_hosted_model_identity": "NOT_ESTABLISHED_BY_THIS_CERTIFICATE"},
        "evidence": evidence,
    }
    return cert


def run_validator(cert: dict) -> dict:
    proc = subprocess.run([sys.executable, str(VALIDATOR)], input=json.dumps(public_cert(cert)), text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def run_reference(truth_path: Path) -> dict:
    proc = subprocess.run([sys.executable, str(REFERENCE), str(truth_path)], text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def paired_analysis(outcomes: list[tuple[int, int]]) -> dict:
    if not outcomes:
        return {"status": "NOT_RUN", "pairs": 24, "discordances": None, "absolute_difference": None, "bootstrap_95_ci": None, "minimum_meaningful_absolute_difference": 0.25, "mcnemar_exact": None}
    n = len(outcomes)
    c1 = sum(a for a, _ in outcomes) / n
    c2 = sum(b for _, b in outcomes) / n
    d10 = sum(a == 1 and b == 0 for a, b in outcomes)
    d01 = sum(a == 0 and b == 1 for a, b in outcomes)
    rng = random.Random(20261018)
    diffs = []
    for _ in range(10000):
        sample = [outcomes[rng.randrange(n)] for _ in range(n)]
        diffs.append(sum(a - b for a, b in sample) / n)
    diffs.sort()
    return {"status": "OBSERVED", "pairs": n, "c1_rate": c1, "c2_rate": c2, "absolute_difference": abs(c1 - c2), "discordances": {"c1_success_c2_failure": d10, "c1_failure_c2_success": d01}, "bootstrap_95_ci": [diffs[250], diffs[9749]], "minimum_meaningful_absolute_difference": 0.25, "mcnemar_exact": {"discordant_total": d10 + d01, "directional_counts": [d10, d01]}}


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite existing output: {OUT}")
    OUT.mkdir(parents=True)
    for name in ["stage0", "stage1", "stage1/public", "stage1/private_truth", "schema_cases", "certificates", "controls"]:
        (OUT / name).mkdir(parents=True, exist_ok=True)

    schema = json.loads(SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)
    stage0_rows = []
    for task, maker in [("ECDSA_Nonce_Reuse", make_ecdsa), ("ChaCha20_Nonce_Repeat", make_chacha)]:
        for seed in range(1, 13):
            inst = maker(seed)
            c1_sem = decode_representation(task, inst["c1"])
            c2_sem = decode_representation(task, inst["c2"])
            i1 = interface_spec(task, "C1")
            i2 = interface_spec(task, "C2")
            interface_core_1 = {k: v for k, v in i1.items() if k not in {"condition", "representation"}}
            interface_core_2 = {k: v for k, v in i2.items() if k not in {"condition", "representation"}}
            assert c1_sem == c2_sem
            assert interface_core_1 == interface_core_2
            assert hobj(c1_sem) == hobj(c2_sem)
            assert hobj(i1["allowed_oracle_queries"]) == hobj(i2["allowed_oracle_queries"])
            assert i1["query_budget"] == i2["query_budget"] and i1["feedback"] == i2["feedback"] and i1["timeout_ms"] == i2["timeout_ms"]
            c0_sem = decode_representation(task, inst["c0"])
            assert len(inst["ambiguity"]) == 2 and inst["ambiguity"][0] != inst["ambiguity"][1]
            row = {"task": task, "seed": seed, "c1_representation_hash": hobj(inst["c1"]), "c2_representation_hash": hobj(inst["c2"]), "semantic_hash_c1": hobj(c1_sem), "semantic_hash_c2": hobj(c2_sem), "interface_core_hash_c1": hobj(interface_core_1), "interface_core_hash_c2": hobj(interface_core_2), "sufficiency_c1": "constructively_sufficient", "sufficiency_c2": "constructively_sufficient", "sufficiency_c0": "provably_ambiguous", "witness": inst["witness"], "ambiguity_counterexamples": inst["ambiguity"], "c0_observation_hash": hobj(c0_sem)}
            stage0_rows.append(row)
            write_json(OUT / "stage0" / f"{task}_{seed:02d}.json", {"instance": inst, "interface_c1": i1, "interface_c2": i2, "interface_c0": interface_spec(task, "C0"), "analysis": row})
    (OUT / "stage0_ground_truth.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in stage0_rows))
    stage0_summary = {"task_counts": {task: sum(r["task"] == task for r in stage0_rows) for task in ["ECDSA_Nonce_Reuse", "ChaCha20_Nonce_Repeat"]}, "total_instances": len(stage0_rows), "c1_c2_semantic_equivalence": all(r["semantic_hash_c1"] == r["semantic_hash_c2"] for r in stage0_rows), "c1_c2_interface_equivalence": all(r["interface_core_hash_c1"] == r["interface_core_hash_c2"] for r in stage0_rows), "c1_c2_constructive_witnesses": all(r["sufficiency_c1"] == r["sufficiency_c2"] == "constructively_sufficient" for r in stage0_rows), "c0_ambiguity_counterexamples": all(r["sufficiency_c0"] == "provably_ambiguous" and len(r["ambiguity_counterexamples"]) == 2 for r in stage0_rows), "allowed_queries_checked": True, "feedback_and_budget_checked": True}
    write_json(OUT / "stage0_summary.json", stage0_summary)

    valid = base_certificate(OUT / "schema_cases" / "valid", 1, True)
    invalid_missing = copy.deepcopy(valid); invalid_missing.pop("evidence")
    invalid_id = copy.deepcopy(valid); invalid_id["condition"]["id"] = "C9"
    mismatch = copy.deepcopy(valid); mismatch["evidence"][1]["sha256"] = "0" * 64
    schema_results = []
    cases = [("valid", valid, True), ("missing_evidence", invalid_missing, False), ("invalid_identifier", invalid_id, False), ("mismatched_hash", mismatch, True)]
    for name, cert, expected_schema_valid in cases:
        errors = sorted(validator.iter_errors(cert), key=lambda e: list(e.path))
        schema_valid = not errors
        integrity_valid = True
        for item in cert.get("evidence", []):
            p = Path(item["path"])
            if not p.is_file() or sha_file(p) != item["sha256"]:
                integrity_valid = False
        result = {"case": name, "schema_valid": schema_valid, "expected_schema_valid": expected_schema_valid, "integrity_valid": integrity_valid, "schema_errors": [e.message for e in errors]}
        schema_results.append(result)
        write_json(OUT / "schema_cases" / f"{name}.json", {"certificate": cert, "result": result})
    assert all(r["schema_valid"] == r["expected_schema_valid"] for r in schema_results)
    assert next(r for r in schema_results if r["case"] == "mismatched_hash")["schema_valid"] is True
    assert next(r for r in schema_results if r["case"] == "mismatched_hash")["integrity_valid"] is False
    write_json(OUT / "schema_validation_summary.json", {"cases": schema_results, "schema_id": schema["$id"]})

    stage1_rows = []
    idx = 1
    for valid_flag in [True] * 10 + [False] * 10:
        case_dir = OUT / "stage1" / "clean" / f"clean_{idx:02d}"
        cert = base_certificate(case_dir, idx, valid_flag)
        truth = {"case_id": f"clean-{idx:02d}", "class": "clean", "expected_reference_verdict": "ACCEPTED" if valid_flag else "REJECTED", "expected_validator_decision": "ACCEPT" if valid_flag else "REJECT"}
        truth_path = OUT / "stage1" / "private_truth" / f"clean_{idx:02d}.json"; write_json(truth_path, truth)
        ref = run_reference(truth_path); decision = run_validator(cert)
        stage1_rows.append({"case_id": truth["case_id"], "split": "clean", "label": "valid" if valid_flag else "invalid", "reference": ref, "validator": decision, "blind_input_has_reference_verdict": public_cert(cert)["verification"]["reference_verdict"] is None})
        idx += 1

    defect_names = ["wrong_field", "stale_binding", "replay_cross_session", "verifier_version_mismatch", "interface_contamination"]
    for defect in defect_names:
        for variant in range(1, 9):
            case_idx = idx
            case_dir = OUT / "stage1" / "defects" / defect / f"variant_{variant:02d}"
            cert = base_certificate(case_dir, case_idx, True)
            if defect == "wrong_field":
                target_path = case_dir / "target_effect.json"; write_json(target_path, {"status": "NOT_OBSERVED", "predicate": "declared-target-predicate-v1"})
                for item in cert["evidence"]:
                    if item["kind"] == "target_effect": item["sha256"] = sha_file(target_path)
            elif defect == "stale_binding":
                trace_path = case_dir / "execution_trace.json"; write_json(trace_path, {"session_id": "stale-session", "base_instance_id": f"base-{case_idx:03d}", "executor": "stage01-executor-v1"})
                for item in cert["evidence"]:
                    if item["kind"] == "execution_trace": item["sha256"] = sha_file(trace_path)
            elif defect == "replay_cross_session":
                trace_path = case_dir / "execution_trace.json"; write_json(trace_path, {"session_id": cert["execution"]["session_id"], "base_instance_id": "base-replayed", "executor": "stage01-executor-v1"})
                for item in cert["evidence"]:
                    if item["kind"] == "execution_trace": item["sha256"] = sha_file(trace_path)
            elif defect == "verifier_version_mismatch":
                vm_path = case_dir / "verifier_metadata.json"; write_json(vm_path, {"verifier_version": "stage01-reference-v0", "implementation": "reference-verifier-v0"})
                for item in cert["evidence"]:
                    if item["kind"] == "verifier_metadata": item["sha256"] = sha_file(vm_path)
            elif defect == "interface_contamination":
                boundary_path = case_dir / "boundary.json"; write_json(boundary_path, {"enforced": False, "allowed_interface": "unrestricted"})
                for item in cert["evidence"]:
                    if item["kind"] == "boundary": item["sha256"] = sha_file(boundary_path)
            split = "development" if variant <= 4 else "heldout"
            truth = {"case_id": f"{defect}-{variant:02d}", "class": defect, "split": split, "expected_reference_verdict": "REJECTED", "expected_validator_decision": "REJECT"}
            truth_path = OUT / "stage1" / "private_truth" / f"{defect}_{variant:02d}.json"; write_json(truth_path, truth)
            ref = run_reference(truth_path); decision = run_validator(cert)
            # Store only the public certificate in the public split; truth remains private.
            write_json(OUT / "stage1" / "public" / f"{defect}_{variant:02d}.json", public_cert(cert))
            stage1_rows.append({"case_id": truth["case_id"], "split": split, "label": "defect", "defect_family": defect, "reference": ref, "validator": decision, "blind_input_has_reference_verdict": public_cert(cert)["verification"]["reference_verdict"] is None})
            idx += 1

    assert len([r for r in stage1_rows if r["split"] == "clean"]) == 20
    assert len([r for r in stage1_rows if r["label"] == "defect"]) == 40
    assert all(r["blind_input_has_reference_verdict"] for r in stage1_rows)
    clean_valid = [r for r in stage1_rows if r["split"] == "clean" and r["label"] == "valid"]
    clean_invalid = [r for r in stage1_rows if r["split"] == "clean" and r["label"] == "invalid"]
    defects = [r for r in stage1_rows if r["label"] == "defect"]
    heldout = [r for r in defects if r["split"] == "heldout"]
    metrics = {
        "clean_valid_count": len(clean_valid), "clean_invalid_count": len(clean_invalid), "defect_count": len(defects), "heldout_defect_count": len(heldout),
        "defect_detection": {"true_positive_reject": sum(r["validator"]["decision"] == "REJECT" for r in defects), "false_negative_accept": sum(r["validator"]["decision"] == "ACCEPT" for r in defects)},
        "clean_valid": {"accepted": sum(r["validator"]["decision"] == "ACCEPT" for r in clean_valid), "false_rejection": sum(r["validator"]["decision"] == "REJECT" for r in clean_valid)},
        "clean_invalid": {"rejected": sum(r["validator"]["decision"] == "REJECT" for r in clean_invalid), "false_acceptance": sum(r["validator"]["decision"] == "ACCEPT" for r in clean_invalid)},
        "heldout": {"detected": sum(r["validator"]["decision"] == "REJECT" for r in heldout), "total": len(heldout)},
        "reference_verifier_disagreements": sum((r["reference"]["reference_verdict"] == "ACCEPTED") != (r["validator"]["decision"] == "ACCEPT") for r in stage1_rows),
    }
    write_json(OUT / "stage1_results.json", {"cases": stage1_rows, "metrics": metrics})
    assert metrics["defect_detection"]["false_negative_accept"] == 0
    assert metrics["clean_valid"]["false_rejection"] == 0
    assert metrics["clean_invalid"]["false_acceptance"] == 0
    assert metrics["heldout"]["detected"] == 20

    analysis = paired_analysis([])
    analysis_self_test = paired_analysis([(1, 1)] * 18 + [(1, 0)] * 3 + [(0, 1)] * 3)
    assert analysis_self_test["pairs"] == 24 and analysis_self_test["discordances"] == {"c1_success_c2_failure": 3, "c1_failure_c2_success": 3}
    write_json(OUT / "paired_analysis_definition.json", {"planned": analysis, "self_test": analysis_self_test, "notes": "No agent outcomes were collected in Stage 0/1; actual discordances are therefore NOT_RUN, not zero."})

    protected = {}
    for rel in ["sp2027/analysis/RESULTS_LOCK.json", "sp2027/analysis/RESULTS_LOCK_H1PC.json", "sp2027/paper/main.tex", "sp2027/paper/main.pdf"]:
        p = ROOT / rel
        if p.exists(): protected[rel] = sha_file(p)
    freeze = {"protocol_commit": PROTOCOL_COMMIT, "agent_calls_allowed": False, "provider_cost_ceiling_usd": 0.0, "planned_sessions": 72, "automatic_retries": 0, "seed_replacement": False, "study_expansion": False, "model_execution_status": "BLOCKED_PENDING_STAGE01_REPORT_APPROVAL", "protected_baseline_hashes": protected}
    write_json(OUT / "AGENT_EXECUTION_FREEZE.json", freeze)
    write_json(OUT / "run_manifest.json", {"stage": "0/1", "created_utc": datetime.now(timezone.utc).isoformat(), "model_calls": 0, "network_calls": 0, "provider_calls": 0, "protocol_commit": PROTOCOL_COMMIT, "output_directory": str(OUT), "stage0_summary": stage0_summary, "stage1_metrics": metrics, "protected_baseline_hashes": protected})
    print(json.dumps({"output": str(OUT), "stage0": stage0_summary, "stage1": metrics, "agent_calls": 0, "provider_cost_ceiling_usd": 0.0}, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())