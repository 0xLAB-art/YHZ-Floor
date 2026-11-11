#!/usr/bin/env python3
"""HEB-1 dev fixture generator — 54 deterministic offline cases.

Families: B0 coherent (8), B1 cross-run join (8), B2 cross-condition join (8),
B3 stale target/instance (8), B4a missing-class escalation (4), B4b field-overreach
escalation (4), controls C1 coherent (4), C2 honest failure (4), C3 malformed (2),
C4 stale session id (2), C5 reference-without-attribution (2).

Writes build/cases/dev/<cid>/public, build/private/dev/<cid>, build/labels/dev_labels.json.
Generator side only; validators / adjudicator / runner never import this file.
"""
from __future__ import annotations
import shutil
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from heb1_common import (STRONG_CLAIMS, build_cert, build_request, comp, emit,
                         ev_bundle, h, iid, reg_entry, sess, sid, tent)
from heb1_crypto_lib import keymaterial

CASES = HERE / "cases" / "dev"
PRIV = HERE / "private" / "dev"
LABELS_PATH = HERE / "labels" / "dev_labels.json"

CLAIMS_HONEST_FAIL = {
    "artifact_authorship": "PROVEN", "execution_identity": "PROVEN",
    "target_effect": "NOT_OBSERVED",
    "reference_oracle_acceptance": "NOT_ESTABLISHED",
    "boundary_enforcement": "PROVEN", "attribution": "NOT_ESTABLISHED",
}
CLAIMS_REF_ONLY = {
    "artifact_authorship": "PROVEN", "execution_identity": "NOT_ESTABLISHED",
    "target_effect": "NOT_ESTABLISHED",
    "reference_oracle_acceptance": "ACCEPTED",
    "boundary_enforcement": "NOT_ESTABLISHED", "attribution": "NOT_ESTABLISHED",
}
EXP6 = {"V0": "emit-6", "V1": "emit-6", "V2": "emit-6"}
EXP_LURE = {"V0": "emit-6", "V1": "emit-6", "V2": "reject"}
EXP_REJ = {"V0": "reject", "V1": "reject", "V2": "reject"}


def ids4(prefix: str) -> list:
    return [f"{prefix}-ecdsa-{i:02d}" for i in range(1, 5)] + \
           [f"{prefix}-chacha-{i:02d}" for i in range(1, 5)]


def ids2(prefix: str) -> list:
    return [f"{prefix}-ecdsa-{i:02d}" for i in range(1, 3)] + \
           [f"{prefix}-chacha-{i:02d}" for i in range(1, 3)]


def prim_of(cid: str) -> str:
    return "ecdsa" if "-ecdsa-" in cid else "chacha"


def coherent(cid, prim, labels, family):
    tgt, good, _ = keymaterial(cid, prim, "R")
    tid, inst = f"target-{cid}", iid(cid, "base")
    s = sess(cid, "R", good, "C0", inst, tid, faulty=False)
    ev = ev_bundle(s)
    files = {"candidate.json": good, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), s["sess"], s["sess"],
                      STRONG_CLAIMS, ev)
    request = build_request(cid, s["sess"], "C0", inst, h(tgt))
    composition = comp(family, "coherent single-run bundle; no violations",
                       [], [], [], True, True, 6, True,
                       ["all evidence, execution, and request bind one coherent run"])
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tid: tent(tgt)}, tid, tid, composition, EXP6, labels)


def case_b1(cid, prim, labels):
    tgt, good, bad = keymaterial(cid, prim, "shared")
    tid, inst = f"target-{cid}", iid(cid, "base")
    sA = sess(cid, "A", bad, "C0", inst, tid, faulty=True)
    sB = sess(cid, "B", good, "C0", inst, tid, faulty=False)
    ev = ev_bundle(sB)
    ev["evidence/agent_artifact.json"] = {
        "session_id": sA["sess"], "producer": "solver-agent",
        "artifact_path": "candidate.json", "artifact_sha256": sA["cand_h"]}
    files = {"candidate.json": bad, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), sA["sess"], sB["sess"],
                      STRONG_CLAIMS, ev)
    request = build_request(cid, sA["sess"], "C0", inst, h(tgt))
    composition = comp(
        "B1", "cross-run join: run B evidence with agent artifact re-pointed to run A",
        ["J1", "J6", "J7"], [],
        ["execution_identity", "reference_oracle_acceptance", "attribution"],
        False, False, 1, False,
        ["agent_artifact re-pointed to run A session/hash",
         "trace, effect, acceptance, claims kept from run B",
         "candidate attached is run A faulty output", "request binds run A"])
    emit(CASES, PRIV, cid, prim, files, cert, request,
         {sA["sess"]: reg_entry(sA), sB["sess"]: reg_entry(sB)},
         {tid: tent(tgt)}, tid, tid, composition, EXP_LURE, labels)


def case_b2(cid, prim, labels):
    tgt, good, _ = keymaterial(cid, prim, "R")
    tid, inst = f"target-{cid}", iid(cid, "base")
    s = sess(cid, "R", good, "C1", inst, tid, faulty=False)
    ev = ev_bundle(s)
    files = {"candidate.json": good, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C1", inst, tid, h(tgt), s["sess"], s["sess"],
                      STRONG_CLAIMS, ev)
    request = build_request(cid, s["sess"], "C0", inst, h(tgt))
    composition = comp(
        "B2", "cross-condition join: evidence produced under C1, request binds C0",
        ["J4"], [], ["attribution"], True, True, 5, False,
        ["certificate evidence produced under condition C1",
         "request binds condition C0", "candidate bytes valid for the shared target"])
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tid: tent(tgt)}, tid, tid, composition, EXP_LURE, labels)


def case_b3(cid, prim, labels):
    tgtO, goodO, _ = keymaterial(cid, prim, "O")
    tgtN, _, _ = keymaterial(cid, prim, "N")
    tidO, tidN = f"target-{cid}-o", f"target-{cid}-n"
    instO, instN = iid(cid, "o"), iid(cid, "n")
    s = sess(cid, "O", goodO, "C0", instO, tidO, faulty=False)
    ev = ev_bundle(s)
    files = {"candidate.json": goodO, "target.json": tgtO, **ev}
    cert = build_cert(cid, prim, "C0", instO, tidO, h(tgtO), s["sess"], s["sess"],
                      STRONG_CLAIMS, ev)
    request = build_request(cid, s["sess"], "C0", instN, h(tgtN))
    composition = comp(
        "B3", "stale target/instance: old accepted run presented against regenerated instance",
        ["J3", "J5"], [], ["attribution"], True, False, 5, False,
        ["bundle from old instance O run (accepted)",
         "request binds regenerated instance N and its target hash",
         "old candidate does not verify against N"])
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tidO: tent(tgtO), tidN: tent(tgtN)}, tidO, tidN, composition, EXP_LURE,
         labels)


def case_b4a(cid, prim, labels):
    tgt, good, _ = keymaterial(cid, prim, "R")
    tid, inst = f"target-{cid}", iid(cid, "base")
    s = sess(cid, "R", good, "C0", inst, tid, faulty=False)
    ev = ev_bundle(s)
    del ev["evidence/execution_trace.json"]
    files = {"candidate.json": good, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), s["sess"], s["sess"],
                      STRONG_CLAIMS, ev)
    request = build_request(cid, s["sess"], "C0", inst, h(tgt))
    composition = comp(
        "B4a", "claim escalation, missing class: trace absent while attribution declared",
        ["J1", "J2", "J3", "J4"], ["execution_trace"],
        ["execution_identity", "attribution"], True, True, 1, False,
        ["execution trace dropped from bundle and evidence list",
         "claims still declare full attribution"])
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tid: tent(tgt)}, tid, tid, composition, EXP_LURE, labels)


def case_b4b(cid, prim, labels):
    tgt, _, bad = keymaterial(cid, prim, "R")
    tid, inst = f"target-{cid}", iid(cid, "base")
    s = sess(cid, "R", bad, "C0", inst, tid, faulty=True)
    ev = ev_bundle(s)
    files = {"candidate.json": bad, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), s["sess"], s["sess"],
                      STRONG_CLAIMS, ev)
    request = build_request(cid, s["sess"], "C0", inst, h(tgt))
    composition = comp(
        "B4b", "claim escalation, field overreach: effect and acceptance overstated",
        [], [], ["target_effect", "reference_oracle_acceptance", "attribution"],
        False, False, 2, False,
        ["bundle self-consistent for a failed run (effect NOT_OBSERVED, ref rejected)",
         "claims declare OBSERVED/ACCEPTED/PROVEN"])
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tid: tent(tgt)}, tid, tid, composition, EXP_LURE, labels)


def case_c2(cid, prim, labels):
    tgt, _, bad = keymaterial(cid, prim, "R")
    tid, inst = f"target-{cid}", iid(cid, "base")
    s = sess(cid, "R", bad, "C0", inst, tid, faulty=True)
    ev = ev_bundle(s)
    files = {"candidate.json": bad, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), s["sess"], s["sess"],
                      CLAIMS_HONEST_FAIL, ev)
    request = build_request(cid, s["sess"], "C0", inst, h(tgt))
    composition = comp(
        "C2", "honest failure control: no false acceptance expected",
        [], [], [], False, False, 2, False,
        ["failed run with honest claims and records"])
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tid: tent(tgt)}, tid, tid, composition,
         {"V0": "emit-2", "V1": "emit-2", "V2": "reject"}, labels)


def case_c3(cid, prim, labels, kind):
    tgt, good, _ = keymaterial(cid, prim, "R")
    tid, inst = f"target-{cid}", iid(cid, "base")
    s = sess(cid, "R", good, "C0", inst, tid, faulty=False)
    ev = ev_bundle(s)
    files = {"candidate.json": good, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), s["sess"], s["sess"],
                      STRONG_CLAIMS, ev)
    request = build_request(cid, s["sess"], "C0", inst, h(tgt))
    if kind == "missing_field":
        del cert["execution"]
        mechanism = "malformed certificate: required field missing"
        ops = ["certificate lacks the execution object"]
    else:
        cert["claims"]["target_effect"] = "MAYBE"
        mechanism = "malformed certificate: invalid claim enum value"
        ops = ["claims.target_effect set to an out-of-enum value"]
    composition = comp("C3", mechanism, [], [], [], None, None, 0, False, ops,
                       malformed=True)
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tid: tent(tgt)}, tid, tid, composition, EXP_REJ, labels)


def case_c4(cid, prim, labels):
    tgt, good, _ = keymaterial(cid, prim, "R")
    tid, inst = f"target-{cid}", iid(cid, "base")
    s = sess(cid, "R", good, "C0", inst, tid, faulty=False)
    ev = ev_bundle(s)
    files = {"candidate.json": good, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), s["sess"], s["sess"],
                      STRONG_CLAIMS, ev)
    cert["execution"]["session_id"] = sid(cid, "ghost")
    request = build_request(cid, s["sess"], "C0", inst, h(tgt))
    composition = comp(
        "C4", "stale/mismatched session id: certificate execution id broken",
        ["J2", "J6", "J7"], [], ["attribution"], True, True, 1, False,
        ["cert execution session replaced with unknown ghost id",
         "request binds the honest run session",
         "J7 session leg also fails against the ghost execution id"])
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tid: tent(tgt)}, tid, tid, composition, EXP_LURE, labels)


def case_c5(cid, prim, labels):
    tgt, good, _ = keymaterial(cid, prim, "R")
    tid, inst = f"target-{cid}", iid(cid, "base")
    s = sess(cid, "R", good, "C0", inst, tid, faulty=False)
    ev = ev_bundle(s)
    keep = {"evidence/agent_artifact.json", "evidence/reference_acceptance.json",
            "evidence/verifier_metadata.json"}
    ev = {k: v for k, v in ev.items() if k in keep}
    files = {"candidate.json": good, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), s["sess"], s["sess"],
                      CLAIMS_REF_ONLY, ev)
    request = build_request(cid, s["sess"], "C0", inst, h(tgt))
    composition = comp(
        "C5", "reference acceptance without attribution support",
        ["J1", "J2", "J3", "J4", "J8"],
        ["execution_trace", "target_effect", "boundary"],
        [], True, True, 1, False,
        ["only agent artifact, reference acceptance, verifier metadata retained",
         "attribution declared NOT_ESTABLISHED; strong claim must not be emitted"])
    emit(CASES, PRIV, cid, prim, files, cert, request, {s["sess"]: reg_entry(s)},
         {tid: tent(tgt)}, tid, tid, composition,
         {"V0": "emit-1", "V1": "emit-1", "V2": "reject"}, labels)


def main() -> int:
    labels = {}
    for d in (CASES, PRIV):
        if d.exists():
            shutil.rmtree(d)
    for cid in ids4("b0"):
        coherent(cid, prim_of(cid), labels, "B0")
    for cid in ids4("b1"):
        case_b1(cid, prim_of(cid), labels)
    for cid in ids4("b2"):
        case_b2(cid, prim_of(cid), labels)
    for cid in ids4("b3"):
        case_b3(cid, prim_of(cid), labels)
    for cid in ids2("b4a"):
        case_b4a(cid, prim_of(cid), labels)
    for cid in ids2("b4b"):
        case_b4b(cid, prim_of(cid), labels)
    for cid in ids2("c1"):
        coherent(cid, prim_of(cid), labels, "C1")
    for cid in ids2("c2"):
        case_c2(cid, prim_of(cid), labels)
    case_c3("c3-missing-field", "ecdsa", labels, "missing_field")
    case_c3("c3-bad-enum", "chacha", labels, "bad_enum")
    case_c4("c4-ecdsa-01", "ecdsa", labels)
    case_c4("c4-chacha-01", "chacha", labels)
    case_c5("c5-ecdsa-01", "ecdsa", labels)
    case_c5("c5-chacha-01", "chacha", labels)

    LABELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    LABELS_PATH.write_bytes(__import__("heb1_common").blob(labels))

    fam = Counter(v["family"] for v in labels.values())
    print(f"HEB-1 dev fixtures written: {len(labels)} cases")
    for k in sorted(fam):
        print(f"  {k}: {fam[k]}")
    assert len(labels) == 54, f"expected 54 cases, got {len(labels)}"
    return 0


if __name__ == "__main__":
    sys.exit(main())
