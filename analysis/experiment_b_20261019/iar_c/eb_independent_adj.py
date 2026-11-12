#!/usr/bin/env python3
"""IAR-C independent truth adjudicator (Experiment B, IAR-C).

Separately written from ../eb_adjudicator.py (IAR-B) and from all three
evaluated systems. Inputs are read-only: <public_dir> (certificate, request,
candidate, target, evidence + .sig sidecars), <private_dir> (run_registry.json,
targets.json), <trust> (Ed25519 anchor). Only `eb_crypto` is imported, and only
for the shared target-domain predicate; no fixture, validator, or adjudicator
module is imported.

Truth contract (the interface definition every IAR adjudicator implements):

* malformed: any structural / parse / declared-hash failure in the public
  bundle, or an empty evidence list. Broken bundles short-circuit to an
  all-negative verdict and are not re-judged.
* authentic[kind]: the record digest verifies under the anchor key of the
  record's own session_id. Forged, foreign, or unknown-key signatures are NOT
  malformed; they only fail authenticity of the affected record.
* supported: length of the longest consecutive run of rungs r1..r6 built from
  authentic records that are corroborated by the private run registry
  (candidate hash, effect status, reference outcome, condition, instance) and
  bound to the credited session (certificate.execution.session_id). Private
  inputs are never given to the evaluated systems.
* crypto_ok: the task-specific cryptographic predicate recomputes True/False
  from the private target instance named by the certificate's target id.
* truth_strong: supported == 6 and crypto_ok and not malformed.

CLI: python3 eb_independent_adj.py <public_dir> <private_dir> <trust_path>
Prints one JSON line; always exits 0.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eb_crypto  # noqa: E402  (shared target-domain primitive module)

SYS_NAME = "ic-independent-adjudicator"

LEVEL_NAMES = [
    "artifact_authorship",
    "execution_identity",
    "target_effect",
    "reference_oracle_acceptance",
    "boundary_enforcement",
    "attribution",
]


def canon(obj) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_obj(obj) -> str:
    return digest(canon(obj))


def digest_file(path: Path) -> str:
    return digest(path.read_bytes())


def load_json(path: Path):
    return json.loads(path.read_text())


def pick(obj, *names):
    cur = obj
    for name in names:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(name)
    return cur


def all_equal(values) -> bool:
    vals = list(values)
    return bool(vals) and None not in vals and len(set(vals)) == 1


def decode_instance(serialized: dict) -> dict:
    inst = {}
    for key, val in serialized.items():
        if isinstance(val, dict) and "__hex__" in val:
            inst[key] = bytes.fromhex(val["__hex__"])
        else:
            inst[key] = val
    return inst


def verify_under_anchor(record: dict, sig_hex: str, keys: dict) -> bool:
    session = record.get("session_id")
    if session not in keys:
        return False
    try:
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(keys[session]))
        pub.verify(bytes.fromhex(sig_hex.strip()), bytes.fromhex(digest_obj(record)))
        return True
    except Exception:
        return False


def emit(malformed, supported, truth_strong, crypto_ok, cred):
    print(json.dumps({
        "system": SYS_NAME,
        "malformed": bool(malformed),
        "supported": int(supported) if supported is not None else 0,
        "truth_strong": bool(truth_strong),
        "crypto_ok": bool(crypto_ok),
        "cred": cred,
    }, sort_keys=True))
    return 0


def main() -> int:
    if len(sys.argv) != 4:
        return emit(True, 0, False, False, None)
    pub = Path(sys.argv[1])
    priv = Path(sys.argv[2])
    trust = Path(sys.argv[3])

    # -- Phase 1: parse bundle and private state ---------------------------
    try:
        cert = load_json(pub / "certificate.json")
        request = load_json(pub / "request.json")
        candidate = load_json(pub / "candidate.json")
        load_json(pub / "target.json")
        runs = load_json(priv / "run_registry.json")["runs"]
        target_map = load_json(priv / "targets.json")["targets"]
        anchor = load_json(trust)["keys"]
    except Exception:
        return emit(True, 0, False, False, None)

    cred = pick(cert, "execution", "session_id")

    # -- Phase 2: evidence walk (hash binding + anchor authenticity) -------
    records: dict[str, dict] = {}
    authentic: dict[str, bool] = {}
    try:
        declared = cert.get("evidence", [])
        if not declared:
            raise ValueError("empty evidence list")
        for item in declared:
            kind = item.get("kind")
            rel = item.get("path", "")
            local = pub / rel
            if not local.exists():
                raise ValueError("missing evidence file: %s" % kind)
            if digest_file(local) != item.get("sha256"):
                raise ValueError("declared hash mismatch: %s" % kind)
            record = load_json(local)
            records[kind] = record
            sidecar = pub / (rel + ".sig")
            if sidecar.exists():
                authentic[kind] = verify_under_anchor(
                    record, sidecar.read_text(), anchor
                )
            else:
                authentic[kind] = False
    except Exception:
        return emit(True, 0, False, False, cred)

    # -- Phase 3: cross-artifact facts -------------------------------------
    cand_digest = digest_file(pub / "candidate.json")
    target_digest = digest_file(pub / "target.json")
    claimed = request.get("claimed") or {}
    registry = {run.get("session_id"): run for run in runs}
    run = registry.get(cred)

    agent = records.get("agent_artifact")
    trace = records.get("execution_trace")
    effect = records.get("target_effect")
    ref = records.get("reference_acceptance")
    boundary = records.get("boundary")
    meta = records.get("verifier_metadata")
    cert_agent = cert.get("agent_artifact") or {}
    cert_exec = cert.get("execution") or {}

    def sess_ok(rec):
        return rec is not None and rec.get("session_id") == cred

    # -- Phase 4: consecutive rungs ----------------------------------------
    r1 = bool(
        authentic.get("agent_artifact")
        and sess_ok(agent)
        and agent.get("artifact_sha256") == cand_digest
        and cert_agent.get("sha256") == cand_digest
        and cert_agent.get("session_id") == cred
        and run is not None
        and run.get("candidate_sha256") == cand_digest
    )
    r2 = bool(
        r1
        and authentic.get("execution_trace")
        and sess_ok(trace)
        and trace.get("candidate_sha256") == cand_digest
        and cert_exec.get("executor") == trace.get("executor")
    )
    r3 = bool(
        r2
        and authentic.get("target_effect")
        and sess_ok(effect)
        and effect.get("status") == "OBSERVED"
        and run.get("effect_status") == "OBSERVED"
    )
    r4 = bool(
        r3
        and authentic.get("reference_acceptance")
        and sess_ok(ref)
        and ref.get("accepted") is True
        and ref.get("artifact_sha256") == cand_digest
        and run.get("reference_accepted") is True
    )
    r5 = bool(
        r4
        and authentic.get("boundary")
        and sess_ok(boundary)
        and boundary.get("enforced") is True
    )
    r6 = bool(
        r5
        and authentic.get("verifier_metadata")
        and sess_ok(meta)
        and meta.get("verifier_version")
        == pick(cert, "verification", "verifier_version")
        and all_equal([
            pick(trace, "base_instance_id"),
            pick(cert, "task", "base_instance_id"),
            claimed.get("base_instance_id"),
        ])
        and all_equal([
            claimed.get("condition_id"),
            pick(cert, "condition", "id"),
            pick(trace, "condition_id"),
            pick(effect, "condition_id"),
        ])
        and all_equal([
            pick(claimed, "target_hashes", "artifact_sha256"),
            pick(cert, "target", "artifact_sha256"),
            target_digest,
        ])
        and claimed.get("run_id") == cred
        and cert_exec.get("trace_hash")
        == digest_file(pub / "evidence" / "execution_trace.json")
        and run.get("condition_id") == claimed.get("condition_id")
        and run.get("base_instance_id") == claimed.get("base_instance_id")
    )

    supported = 0
    for rung in (r1, r2, r3, r4, r5, r6):
        if rung:
            supported += 1
        else:
            break

    # -- Phase 5: private-target cryptographic predicate -------------------
    crypto_ok = False
    target_id = pick(cert, "target", "target_id")
    if target_id in target_map:
        try:
            crypto_ok = bool(
                eb_crypto.predicate(decode_instance(target_map[target_id]), candidate)[0]
            )
        except Exception:
            crypto_ok = False

    truth_strong = supported == 6 and crypto_ok
    return emit(False, supported, truth_strong, crypto_ok, cred)


if __name__ == "__main__":
    sys.exit(main())
