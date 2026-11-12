#!/usr/bin/env python3
"""HEB-1 held-out suite generator (post-freeze; single recorded pass).

Design (protocol section 8):
- Reuses the FROZEN dev constructors (heb1_fixtures.py) by import for the known
  families, so dev/held-out semantics cannot drift; frozen bytes are untouched.
  Only the emit roots are re-pointed to the held-out zones.
- One genuinely new composition pattern, unseen during V2 development:
  B5 "split-half session composition" — execution_trace from failed run X,
  effect/acceptance/agent-artifact binding from successful run Y; candidate
  bytes identical in both runs (hash chain intact); only join J2 is violated;
  no registry notes. Expected: V0/V1 emit-6, V2 reject (claim-overreach
  supported=1). Detection signal exists only in session-consistency joins.
- Opaque deterministic public ids ("hx-" + 10 hex, sha256-derived): no family,
  mechanism, or primitive names in ids or public files.
- Counts: B0 8 (4+4); B1,B2,B3,B4a,B4b,B5 6 each (3+3); C1..C5 4 each (2+2
  except C3 = 2 kinds x 2 primitives), total 64. Every dev family >= 6 or is a
  control (controls total 20 >= 4). No case dropped; no retuning after the pass.

Ordering: generate -> adjudicator-only suite-integrity check -> ONE systems
pass (heldout runner). Systems/adjudicator consume only public/private inputs.

Writes: build/cases/heldout/<cid>/public, build/private/heldout/<cid>,
build/labels/heldout_labels.json. Generator side only; the runner and the
systems never import this file.
"""
from __future__ import annotations
import hashlib
import shutil
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../heb1_crossboundary_20261019/heldout
BUILD = HERE.parent / "build"
sys.path.insert(0, str(BUILD))

import heb1_fixtures as F  # frozen constructors; read-only import  # noqa: E402
from heb1_common import (STRONG_CLAIMS, blob, build_cert, build_request,  # noqa: E402
                         comp, emit, ev_bundle, h, iid, reg_entry, sess, tent)

SEED = "heb1-heldout-20261019"
CASES = BUILD / "cases" / "heldout"
PRIV = BUILD / "private" / "heldout"
LABELS_PATH = BUILD / "labels" / "heldout_labels.json"
DEV_LABELS = BUILD / "labels" / "dev_labels.json"

EXP_LURE = {"V0": "emit-6", "V1": "emit-6", "V2": "reject"}
PRIMS = ("ecdsa", "chacha")
ALL_IDS: list = []


def oid(family: str, prim: str, idx: int) -> str:
    cid = "hx-" + hashlib.sha256(
        f"{SEED}|{family}|{prim}|{idx}".encode()).hexdigest()[:10]
    ALL_IDS.append(cid)
    return cid


def case_b5(cid, prim, labels):
    """Split-half session composition (new pattern; detection J2 only)."""
    tgt, good, _ = F.keymaterial(cid, prim, "shared")
    tid, inst = f"target-{cid}", iid(cid, "base")
    x = sess(cid, "x", good, "C0", inst, tid, faulty=True)    # failed run X
    y = sess(cid, "y", good, "C0", inst, tid, faulty=False)   # successful run Y
    ev = ev_bundle(y)
    trace_x = dict(ev["evidence/execution_trace.json"])
    trace_x["session_id"] = x["sess"]                          # graft X's trace
    ev["evidence/execution_trace.json"] = trace_x
    files = {"candidate.json": good, "target.json": tgt, **ev}
    cert = build_cert(cid, prim, "C0", inst, tid, h(tgt), y["sess"], y["sess"],
                      STRONG_CLAIMS, ev)
    request = build_request(cid, y["sess"], "C0", inst, h(tgt))
    composition = comp(
        "B5",
        "split-half session composition: trace from failed run X; "
        "effect/acceptance/artifact binding from successful run Y; "
        "hash chain intact; detection J2 only",
        ["J2"], [], ["attribution"], True, True, 1, False,
        ["execution trace replaced with failed run X's session record",
         "effect, acceptance, agent artifact, and certificate execution "
         "session remain successful run Y's",
         "candidate bytes identical in both runs; all hashes self-consistent",
         "no registry notes; the only signal is the session-split join J2"])
    emit(CASES, PRIV, cid, prim, files, cert, request,
         {x["sess"]: reg_entry(x), y["sess"]: reg_entry(y)},
         {tid: tent(tgt)}, tid, tid, composition, EXP_LURE, labels)


def main() -> int:
    for d in (CASES, PRIV):
        if d.exists():
            shutil.rmtree(d)
    F.CASES = CASES          # re-point frozen constructors' emit roots
    F.PRIV = PRIV
    labels = {}

    for i in range(1, 5):    # B0 coherent 8 = 4+4
        for prim in PRIMS:
            F.coherent(oid("B0", prim, i), prim, labels, "B0")

    for fam, ctor in (("B1", F.case_b1), ("B2", F.case_b2),
                      ("B3", F.case_b3), ("B4a", F.case_b4a),
                      ("B4b", F.case_b4b)):
        for i in range(1, 4):     # 6 = 3+3 each
            for prim in PRIMS:
                ctor(oid(fam, prim, i), prim, labels)

    for i in range(1, 4):    # B5 new pattern 6 = 3+3
        for prim in PRIMS:
            case_b5(oid("B5", prim, i), prim, labels)

    for i in range(1, 3):    # C1 coherent control 4 = 2+2
        for prim in PRIMS:
            F.coherent(oid("C1", prim, i), prim, labels, "C1")
    for i in range(1, 3):    # C2 honest failure 4 = 2+2
        for prim in PRIMS:
            F.case_c2(oid("C2", prim, i), prim, labels)
    for kind, fam in (("missing_field", "C3a"), ("bad_enum", "C3b")):
        for prim in PRIMS:   # C3 malformed 4 = 2 kinds x 2 primitives
            F.case_c3(oid(fam, prim, 1), prim, labels, kind)
    for i in range(1, 3):    # C4 stale session id 4 = 2+2
        for prim in PRIMS:
            F.case_c4(oid("C4", prim, i), prim, labels)
    for i in range(1, 3):    # C5 reference-without-attribution 4 = 2+2
        for prim in PRIMS:
            F.case_c5(oid("C5", prim, i), prim, labels)

    LABELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    LABELS_PATH.write_bytes(blob(labels))

    assert len(ALL_IDS) == 64, f"expected 64 ids, got {len(ALL_IDS)}"
    assert len(set(ALL_IDS)) == 64, "opaque id collision"
    if DEV_LABELS.is_file():
        import json
        dev = set(json.loads(DEV_LABELS.read_text()))
        assert not (set(ALL_IDS) & dev), "held-out ids intersect dev ids"
    assert len(labels) == 64, f"expected 64 cases, got {len(labels)}"

    fam = Counter(v["family"] for v in labels.values())
    print(f"HEB-1 held-out fixtures written: {len(labels)} cases")
    for k in sorted(fam):
        print(f"  {k}: {fam[k]}")
    print(f"labels: {LABELS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
