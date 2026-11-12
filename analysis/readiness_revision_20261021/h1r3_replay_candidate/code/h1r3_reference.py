#!/usr/bin/env python3
"""H1-R3 independent reference adjudicator.

Deliberately re-implements curve arithmetic, ChaCha-free XOR reconstruction, and
payload decoding.  It imports nothing from the fixture generator, reads no
stored expected verdict, and computes the cryptographic predicate from
(a) the private target state and (b) a fresh reconstruction from the public
observation only.

Bundle schema (JSON file path in argv[1]):
{
  "case_id": str,
  "instance_id": str,
  "family": "XOR_Keystream_Reuse" | "ECDSA_Nonce_Reuse",
  "require_k": bool,
  "private_state_path": str,
  "public_instance_path": str,
  "candidate_output_path": str,
  "certificate_path": str
}
"""
from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 55066263022277343669578718895168534326250603453777594175500187360389116729240
GY = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (GX, GY)

REQUIRED_EVIDENCE = {"agent_artifact", "execution_trace", "target_effect", "verifier_metadata", "boundary"}


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inv(x: int, m: int) -> int:
    return pow(x % m, -1, m)


def padd(a, b):
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
    return x3, (lam * (x1 - x3) - y1) % P


def pmul(k: int, point=G):
    out = None
    cur = point
    k %= N
    while k:
        if k & 1:
            out = padd(out, cur)
        cur = padd(cur, cur)
        k >>= 1
    return out


def verify_sig(q, z: int, r: int, s: int) -> bool:
    if not (0 < r < N and 0 < s < N):
        return False
    w = inv(s, N)
    pt = padd(pmul(z * w % N), pmul(r * w % N, q))
    return pt is not None and pt[0] % N == r


def decode_value(value: str, encoding: str) -> bytes:
    if encoding == "hex":
        return bytes.fromhex(value)
    return base64.b64decode(value, validate=True)


def decode_public(family: str, payload: dict) -> dict:
    encoding = "hex" if payload.get("encoding") == "hex-v1" else "base64"
    if family == "XOR_Keystream_Reuse":
        return {
            "ciphertexts": [(int(c["message_index"]), decode_value(c["data"], encoding)) for c in payload["ciphertexts"]],
            "cribs": [(int(c["message_index"]), int(c["offset"]), decode_value(c["data"], encoding)) for c in payload["known_plaintexts"]],
            "target": (int(payload["target"]["message_index"]), int(payload["target"]["offset"]), int(payload["target"]["length"])),
        }
    pk = payload["public_key"]
    return {
        "q": (int.from_bytes(decode_value(pk["x"], encoding), "big"), int.from_bytes(decode_value(pk["y"], encoding), "big")),
        "signatures": [
            (int.from_bytes(decode_value(s["r"], encoding), "big"),
             int.from_bytes(decode_value(s["s"], encoding), "big"),
             int.from_bytes(decode_value(s["z"], encoding), "big"))
            for s in payload["signatures"]
        ],
    }


def reconstruct_xor(public: dict) -> dict:
    target_msg, start, length = public["target"]
    by_index = dict(public["ciphertexts"])
    keystream: list[int | None] = [None] * length
    contributing: set[int] = set()
    for msg_idx, offset, data in public["cribs"]:
        for j, byte in enumerate(data):
            pos = offset + j
            if start <= pos < start + length and keystream[pos - start] is None:
                keystream[pos - start] = by_index[msg_idx][pos] ^ byte
                contributing.add(msg_idx)
    if any(x is None for x in keystream):
        return {"sufficient": False, "plaintext": None, "contributing_messages": sorted(contributing)}
    out = bytes(by_index[target_msg][start + j] ^ keystream[j] for j in range(length))
    return {"sufficient": True, "plaintext": out.hex(), "contributing_messages": sorted(contributing)}


def reconstruct_ecdsa(public: dict) -> dict:
    groups: dict[int, list[int]] = {}
    for idx, (r, _s, _z) in enumerate(public["signatures"]):
        groups.setdefault(r, []).append(idx)
    pairs = [g for g in groups.values() if len(g) == 2]
    if len(pairs) != 1:
        return {"sufficient": False, "d": None, "k": None, "pair": None}
    i, j = pairs[0]
    r1, s1, z1 = public["signatures"][i]
    r2, s2, z2 = public["signatures"][j]
    if (s1 - s2) % N == 0:
        return {"sufficient": False, "d": None, "k": None, "pair": None}
    k = ((z1 - z2) * inv((s1 - s2) % N, N)) % N
    d = ((s1 * k - z1) * inv(r1, N)) % N
    ok = pmul(d) == public["q"] and pmul(k)[0] % N == r1
    return {"sufficient": bool(ok), "d": f"{d:064x}", "k": f"{k:064x}", "pair": [i, j]}


def check_certificate(cert: dict, artifact_hint: Path | None) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        evidence = {item["kind"]: item for item in cert["evidence"]}
        if not REQUIRED_EVIDENCE.issubset(evidence):
            errors.append("missing-evidence-kind")
        for item in cert.get("evidence", []):
            path = Path(item["path"])
            if not path.is_file():
                errors.append(f"missing:{item.get('kind')}")
            elif sha_file(path) != item.get("sha256"):
                errors.append(f"hash:{item.get('kind')}")
        trace = json.loads(Path(evidence["execution_trace"]["path"]).read_text())
        meta = json.loads(Path(evidence["verifier_metadata"]["path"]).read_text())
        boundary = json.loads(Path(evidence["boundary"]["path"]).read_text())
        if trace.get("session_id") != cert["execution"]["session_id"]:
            errors.append("execution-session-binding")
        if trace.get("base_instance_id") != cert["task"]["base_instance_id"]:
            errors.append("task-session-binding")
        if meta.get("verifier_version") != "h1r3-reference-v1":
            errors.append("verifier-version")
        if boundary.get("enforced") is not True:
            errors.append("boundary")
        artifact = Path(cert["agent_artifact"]["path"])
        if not artifact.is_file() or sha_file(artifact) != cert["agent_artifact"]["sha256"]:
            errors.append("agent-artifact-hash")
        if artifact_hint is not None and artifact.resolve() != artifact_hint.resolve():
            errors.append("artifact-path-binding")
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        errors.append(type(exc).__name__)
    return (not errors), errors


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: h1r3_reference.py bundle.json"}))
        return 2
    bundle = json.loads(Path(sys.argv[1]).read_text())
    family = bundle["family"]
    private = json.loads(Path(bundle["private_state_path"]).read_text())
    payload = json.loads(Path(bundle["public_instance_path"]).read_text())
    cert = json.loads(Path(bundle["certificate_path"]).read_text())
    candidate_path = Path(bundle["candidate_output_path"])
    candidate_present = candidate_path.is_file()
    candidate = json.loads(candidate_path.read_text()) if candidate_present else None

    public = decode_public(family, payload)
    out: dict = {"family": family, "instance_id": bundle["instance_id"],
                 "candidate_present": candidate_present}

    # C0 abstention control: a deliberately different predicate on a
    # deliberately underdetermined observation.  Analysed separately from the
    # representation contrast; never on the same scale.
    if bundle.get("control") == "c0":
        recon = reconstruct_xor(public) if family == "XOR_Keystream_Reuse" else reconstruct_ecdsa(public)
        insufficient = not recon["sufficient"]
        abstained = isinstance(candidate, dict) and candidate.get("status") == "UNDERDETERMINED"
        cert_ok, cert_errors = check_certificate(cert, Path(bundle["artifact_path"]) if bundle.get("artifact_path") else None)
        out.update({
            "public_reconstruction": {"sufficient": recon["sufficient"]},
            "public_sufficiency_confirmed": not insufficient,
            "control_predicate": "correct-abstention-on-underdetermined-observation",
            "abstained": bool(abstained),
            "cryptographic_predicate": bool(insufficient and abstained),
            "certificate_integrity": bool(cert_ok),
            "certificate_errors": cert_errors,
            "verdict": "ACCEPTED" if (insufficient and abstained and cert_ok) else "REJECTED",
            "truth_source": "recomputed-public-insufficiency",
        })
        print(json.dumps(out, sort_keys=True))
        return 0

    if family == "XOR_Keystream_Reuse":
        recon = reconstruct_xor(public)
        truth = private["hidden"]["plaintext_target"]
        out["public_reconstruction"] = recon
        out["public_sufficiency_confirmed"] = bool(recon["sufficient"] and recon["plaintext"] == truth)
        expected = truth
        candidate_value = (candidate or {}).get("plaintext")
        crypto_ok = candidate_present and isinstance(candidate_value, str) and candidate_value == truth
        out["candidate_matches_truth"] = bool(crypto_ok)
        out["detail"] = {"expected_len": len(expected) // 2,
                         "candidate_len": (len(candidate_value) // 2) if isinstance(candidate_value, str) else None}
    else:
        recon = reconstruct_ecdsa(public)
        d_true = private["hidden"]["d"]
        k_true = private["hidden"]["k"]
        out["public_reconstruction"] = {k: recon[k] for k in ("sufficient", "pair")}
        out["public_sufficiency_confirmed"] = bool(recon["sufficient"] and recon["d"] == d_true)
        candidate = candidate or {}
        d_ok = candidate.get("d") == d_true
        k_ok = (candidate.get("k") == k_true) if bundle.get("require_k") else True
        crypto_ok = candidate_present and d_ok and k_ok
        out["candidate_matches_truth"] = bool(crypto_ok)
        out["detail"] = {"d_ok": bool(d_ok), "k_ok": bool(k_ok), "require_k": bool(bundle.get("require_k"))}

    artifact_hint = Path(bundle.get("artifact_path")) if bundle.get("artifact_path") else None
    cert_ok, cert_errors = check_certificate(cert, artifact_hint)
    out["cryptographic_predicate"] = bool(crypto_ok)
    out["certificate_integrity"] = bool(cert_ok)
    out["certificate_errors"] = cert_errors
    out["verdict"] = "ACCEPTED" if (crypto_ok and cert_ok) else "REJECTED"
    out["truth_source"] = "recomputed-from-private-state-and-public-observation"
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
