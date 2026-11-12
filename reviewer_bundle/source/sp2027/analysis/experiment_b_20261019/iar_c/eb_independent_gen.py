#!/usr/bin/env python3
"""IAR-C independent adversarial case generator (Experiment B).

Structural-independence commitments
-----------------------------------
- Does NOT import eb_fixtures, eb_adjudicator, eb_v3_sig, eb_v3_full, or any
  frozen HEB-1 module. Only eb_crypto (target-domain primitives: ECDSA nonce
  reuse, ChaCha20 keystream reuse) plus the stdlib and `cryptography` Ed25519
  are used.
- Own ids, own key-derivation salt, own run builder, own scenario model, and
  an own truth model (the claim ladder implemented here, independently of the
  frozen adjudicator in ../eb_adjudicator.py).
- The wire format (evidence kinds, certificate fields, `.sig` sidecars, trust
  anchor) is the *interface* the three evaluated systems consume; it is
  schema-shared by necessity, not code-shared.

Scenario classes (per protocol EXPERIMENT_B_PROTOCOL.md, IAR-C section)
-----------------------------------------------------------------------
S1  clean success, full attribution (level 6)
S2  failed execution (no target effect), honest level-2 claim
S3  failed execution (wrong candidate), honest level-2 claim
S4  cross-run splice: failed run's records + successful candidate (C1)
S5  cross-condition: successful run relabeled to another condition (C2)
S6  stale instance/target: candidate from instance B claimed against A (C2)
S7  foreign authorship record: another authentic run's authorship (C1)
S8  foreign reference acceptance: another authentic run's reference (C1)
S9  forged trace signature: Y content signed by X's key (C2)
S10 forged authorship signature: Y content signed by X's key (C2)
S11 unsigned certificate executor rewrite (C2)
S12 unauthorized signer: valid signature under a key outside the anchor (C2)
S13 incomplete but legitimate evidence at levels k = 1..5 (honest fractions)
S14 unsupported higher claim: full claims over a level-3 evidence set
S15 malformed evidence (4 variants a-d)

Truth model: supported level = number of consecutive rungs satisfied by
authentic, registry-corroborated records bound to the credited execution
session (see `supported_level`); truth_strong = supported == 6 and the
cryptographic predicate recomputes True from the private target state.

Outputs (default): iar_c/data/{cases,private,labels,trust}
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
import eb_crypto  # noqa: E402

# ---- paths (module-level so a runner/scorer can re-point if ever needed) ----
ROOT = HERE / "data"
CASES = ROOT / "cases"
PRIV = ROOT / "private"
LABELS = ROOT / "labels" / "iar_c_labels.json"
TRUST = ROOT / "trust" / "iar_c_run_keys.json"
SEED = "eb-iar-c-20261019"

KINDS = [
    "agent_artifact",
    "execution_trace",
    "target_effect",
    "reference_acceptance",
    "boundary",
    "verifier_metadata",
]
LEVELS = [
    "artifact_authorship",
    "execution_identity",
    "target_effect",
    "reference_oracle_acceptance",
    "boundary_enforcement",
    "attribution",
]
STRONG = {
    "artifact_authorship": "PROVEN",
    "execution_identity": "PROVEN",
    "target_effect": "OBSERVED",
    "reference_oracle_acceptance": "ACCEPTED",
    "boundary_enforcement": "PROVEN",
    "attribution": "PROVEN",
}
PREDICATE = "task-specific-cryptographic-predicate-v1"
VERIFIER_VERSION = "heb1-reference-v1"

ANCHOR: dict[str, str] = {}


def blob(obj) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()


def hobj(obj) -> str:
    return hashlib.sha256(blob(obj)).hexdigest()


def sha_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def ser_inst(inst: dict) -> dict:
    return {k: ({"__hex__": v.hex()} if isinstance(v, bytes) else v) for k, v in inst.items()}


def full_claims() -> dict:
    return {name: STRONG[name] for name in LEVELS}


def partial_claims(k: int) -> dict:
    return {name: (STRONG[name] if i < k else "NOT_ESTABLISHED") for i, name in enumerate(LEVELS)}


def cid_for(scenario: str, prim: str, idx: int) -> str:
    return "ic-" + hashlib.sha256(f"eb-iar-c|{SEED}|{scenario}|{prim}|{idx}".encode()).hexdigest()[:10]


def sess_for(cid: str, role: str) -> str:
    return "ic-sess-" + hashlib.sha256(f"eb-iar-c|{cid}|{role}".encode()).hexdigest()[:16]


def iid_for(cid: str, tag: str) -> str:
    return "ic-inst-" + hashlib.sha256(f"eb-iar-c|{cid}|{tag}".encode()).hexdigest()[:12]


def key_for(session: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(
        hashlib.sha256(f"eb-iar-c|key|{session}".encode()).digest()
    )


def pub_for(session: str) -> str:
    return key_for(session).public_key().public_bytes_raw().hex()


def sign_record(record: dict, session: str) -> str:
    return key_for(session).sign(bytes.fromhex(hobj(record))).hex()


def build_run(cid, prim, role, cond, inst_id, tid, inst, outcome, cand=None) -> dict:
    session = sess_for(cid, role)
    if outcome == "success":
        cand = eb_crypto.good_candidate(prim, f"eb-iar-c|{cid}|{role}|cand".encode(), inst)
        status, accepted, crypto_ok = "OBSERVED", True, True
    elif outcome == "fail-op":
        if cand is None:
            raise ValueError("fail-op needs an explicit candidate")
        status, accepted = "NOT_OBSERVED", False
        crypto_ok = bool(eb_crypto.predicate(inst, cand)[0])
    elif outcome == "fail-crypto":
        cand = eb_crypto.bad_candidate(prim, inst)
        status, accepted, crypto_ok = "NOT_OBSERVED", False, False
    else:
        raise ValueError(f"unknown outcome {outcome}")
    cand_h = hashlib.sha256(eb_crypto.candidate_bytes(cand)).hexdigest()
    executor = f"ic-executor-{role}"
    records = {
        "agent_artifact": {
            "session_id": session,
            "artifact": "candidate.json",
            "artifact_sha256": cand_h,
            "producer": f"ic-run-{role}",
        },
        "execution_trace": {
            "session_id": session,
            "base_instance_id": inst_id,
            "condition_id": cond,
            "executor": executor,
            "candidate_sha256": cand_h,
        },
        "target_effect": {
            "session_id": session,
            "status": status,
            "predicate": PREDICATE,
            "condition_id": cond,
        },
        "reference_acceptance": {
            "session_id": session,
            "accepted": accepted,
            "artifact_sha256": cand_h,
        },
        "boundary": {
            "session_id": session,
            "enforced": True,
            "allowed_interface": "iface-ic-t0",
        },
        "verifier_metadata": {
            "session_id": session,
            "verifier_version": VERIFIER_VERSION,
            "implementation": "ic-independent-v1",
        },
    }
    return {
        "session": session,
        "role": role,
        "cond": cond,
        "inst_id": inst_id,
        "tid": tid,
        "cand": cand,
        "cand_h": cand_h,
        "status": status,
        "accepted": accepted,
        "crypto_ok": crypto_ok,
        "executor": executor,
        "records": records,
    }


def reg_entry(run: dict, tid: str) -> dict:
    return {
        "session_id": run["session"],
        "role": run["role"],
        "condition_id": run["cond"],
        "base_instance_id": run["inst_id"],
        "candidate_sha256": run["cand_h"],
        "effect_status": run["status"],
        "reference_accepted": run["accepted"],
        "crypto_ok": run["crypto_ok"],
        "executor": run["executor"],
        "target_id": tid,
    }


def base_case(cid, prim, scenario, mechanism) -> dict:
    inst_id = iid_for(cid, "a")
    tid = "tid-" + inst_id
    inst = eb_crypto.make_instance(prim, f"eb-iar-c|{cid}|a".encode())
    return {
        "cid": cid,
        "prim": prim,
        "scenario": scenario,
        "mechanism": mechanism,
        "inst_id": inst_id,
        "tid": tid,
        "inst": inst,
        "targets_map": {tid: inst},
        "claimed_tid": tid,
        "claimed_inst": inst_id,
        "claimed_cond": "cond-0",
        "breaks": [],
        "ops": [mechanism],
    }


def write_case(case: dict):
    cid = case["cid"]
    prim = case["prim"]
    pub = CASES / cid / "public"
    priv = PRIV / cid
    evdir = pub / "evidence"
    evdir.mkdir(parents=True, exist_ok=True)
    priv.mkdir(parents=True, exist_ok=True)

    (pub / "candidate.json").write_bytes(eb_crypto.candidate_bytes(case["cand"]))
    (pub / "target.json").write_bytes(blob(eb_crypto.public_target(case["targets_map"][case["claimed_tid"]])))

    evidence = []
    for kind, rec, sig_session in case["evidence"]:
        fp = evdir / f"{kind}.json"
        fp.write_bytes(blob(rec))
        (evdir / f"{kind}.json.sig").write_bytes((sign_record(rec, sig_session) + "\n").encode())
        evidence.append({"kind": kind, "path": f"evidence/{kind}.json", "sha256": sha_file(fp)})

    trace_path = evdir / "execution_trace.json"
    trace_hash = sha_file(trace_path) if trace_path.exists() else ""
    if case.get("trace_hash_override") is not None:
        trace_hash = case["trace_hash_override"]

    cred_executor = case.get("cred_executor", case["cred"])
    cert = {
        "schema": "heb1-signed/1",
        "attempt_id": f"ic-attempt-{cid}",
        "task": {
            "task_id": f"task-{prim}-nonce-reuse",
            "base_instance_id": case["claimed_inst"],
            "primitive": prim,
        },
        "condition": {"id": case["claimed_cond"]},
        "target": {"target_id": case["claimed_tid"], "artifact_sha256": sha_file(pub / "target.json")},
        "agent_artifact": {
            "session_id": case.get("cert_agent_session", case["cred"]),
            "path": "candidate.json",
            "sha256": sha_file(pub / "candidate.json"),
        },
        "execution": {
            "session_id": case["cred"],
            "executor": case.get("cert_executor", cred_executor),
            "exit_status": "completed",
            "trace_hash": trace_hash,
        },
        "verification": {"verifier_version": VERIFIER_VERSION},
        "claims": case["claims"],
        "evidence": evidence,
    }
    request = {
        "case_id": cid,
        "candidate_path": "candidate.json",
        "claimed": {
            "run_id": case["cred"],
            "condition_id": case["claimed_cond"],
            "base_instance_id": case["claimed_inst"],
            "target_hashes": {"artifact_sha256": sha_file(pub / "target.json")},
            "claim_level": LEVELS[case["request_level"] - 1],
        },
    }
    (pub / "certificate.json").write_bytes(blob(cert))
    (pub / "request.json").write_bytes(blob(request))

    registry = [reg_entry(run, run["tid"]) for run in case["registry_runs"]]
    targets = {
        "cert_target_id": case["claimed_tid"],
        "requested_target_id": case["claimed_tid"],
        "targets": {tid: ser_inst(inst) for tid, inst in case["targets_map"].items()},
    }
    composition = {
        "scenario": case["scenario"],
        "primitive": prim,
        "mechanism": case["mechanism"],
        "ops": case["ops"],
        "cred": case["cred"],
        "request_level": case["request_level"],
    }
    (priv / "run_registry.json").write_bytes(blob({"runs": registry}))
    (priv / "targets.json").write_bytes(blob(targets))
    (priv / "composition.json").write_bytes(blob(composition))

    for run in case["registry_runs"]:
        ANCHOR[run["session"]] = pub_for(run["session"])

    for tag in case["breaks"]:
        if tag == "del_candidate":
            (pub / "candidate.json").unlink()
        elif tag == "del_target":
            (pub / "target.json").unlink()
        elif tag == "corrupt_evidence":
            (evdir / "target_effect.json").write_bytes(b"{ not json\n")
        elif tag == "stale_hash":
            with (evdir / "execution_trace.json").open("ab") as fh:
                fh.write(b" ")
        else:
            raise ValueError(f"unknown break {tag}")

    entry = {
        "family": case["scenario"],
        "primitive": prim,
        "mechanism": case["mechanism"],
        "expected_systems": case["expected_systems"],
        "expected_adjudicator": case["expected_adj"],
    }
    return cid, entry


# --------------------------------------------------------------------------
# scenarios
# --------------------------------------------------------------------------

def sc_success(prim, idx=1):
    cid = cid_for("S1", prim, idx)
    c = base_case(cid, prim, "S1", "clean-success-full-attribution")
    r = build_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    c.update(
        cand=r["cand"], cred=r["session"], cred_executor=r["executor"], registry_runs=[r],
        evidence=[(k, r["records"][k], r["session"]) for k in KINDS],
        claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "EMIT", "level": 6},
            "v3sig": {"decision": "ACCEPT", "supported": 6},
            "v3full": {"decision": "ACCEPT", "supported": 6},
        },
        expected_adj={"supported": 6, "truth_strong": True, "crypto_ok": True, "malformed": False},
    )
    return c


def _fail_honest(prim, idx, mode):
    scenario = "S2" if mode == "op" else "S3"
    mechanism = "clean-failure-%s-honest-level-2" % ("no-effect" if mode == "op" else "wrong-candidate")
    cid = cid_for(scenario, prim, idx)
    c = base_case(cid, prim, scenario, mechanism)
    if mode == "op":
        cand = eb_crypto.good_candidate(prim, f"eb-iar-c|{cid}|r|cand".encode(), c["inst"])
        r = build_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"], c["inst"], "fail-op", cand=cand)
    else:
        r = build_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"], c["inst"], "fail-crypto")
    c.update(
        cand=r["cand"], cred=r["session"], cred_executor=r["executor"], registry_runs=[r],
        evidence=[(k, r["records"][k], r["session"]) for k in KINDS],
        claims=partial_claims(2), request_level=2,
        expected_systems={
            "v2": {"decision": "REJECT", "level": 2},
            "v3sig": {"decision": "ACCEPT", "supported": 2},
            "v3full": {"decision": "ACCEPT", "supported": 2},
        },
        expected_adj={"supported": 2, "truth_strong": False, "crypto_ok": mode == "op", "malformed": False},
    )
    return c


def sc_fail_op(prim, idx=1):
    return _fail_honest(prim, idx, "op")


def sc_fail_crypto(prim, idx=1):
    return _fail_honest(prim, idx, "crypto")


def sc_cross_run(prim, idx=1):
    cid = cid_for("S4", prim, idx)
    c = base_case(cid, prim, "S4", "cross-run-splice-failed-records-with-successful-candidate")
    xr = build_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"], c["inst"], "fail-crypto")
    yr = build_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    ev = [(k, yr["records"][k], yr["session"]) for k in KINDS]
    for k in ("agent_artifact", "execution_trace", "boundary", "verifier_metadata"):
        ev[KINDS.index(k)] = (k, xr["records"][k], xr["session"])
    c.update(
        cand=yr["cand"], cred=yr["session"], cred_executor=yr["executor"], registry_runs=[xr, yr],
        evidence=ev, claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "REJECT", "level": 0},
            "v3sig": {"decision": "ACCEPT", "supported": 6},
            "v3full": {"decision": "REJECT", "supported": 0},
        },
        expected_adj={"supported": 0, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_cross_condition(prim, idx=1):
    cid = cid_for("S5", prim, idx)
    c = base_case(cid, prim, "S5", "cross-condition-relabel")
    z = build_run(cid, prim, "z", "cond-1", c["inst_id"], c["tid"], c["inst"], "success")
    c.update(
        cand=z["cand"], cred=z["session"], cred_executor=z["executor"], registry_runs=[z],
        evidence=[(k, z["records"][k], z["session"]) for k in KINDS],
        claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "REJECT", "level": 5},
            "v3sig": {"decision": "ACCEPT", "supported": 6},
            "v3full": {"decision": "REJECT", "supported": 5},
        },
        expected_adj={"supported": 5, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_stale_instance(prim, idx=1):
    cid = cid_for("S6", prim, idx)
    c = base_case(cid, prim, "S6", "stale-instance-target-swap")
    inst1 = eb_crypto.make_instance(prim, f"eb-iar-c|{cid}|b".encode())
    iid1 = iid_for(cid, "b")
    tid1 = "tid-" + iid1
    z = build_run(cid, prim, "z", "cond-0", iid1, tid1, inst1, "success")
    c["targets_map"] = {c["tid"]: c["inst"], tid1: inst1}
    c.update(
        cand=z["cand"], cred=z["session"], cred_executor=z["executor"], registry_runs=[z],
        evidence=[(k, z["records"][k], z["session"]) for k in KINDS],
        claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "REJECT", "level": 5},
            "v3sig": {"decision": "ACCEPT", "supported": 6},
            "v3full": {"decision": "REJECT", "supported": 5},
        },
        expected_adj={"supported": 5, "truth_strong": False, "crypto_ok": False, "malformed": False},
    )
    return c


def sc_foreign_authorship(prim, idx=1):
    cid = cid_for("S7", prim, idx)
    c = base_case(cid, prim, "S7", "foreign-authentic-authorship")
    yr = build_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    xr = build_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"], c["inst"], "fail-op", cand=yr["cand"])
    ev = [(k, yr["records"][k], yr["session"]) for k in KINDS]
    ev[0] = ("agent_artifact", xr["records"]["agent_artifact"], xr["session"])
    c.update(
        cand=yr["cand"], cred=yr["session"], cred_executor=yr["executor"], registry_runs=[xr, yr],
        evidence=ev, claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "EMIT", "level": 6},
            "v3sig": {"decision": "ACCEPT", "supported": 6},
            "v3full": {"decision": "REJECT", "supported": 0},
        },
        expected_adj={"supported": 0, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_foreign_reference(prim, idx=1):
    cid = cid_for("S8", prim, idx)
    c = base_case(cid, prim, "S8", "foreign-authentic-reference-acceptance")
    yr = build_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    inst1 = eb_crypto.make_instance(prim, f"eb-iar-c|{cid}|b".encode())
    iid1 = iid_for(cid, "b")
    tid1 = "tid-" + iid1
    zr = build_run(cid, prim, "z", "cond-0", iid1, tid1, inst1, "success")
    c["targets_map"] = {c["tid"]: c["inst"], tid1: inst1}
    ev = [(k, yr["records"][k], yr["session"]) for k in KINDS]
    ev[3] = ("reference_acceptance", zr["records"]["reference_acceptance"], zr["session"])
    c.update(
        cand=yr["cand"], cred=yr["session"], cred_executor=yr["executor"], registry_runs=[yr, zr],
        evidence=ev, claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "REJECT", "level": 3},
            "v3sig": {"decision": "ACCEPT", "supported": 6},
            "v3full": {"decision": "REJECT", "supported": 3},
        },
        expected_adj={"supported": 3, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_forged_trace(prim, idx=1):
    cid = cid_for("S9", prim, idx)
    c = base_case(cid, prim, "S9", "forged-trace-signature")
    yr = build_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    xr = build_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"], c["inst"], "fail-op", cand=yr["cand"])
    ev = [(k, yr["records"][k], yr["session"]) for k in KINDS]
    ev[1] = ("execution_trace", yr["records"]["execution_trace"], xr["session"])
    c.update(
        cand=yr["cand"], cred=yr["session"], cred_executor=yr["executor"], registry_runs=[xr, yr],
        evidence=ev, claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "EMIT", "level": 6},
            "v3sig": {"decision": "REJECT", "supported": None},
            "v3full": {"decision": "REJECT", "supported": None},
        },
        expected_adj={"supported": 1, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_forged_authorship(prim, idx=1):
    cid = cid_for("S10", prim, idx)
    c = base_case(cid, prim, "S10", "forged-authorship-signature")
    yr = build_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    xr = build_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"], c["inst"], "fail-op", cand=yr["cand"])
    ev = [(k, yr["records"][k], yr["session"]) for k in KINDS]
    ev[0] = ("agent_artifact", yr["records"]["agent_artifact"], xr["session"])
    c.update(
        cand=yr["cand"], cred=yr["session"], cred_executor=yr["executor"], registry_runs=[xr, yr],
        evidence=ev, claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "EMIT", "level": 6},
            "v3sig": {"decision": "REJECT", "supported": None},
            "v3full": {"decision": "REJECT", "supported": None},
        },
        expected_adj={"supported": 0, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_executor_rewrite(prim, idx=1):
    cid = cid_for("S11", prim, idx)
    c = base_case(cid, prim, "S11", "unsigned-executor-rewrite")
    yr = build_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    c.update(
        cand=yr["cand"], cred=yr["session"], cred_executor=yr["executor"], registry_runs=[yr],
        evidence=[(k, yr["records"][k], yr["session"]) for k in KINDS],
        claims=full_claims(), request_level=6, cert_executor="ic-executor-x",
        expected_systems={
            "v2": {"decision": "EMIT", "level": 6},
            "v3sig": {"decision": "ACCEPT", "supported": 6},
            "v3full": {"decision": "REJECT", "supported": 1},
        },
        expected_adj={"supported": 1, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_unauthorized_signer(prim, idx=1):
    cid = cid_for("S12", prim, idx)
    c = base_case(cid, prim, "S12", "unauthorized-signer-record")
    yr = build_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    unauth_session = "ic-sess-unauth-" + hashlib.sha256(f"eb-iar-c|{cid}|unauth".encode()).hexdigest()[:10]
    rec = dict(yr["records"]["agent_artifact"], session_id=unauth_session)
    ev = [(k, yr["records"][k], yr["session"]) for k in KINDS]
    ev[0] = ("agent_artifact", rec, unauth_session)  # key never registered in the anchor
    c.update(
        cand=yr["cand"], cred=yr["session"], cred_executor=yr["executor"], registry_runs=[yr],
        evidence=ev, claims=full_claims(), request_level=6, cert_agent_session=yr["session"],
        expected_systems={
            "v2": {"decision": "EMIT", "level": 6},
            "v3sig": {"decision": "REJECT", "supported": None},
            "v3full": {"decision": "REJECT", "supported": None},
        },
        expected_adj={"supported": 0, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_incomplete(prim, k):
    cid = cid_for("S13", prim, k)
    c = base_case(cid, prim, "S13", f"incomplete-legitimate-level-{k}")
    r = build_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    c.update(
        cand=r["cand"], cred=r["session"], cred_executor=r["executor"], registry_runs=[r],
        evidence=[(kind, r["records"][kind], r["session"]) for kind in KINDS[:k]],
        claims=partial_claims(k), request_level=k,
        expected_systems={
            "v2": {"decision": "REJECT", "level": 0},
            "v3sig": {"decision": "ACCEPT", "supported": k},
            "v3full": {"decision": "ACCEPT", "supported": k},
        },
        expected_adj={"supported": k, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_unsupported_high(prim, idx=1):
    cid = cid_for("S14", prim, idx)
    c = base_case(cid, prim, "S14", "unsupported-high-claim-over-partial-evidence")
    r = build_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    c.update(
        cand=r["cand"], cred=r["session"], cred_executor=r["executor"], registry_runs=[r],
        evidence=[(kind, r["records"][kind], r["session"]) for kind in KINDS[:3]],
        claims=full_claims(), request_level=6,
        expected_systems={
            "v2": {"decision": "REJECT", "level": 0},
            "v3sig": {"decision": "ACCEPT", "supported": 6},
            "v3full": {"decision": "REJECT", "supported": 3},
        },
        expected_adj={"supported": 3, "truth_strong": False, "crypto_ok": True, "malformed": False},
    )
    return c


def sc_malformed(prim, tag):
    cid = cid_for("S15", prim, tag)
    c = base_case(cid, prim, "S15", f"malformed-{tag}")
    r = build_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
    breaks = {"a": ["del_candidate"], "b": ["corrupt_evidence"], "c": ["stale_hash"], "d": ["del_target"]}[tag]
    c.update(
        cand=r["cand"], cred=r["session"], cred_executor=r["executor"], registry_runs=[r],
        evidence=[(k, r["records"][k], r["session"]) for k in KINDS],
        claims=full_claims(), request_level=6, breaks=breaks,
        expected_systems={
            "v2": {"decision": "REJECT", "level": 0},
            "v3sig": {"decision": "REJECT", "supported": None},
            "v3full": {"decision": "REJECT", "supported": None},
        },
        expected_adj={"supported": 0, "truth_strong": False, "crypto_ok": False, "malformed": True},
    )
    return c


SCENARIOS = [
    sc_success, sc_fail_op, sc_fail_crypto, sc_cross_run, sc_cross_condition,
    sc_stale_instance, sc_foreign_authorship, sc_foreign_reference,
    sc_forged_trace, sc_forged_authorship, sc_executor_rewrite, sc_unauthorized_signer,
]
PRIMS = ["ecdsa", "chacha"]


def build_cases() -> list:
    cases = []
    for prim in PRIMS:
        for fn in SCENARIOS:
            cases.append(fn(prim, 1))
        for k in range(1, 6):
            cases.append(sc_incomplete(prim, k))
        cases.append(sc_unsupported_high(prim, 1))
        for tag in ["a", "b", "c", "d"]:
            cases.append(sc_malformed(prim, tag))
    return cases


def build_all():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ANCHOR.clear()
    labels = {}
    for case in build_cases():
        cid, entry = write_case(case)
        if cid in labels:
            raise ValueError(f"duplicate cid {cid}")
        labels[cid] = entry
    LABELS.parent.mkdir(parents=True, exist_ok=True)
    TRUST.parent.mkdir(parents=True, exist_ok=True)
    LABELS.write_bytes(blob(labels))
    TRUST.write_bytes(blob({"schema": "eb-trust-anchor/1", "keys": ANCHOR}))
    return labels


def main() -> int:
    labels = build_all()
    fam_counts: dict[str, int] = {}
    for entry in labels.values():
        fam_counts[entry["family"]] = fam_counts.get(entry["family"], 0) + 1
    info = {
        "cases": len(labels),
        "families": dict(sorted(fam_counts.items())),
        "seed": SEED,
        "labels": str(LABELS),
        "labels_sha256": sha_file(LABELS),
        "trust": str(TRUST),
        "trust_sha256": sha_file(TRUST),
        "anchors": len(ANCHOR),
    }
    print(json.dumps(info, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
