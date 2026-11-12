#!/usr/bin/env python3
"""Experiment B / IAR-B signed-run fixture builder.

Builds deterministic signed bundles in the `heb1-signed/1` format so that the
frozen HEB-1 V2 validator can read them unchanged, alongside an Ed25519 trust
anchor that lives outside the composer's control.

Layout (all module globals are monkey-patchable for held-out generation):

  iar_b/cases/<zone>/<cid>/public/{candidate.json,target.json,certificate.json,
                                   request.json,evidence/<kind>.json,
                                   evidence/<kind>.json.sig}
  iar_b/private/<zone>/<cid>/{run_registry.json,targets.json,composition.json}
  iar_b/labels/<zone>_labels.json
  iar_b/trust/<zone>_run_keys.json

The certificate is V2-compatible: V2 ignores the schema string value and the
signature sidecars, so the same public dir serves the unsigned baseline and
the authenticated-provenance systems.

No frozen HEB-1 code is imported. Crypto comes from eb_crypto.py.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eb_crypto  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE / "iar_b"
CASES = ROOT / "cases" / "dev"
PRIV = ROOT / "private" / "dev"
LABELS = ROOT / "labels" / "dev_labels.json"
TRUST = ROOT / "trust" / "dev_run_keys.json"
SEED = "eb-iar-b-dev-20261019"

LEVELS = ["artifact_authorship", "execution_identity", "target_effect",
          "reference_oracle_acceptance", "boundary_enforcement", "attribution"]
FULL_CLAIMS = {"artifact_authorship": "PROVEN", "execution_identity": "PROVEN",
               "target_effect": "OBSERVED",
               "reference_oracle_acceptance": "ACCEPTED",
               "boundary_enforcement": "PROVEN", "attribution": "PROVEN"}
EVIDENCE_ORDER = ["agent_artifact", "execution_trace", "target_effect",
                  "reference_acceptance", "boundary", "verifier_metadata"]
PREDICATE = "task-specific-cryptographic-predicate-v1"


def partial_claims(k):
    out = {}
    for i, name in enumerate(LEVELS):
        out[name] = FULL_CLAIMS[name] if i < k else "NOT_ESTABLISHED"
    return out


def jd(obj):
    return json.dumps(obj, indent=2, sort_keys=True)


def blob(obj):
    return (jd(obj) + "\n").encode()


def hb(data):
    return hashlib.sha256(data).hexdigest()


def hobj(obj):
    return hb(blob(obj))


def sha_file(path):
    return hb(Path(path).read_bytes())


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def ser_inst(inst):
    out = {}
    for key, val in inst.items():
        out[key] = {"__hex__": val.hex()} if isinstance(val, bytes) else val
    return out


def de_inst(obj):
    out = {}
    for key, val in obj.items():
        if isinstance(val, dict) and "__hex__" in val:
            out[key] = bytes.fromhex(val["__hex__"])
        else:
            out[key] = val
    return out


def cid_for(family, prim, idx):
    return "eb-" + hashlib.sha256(
        f"iar-b|{SEED}|{family}|{prim}|{idx}".encode()).hexdigest()[:10]


def sess_for(cid, role):
    return "eb-sess-" + hashlib.sha256(f"eb|{cid}|{role}".encode()).hexdigest()[:16]


def iid_for(cid, tag):
    return "eb-inst-" + hashlib.sha256(f"eb|{cid}|{tag}".encode()).hexdigest()[:12]


def key_for(session):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    return Ed25519PrivateKey.from_private_bytes(
        hashlib.sha256(f"eb-iar-b|key|{session}".encode()).digest())


def pub_for(session):
    return key_for(session).public_key().public_bytes_raw().hex()


def sign_record(record, session):
    return key_for(session).sign(bytes.fromhex(hobj(record))).hex()


def make_instance(prim, cid, tag):
    return eb_crypto.make_instance(prim, f"{SEED}|{cid}|{tag}".encode())


def make_run(cid, prim, role, cond, inst_id, tid, inst, outcome, cand=None):
    session = sess_for(cid, role)
    if outcome == "success":
        cand = eb_crypto.good_candidate(prim, f"{cid}|{role}|cand".encode(), inst)
    elif outcome == "fail-op":
        if cand is None:
            raise ValueError("fail-op needs candidate bytes")
    elif outcome == "fail-crypto":
        cand = eb_crypto.bad_candidate(prim, inst)
    else:
        raise ValueError(outcome)
    ok, _ = eb_crypto.predicate(inst, cand)
    if outcome == "success" and not ok:
        raise AssertionError("success candidate must verify")
    status = "OBSERVED" if outcome == "success" else "NOT_OBSERVED"
    accepted = outcome == "success"
    cand_h = hb(eb_crypto.candidate_bytes(cand))
    executor = f"eb-executor-{role}"
    records = {
        "agent_artifact": {"session_id": session, "artifact": "candidate.json",
                           "artifact_sha256": cand_h, "producer": f"eb-run-{role}"},
        "execution_trace": {"session_id": session, "base_instance_id": inst_id,
                            "condition_id": cond, "executor": executor,
                            "candidate_sha256": cand_h},
        "target_effect": {"session_id": session, "status": status,
                          "predicate": PREDICATE, "condition_id": cond},
        "reference_acceptance": {"session_id": session, "accepted": accepted,
                                 "artifact_sha256": cand_h},
        "boundary": {"session_id": session, "enforced": True,
                     "allowed_interface": "iface-eb-t0"},
        "verifier_metadata": {"session_id": session,
                              "verifier_version": "heb1-reference-v1",
                              "implementation": "eb-independent-v1"},
    }
    return {"session": session, "role": role, "cond": cond, "inst_id": inst_id,
            "tid": tid, "cand": cand, "cand_h": cand_h, "status": status,
            "accepted": accepted, "crypto_ok": ok, "executor": executor,
            "records": records}


def reg_entry(run):
    return {"session_id": run["session"], "role": run["role"],
            "condition_id": run["cond"], "base_instance_id": run["inst_id"],
            "candidate_sha256": run["cand_h"], "effect_status": run["status"],
            "reference_accepted": run["accepted"], "crypto_ok": run["crypto_ok"],
            "target_id": run["tid"], "executor": run["executor"]}


ANCHOR = {}


def write_case(case):
    cid = case["cid"]
    pub = CASES / cid / "public"
    ev = pub / "evidence"
    priv = PRIV / cid
    ev.mkdir(parents=True, exist_ok=True)
    priv.mkdir(parents=True, exist_ok=True)

    cand_bytes = eb_crypto.candidate_bytes(case["cand"])
    assert hb(cand_bytes) == hobj(case["cand"])
    (pub / "candidate.json").write_bytes(cand_bytes)

    target_obj = eb_crypto.public_target(case["targets_map"][case["claimed_tid"]])
    (pub / "target.json").write_bytes(blob(target_obj))

    ev_meta = []
    for kind, record, sig_session in case["evidence"]:
        path = ev / f"{kind}.json"
        path.write_bytes(blob(record))
        (ev / f"{kind}.json.sig").write_text(sign_record(record, sig_session) + "\n")
        ev_meta.append({"kind": kind, "path": f"evidence/{kind}.json",
                        "sha256": sha_file(path)})

    trace_hash = ""
    for kind, record, _ in case["evidence"]:
        if kind == "execution_trace":
            trace_hash = sha_file(ev / "execution_trace.json")
    if case.get("trace_hash_override") is not None:
        trace_hash = case["trace_hash_override"]

    authorship = case["evidence"][0][1] if case["evidence"] else {}
    cert_agent_session = case.get("cert_agent_session", authorship.get("session_id"))
    cred_executor = case.get("cert_executor")
    if cred_executor is None:
        cred_executor = next(r["executor"] for r in case["registry_runs"]
                             if r["session"] == case["cred"])
    cert = {
        "schema": "heb1-signed/1",
        "attempt_id": f"eb-attempt-{cid}",
        "task": {"task_id": f"task-{case['prim']}-nonce-reuse",
                 "base_instance_id": case["claimed_inst"],
                 "primitive": case["prim"]},
        "condition": {"id": case["claimed_cond"]},
        "target": {"target_id": case["claimed_tid"],
                   "artifact_sha256": sha_file(pub / "target.json")},
        "agent_artifact": {"session_id": cert_agent_session,
                           "path": "candidate.json",
                           "sha256": sha_file(pub / "candidate.json")},
        "execution": {"session_id": case["cred"], "executor": cred_executor,
                      "exit_status": "completed", "trace_hash": trace_hash},
        "verification": {"verifier_version": "heb1-reference-v1"},
        "claims": case["claims"],
        "evidence": ev_meta,
    }
    (pub / "certificate.json").write_bytes(blob(cert))

    request = {"case_id": cid, "candidate_path": "candidate.json",
               "claimed": {"run_id": case["cred"],
                           "condition_id": case["claimed_cond"],
                           "base_instance_id": case["claimed_inst"],
                           "target_hashes": {"artifact_sha256":
                                             sha_file(pub / "target.json")},
                           "claim_level": LEVELS[case["request_level"] - 1]}}
    (pub / "request.json").write_bytes(blob(request))

    (priv / "run_registry.json").write_bytes(blob({"runs": [
        reg_entry(r) for r in case["registry_runs"]]}))
    (priv / "targets.json").write_bytes(blob({
        "cert_target_id": case["claimed_tid"],
        "requested_target_id": case["claimed_tid"],
        "targets": {tid: ser_inst(inst)
                    for tid, inst in case["targets_map"].items()},
    }))
    (priv / "composition.json").write_bytes(blob({
        "family": case["family"], "primitive": case["prim"],
        "mechanism": case["mechanism"], "ops": case["ops"],
        "cred": case["cred"], "request_level": case["request_level"],
    }))

    for run in case["registry_runs"]:
        ANCHOR[run["session"]] = pub_for(run["session"])

    breaks = case.get("breaks", [])
    if "del_candidate" in breaks:
        (pub / "candidate.json").unlink()
    if "del_target" in breaks:
        (pub / "target.json").unlink()
    if "touch_trace" in breaks:
        p = ev / "execution_trace.json"
        p.write_bytes(p.read_bytes() + b" ")
    if "corrupt_effect" in breaks:
        (ev / "target_effect.json").write_bytes(b"{ not json\n")

    entry = {
        "family": case["family"], "primitive": case["prim"],
        "mechanism": case["mechanism"],
        "expected_systems": case["expected_systems"],
        "expected_adjudicator": case["expected_adj"],
    }
    return cid, entry


# ---------------------------------------------------------------- families

def base_case(cid, prim, family, mechanism):
    inst_id = iid_for(cid, "a")
    tid = "tid-" + iid_for(cid, "a")
    inst = make_instance(prim, cid, "a")
    return {"cid": cid, "prim": prim, "family": family,
            "mechanism": mechanism, "inst_id": inst_id, "tid": tid,
            "inst": inst, "targets_map": {tid: inst}, "claimed_tid": tid,
            "claimed_inst": inst_id, "claimed_cond": "cond-0",
            "breaks": [], "ops": [mechanism]}


def exp(v2, v3sig, v3full, adj):
    return v2, v3sig, v3full, adj


def fam_h0(prim, idx):
    cid = cid_for("H0", prim, idx)
    c = base_case(cid, prim, "H0", "clean-coherent-success")
    run = make_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"],
                   c["inst"], "success")
    c.update({"cand": run["cand"], "cred": run["session"],
              "registry_runs": [run],
              "evidence": [(k, run["records"][k], run["session"])
                           for k in EVIDENCE_ORDER],
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "expected_systems": {
                  "v2": {"decision": "EMIT", "level": 6},
                  "v3sig": {"decision": "ACCEPT", "supported": 6},
                  "v3full": {"decision": "ACCEPT", "supported": 6}},
              "expected_adj": {"supported": 6, "truth_strong": True,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h1(prim, idx):
    cid = cid_for("H1", prim, idx)
    c = base_case(cid, prim, "H1", "cross-run-c1-splice")
    xr = make_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "fail-crypto")
    yr = make_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "success")
    c.update({"cand": yr["cand"], "cred": xr["session"],
              "registry_runs": [xr, yr],
              "evidence": [
                  ("agent_artifact", xr["records"]["agent_artifact"], xr["session"]),
                  ("execution_trace", xr["records"]["execution_trace"], xr["session"]),
                  ("target_effect", yr["records"]["target_effect"], yr["session"]),
                  ("reference_acceptance", yr["records"]["reference_acceptance"], yr["session"]),
                  ("boundary", xr["records"]["boundary"], xr["session"]),
                  ("verifier_metadata", xr["records"]["verifier_metadata"], xr["session"])],
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "ops": ["candidate=Y", "authorship/trace/boundary/metadata=X authentic",
                      "effect/reference=Y authentic", "cred=X session"],
              "expected_systems": {
                  "v2": {"decision": "REJECT", "level": 0},
                  "v3sig": {"decision": "ACCEPT", "supported": 6},
                  "v3full": {"decision": "REJECT", "supported": 0}},
              "expected_adj": {"supported": 0, "truth_strong": False,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h2(prim, idx):
    cid = cid_for("H2", prim, idx)
    c = base_case(cid, prim, "H2", "cross-condition-relabel")
    zr = make_run(cid, prim, "z", "cond-1", c["inst_id"], c["tid"],
                  c["inst"], "success")
    c.update({"cand": zr["cand"], "cred": zr["session"],
              "claimed_cond": "cond-0",
              "registry_runs": [zr],
              "evidence": [(k, zr["records"][k], zr["session"])
                           for k in EVIDENCE_ORDER],
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "ops": ["records authentic under cond-1",
                      "cert/request claim cond-0"],
              "expected_systems": {
                  "v2": {"decision": "REJECT", "level": 5},
                  "v3sig": {"decision": "ACCEPT", "supported": 6},
                  "v3full": {"decision": "REJECT", "supported": 5}},
              "expected_adj": {"supported": 5, "truth_strong": False,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h3(prim, idx):
    cid = cid_for("H3", prim, idx)
    c = base_case(cid, prim, "H3", "stale-instance-target-swap")
    inst0 = c["inst"]
    inst1 = make_instance(prim, cid, "b")
    tid1 = "tid-" + iid_for(cid, "b")
    zr = make_run(cid, prim, "z", "cond-0", iid_for(cid, "b"), tid1,
                  inst1, "success")
    c.update({"cand": zr["cand"], "cred": zr["session"],
              "targets_map": {c["tid"]: inst0, tid1: inst1},
              "registry_runs": [zr],
              "evidence": [(k, zr["records"][k], zr["session"])
                           for k in EVIDENCE_ORDER],
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "ops": ["candidate solves inst-1", "claimed target = inst-0",
                      "trace base_instance_id = inst-1"],
              "expected_systems": {
                  "v2": {"decision": "REJECT", "level": 5},
                  "v3sig": {"decision": "ACCEPT", "supported": 6},
                  "v3full": {"decision": "REJECT", "supported": 5}},
              "expected_adj": {"supported": 5, "truth_strong": False,
                               "crypto_ok": False, "malformed": False}})
    return c


def fam_h4(prim, idx):
    cid = cid_for("H4", prim, idx)
    c = base_case(cid, prim, "H4", "b5-split-half-trace")
    yr = make_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "success")
    xr = make_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "fail-op", cand=yr["cand"])
    ev = [(k, yr["records"][k], yr["session"]) for k in EVIDENCE_ORDER]
    ev[1] = ("execution_trace", xr["records"]["execution_trace"], xr["session"])
    c.update({"cand": yr["cand"], "cred": yr["session"],
              "registry_runs": [xr, yr], "evidence": ev,
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "ops": ["failed-run trace inside successful bundle",
                      "same candidate bytes in both runs"],
              "expected_systems": {
                  "v2": {"decision": "REJECT", "level": 1},
                  "v3sig": {"decision": "ACCEPT", "supported": 6},
                  "v3full": {"decision": "REJECT", "supported": 1}},
              "expected_adj": {"supported": 1, "truth_strong": False,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h5(prim, idx):
    cid = cid_for("H5", prim, idx)
    c = base_case(cid, prim, "H5", "c2-forged-trace-signature")
    yr = make_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "success")
    xr = make_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "fail-op", cand=yr["cand"])
    ev = [(k, yr["records"][k], yr["session"]) for k in EVIDENCE_ORDER]
    ev[1] = ("execution_trace", yr["records"]["execution_trace"], xr["session"])
    c.update({"cand": yr["cand"], "cred": yr["session"],
              "registry_runs": [xr, yr], "evidence": ev,
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "ops": ["Y-shaped trace content", "signature produced by X key"],
              "expected_systems": {
                  "v2": {"decision": "EMIT", "level": 6},
                  "v3sig": {"decision": "REJECT", "supported": None},
                  "v3full": {"decision": "REJECT", "supported": None}},
              "expected_adj": {"supported": 1, "truth_strong": False,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h6a(prim, idx):
    cid = cid_for("H6a", prim, idx)
    c = base_case(cid, prim, "H6a", "c2-forged-authorship-signature")
    yr = make_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "success")
    xr = make_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "fail-op", cand=yr["cand"])
    ev = [(k, yr["records"][k], yr["session"]) for k in EVIDENCE_ORDER]
    ev[0] = ("agent_artifact", yr["records"]["agent_artifact"], xr["session"])
    c.update({"cand": yr["cand"], "cred": yr["session"],
              "registry_runs": [xr, yr], "evidence": ev,
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "ops": ["Y-shaped authorship content", "signature by X key"],
              "expected_systems": {
                  "v2": {"decision": "EMIT", "level": 6},
                  "v3sig": {"decision": "REJECT", "supported": None},
                  "v3full": {"decision": "REJECT", "supported": None}},
              "expected_adj": {"supported": 0, "truth_strong": False,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h6b(prim, idx):
    cid = cid_for("H6b", prim, idx)
    c = base_case(cid, prim, "H6b", "c1-foreign-authentic-authorship")
    yr = make_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "success")
    xr = make_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "fail-op", cand=yr["cand"])
    ev = [(k, yr["records"][k], yr["session"]) for k in EVIDENCE_ORDER]
    ev[0] = ("agent_artifact", xr["records"]["agent_artifact"], xr["session"])
    c.update({"cand": yr["cand"], "cred": yr["session"],
              "registry_runs": [xr, yr], "evidence": ev,
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "ops": ["X's authentic authorship record",
                      "session mismatch vs credited session Y"],
              "expected_systems": {
                  "v2": {"decision": "EMIT", "level": 6},
                  "v3sig": {"decision": "ACCEPT", "supported": 6},
                  "v3full": {"decision": "REJECT", "supported": 0}},
              "expected_adj": {"supported": 0, "truth_strong": False,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h9(prim, idx):
    cid = cid_for("H9", prim, idx)
    c = base_case(cid, prim, "H9", "c2-unsigned-executor-rewrite")
    yr = make_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "success")
    xr = make_run(cid, prim, "x", "cond-0", c["inst_id"], c["tid"],
                  c["inst"], "fail-op", cand=yr["cand"])
    c.update({"cand": yr["cand"], "cred": yr["session"],
              "registry_runs": [xr, yr],
              "evidence": [(k, yr["records"][k], yr["session"])
                           for k in EVIDENCE_ORDER],
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "cert_executor": "eb-executor-x",
              "ops": ["cert.execution.executor rewritten to eb-executor-x",
                      "all records authentic"],
              "expected_systems": {
                  "v2": {"decision": "EMIT", "level": 6},
                  "v3sig": {"decision": "ACCEPT", "supported": 6},
                  "v3full": {"decision": "REJECT", "supported": 1}},
              "expected_adj": {"supported": 1, "truth_strong": False,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h7(prim, k):
    cid = cid_for("H7", prim, k)
    c = base_case(cid, prim, "H7", f"honest-partial-level-{k}")
    run = make_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"],
                   c["inst"], "success")
    kinds = EVIDENCE_ORDER[:k]
    c.update({"cand": run["cand"], "cred": run["session"],
              "registry_runs": [run],
              "evidence": [(kind, run["records"][kind], run["session"])
                           for kind in kinds],
              "claims": partial_claims(k), "request_level": k,
              "ops": [f"first {k} evidence kinds only"],
              "expected_systems": {
                  "v2": {"decision": "REJECT", "level": 0},
                  "v3sig": {"decision": "ACCEPT", "supported": k},
                  "v3full": {"decision": "ACCEPT", "supported": k}},
              "expected_adj": {"supported": k, "truth_strong": False,
                               "crypto_ok": True, "malformed": False}})
    return c


def fam_h8(prim, tag):
    idx = {"a": 1, "b": 2, "c": 3, "d": 4}[tag]
    cid = cid_for("H8", prim, idx)
    names = {"a": "missing-candidate", "b": "stale-evidence-hash",
             "c": "unparseable-evidence", "d": "missing-target"}
    c = base_case(cid, prim, "H8", names[tag])
    run = make_run(cid, prim, "r", "cond-0", c["inst_id"], c["tid"],
                   c["inst"], "success")
    break_tag = {"a": "del_candidate", "b": "touch_trace",
                 "c": "corrupt_effect", "d": "del_target"}[tag]
    c.update({"cand": run["cand"], "cred": run["session"],
              "registry_runs": [run],
              "evidence": [(k, run["records"][k], run["session"])
                           for k in EVIDENCE_ORDER],
              "claims": dict(FULL_CLAIMS), "request_level": 6,
              "breaks": [break_tag],
              "ops": [names[tag]],
              "expected_systems": {
                  "v2": {"decision": "REJECT", "level": 0},
                  "v3sig": {"decision": "REJECT", "supported": None},
                  "v3full": {"decision": "REJECT", "supported": None}},
              "expected_adj": {"supported": 0, "truth_strong": False,
                               "crypto_ok": False, "malformed": True}})
    return c


FAMILIES = {"H0": fam_h0, "H1": fam_h1, "H2": fam_h2, "H3": fam_h3,
            "H4": fam_h4, "H5": fam_h5, "H6a": fam_h6a, "H6b": fam_h6b,
            "H9": fam_h9}


def build_cases():
    cases = []
    for prim in ("ecdsa", "chacha"):
        for family in ("H0", "H1", "H2", "H3", "H4", "H5", "H6a", "H6b", "H9"):
            for idx in (1, 2):
                cases.append(FAMILIES[family](prim, idx))
        for k in range(1, 6):
            cases.append(fam_h7(prim, k))
        for tag in ("a", "b", "c", "d"):
            cases.append(fam_h8(prim, tag))
    return cases


def build_all():
    for path in (ROOT / "cases" / "dev", ROOT / "private" / "dev",
                 ROOT / "labels", ROOT / "trust"):
        if path.exists():
            shutil.rmtree(path)
    ANCHOR.clear()
    labels = {}
    cases = build_cases()
    for case in cases:
        cid, entry = write_case(case)
        if cid in labels:
            raise AssertionError(f"duplicate cid {cid}")
        labels[cid] = entry
    LABELS.parent.mkdir(parents=True, exist_ok=True)
    LABELS.write_bytes(blob(labels))
    TRUST.parent.mkdir(parents=True, exist_ok=True)
    TRUST.write_bytes(blob({"schema": "eb-trust-anchor/1", "keys": ANCHOR}))
    return labels


if __name__ == "__main__":
    labels = build_all()
    fams = {}
    for cid, entry in labels.items():
        fams[entry["family"]] = fams.get(entry["family"], 0) + 1
    print(f"cases={len(labels)} families={json.dumps(fams, sort_keys=True)}")
    print(f"labels={LABELS}")
    print(f"trust={TRUST} anchors={len(ANCHOR)}")
    sys.exit(0)
