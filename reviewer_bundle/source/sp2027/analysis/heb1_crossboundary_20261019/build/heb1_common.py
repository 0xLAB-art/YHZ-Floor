#!/usr/bin/env python3
"""HEB-1 case-assembly helpers (generator side only).

Canonical serialization, session/run records, certificate and request
builders, and the emit() writer used by the dev and held-out case
generators. Validators, the adjudicator, and the runner never import
this module.
"""
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path

VERIFIER_VERSION = "heb1-reference-v1"

STRONG_CLAIMS = {
    "artifact_authorship": "PROVEN",
    "execution_identity": "PROVEN",
    "target_effect": "OBSERVED",
    "reference_oracle_acceptance": "ACCEPTED",
    "boundary_enforcement": "PROVEN",
    "attribution": "PROVEN",
}


def jd(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)


def blob(obj) -> bytes:
    return (jd(obj) + "\n").encode("utf-8")


def h(obj) -> str:
    return hashlib.sha256(blob(obj)).hexdigest()


def sid(cid: str, role: str) -> str:
    return "sess-" + hashlib.sha256(f"heb1|{cid}|{role}".encode()).hexdigest()[:16]


def iid(cid: str, tag: str) -> str:
    return "inst-" + hashlib.sha256(f"heb1|{cid}|{tag}".encode()).hexdigest()[:12]


def sess(cid, role, cand, cond, inst, tid, faulty):
    """A run's honest operational record (generator-side ground truth)."""
    return {
        "sess": sid(cid, role),
        "cand": cand,
        "cand_h": h(cand),
        "effect": "NOT_OBSERVED" if faulty else "OBSERVED",
        "accepted": not faulty,
        "faulty": faulty,
        "cond": cond,
        "inst": inst,
        "tid": tid,
    }


def ev_bundle(s) -> dict:
    """The six honest evidence files for a coherent run."""
    return {
        "evidence/agent_artifact.json": {
            "session_id": s["sess"], "producer": "solver-agent",
            "artifact_path": "candidate.json", "artifact_sha256": s["cand_h"]},
        "evidence/execution_trace.json": {
            "session_id": s["sess"], "executor": "runner-01",
            "base_instance_id": s["inst"], "condition_id": s["cond"],
            "candidate_sha256": s["cand_h"]},
        "evidence/target_effect.json": {
            "status": s["effect"], "session_id": s["sess"], "target_id": s["tid"]},
        "evidence/reference_acceptance.json": {
            "accepted": s["accepted"], "artifact_sha256": s["cand_h"],
            "session_id": s["sess"]},
        "evidence/boundary.json": {
            "enforced": True, "interface_id": "ifce-heb1-t0"},
        "evidence/verifier_metadata.json": {
            "verifier_version": VERIFIER_VERSION},
    }


def build_cert(cid, prim, cond, inst, tid, target_h, agent_sess, exec_sess,
               claims, ev_keys) -> dict:
    return {
        "schema": "heb1-exploitation-attribution/1",
        "attempt_id": cid,
        "task": {"task_id": f"task-{prim}-nonce-reuse",
                 "base_instance_id": inst, "primitive": prim},
        "condition": {"id": cond},
        "target": {"target_id": tid, "artifact_sha256": target_h},
        "agent_artifact": {"session_id": agent_sess,
                           "path": "candidate.json", "sha256": ""},
        "execution": {"session_id": exec_sess, "executor": "runner-01",
                      "exit_status": "completed"},
        "verification": {"verifier_version": VERIFIER_VERSION},
        "claims": dict(claims),
        "evidence": [{"kind": Path(k).stem, "path": k, "sha256": ""}
                     for k in sorted(ev_keys)],
    }


def build_request(cid, run_id, cond, inst, target_h) -> dict:
    return {
        "case_id": cid,
        "candidate_path": "candidate.json",
        "claimed": {
            "run_id": run_id,
            "condition_id": cond,
            "base_instance_id": inst,
            "target_hashes": {"artifact_sha256": target_h},
            "claim_level": "attribution",
        },
    }


def reg_entry(s) -> dict:
    return {
        "condition_id": s["cond"],
        "base_instance_id": s["inst"],
        "candidate_sha256": s["cand_h"],
        "effect_status": s["effect"],
        "reference_accepted": s["accepted"],
        "crypto_ok": not s["faulty"],
        "target_id": s["tid"],
    }


def tent(tgt) -> dict:
    """Private-side target entry: recorded canonical hash + full state."""
    return {"sha256": h(tgt), "state": tgt}


def comp(family, mechanism, joins_failed, missing, mismatches,
         crypto_cert, crypto_requested, level, truth_strong, ops,
         malformed=False) -> dict:
    return {
        "family": family,
        "mechanism": mechanism,
        "intended": {
            "joins_failed": list(joins_failed),
            "missing_kinds": list(missing),
            "claim_mismatches": list(mismatches),
            "crypto_cert": crypto_cert,
            "crypto_requested": crypto_requested,
            "level": level,
            "truth_strong": truth_strong,
            "malformed": malformed,
        },
        "ops": list(ops),
    }


def emit(case_root: Path, private_root: Path, cid, prim, files, cert, request,
         registry, targets_map, cert_tid, req_tid, composition, expect,
         labels) -> None:
    """Write one case: public zone, private zone, label entry."""
    pub = case_root / cid / "public"
    if pub.exists():
        shutil.rmtree(pub)
    pub.mkdir(parents=True)
    hashes = {}
    for rel, obj in files.items():
        p = pub / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        data = blob(obj)
        p.write_bytes(data)
        hashes[rel] = hashlib.sha256(data).hexdigest()
    cert["agent_artifact"]["sha256"] = hashes["candidate.json"]
    for item in cert["evidence"]:
        item["sha256"] = hashes[item["path"]]
    (pub / "certificate.json").write_bytes(blob(cert))
    (pub / "request.json").write_bytes(blob(request))

    prv = private_root / cid
    if prv.exists():
        shutil.rmtree(prv)
    prv.mkdir(parents=True)
    (prv / "run_registry.json").write_bytes(blob(
        {"runs": registry, "composition_ops": composition["ops"]}))
    (prv / "targets.json").write_bytes(blob(
        {"cert_target_id": cert_tid, "requested_target_id": req_tid,
         "targets": targets_map}))
    (prv / "composition.json").write_bytes(blob(composition))

    labels[cid] = {
        "family": composition["family"],
        "primitive": prim,
        "mechanism": composition["mechanism"],
        "expected_systems": dict(expect),
    }
