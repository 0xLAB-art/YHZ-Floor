#!/usr/bin/env python3
"""Experiment B / IAR-B — held-out case generation (post-freeze).

Verifies the frozen component bytes against `freeze/HEB_IARB_FREEZE.json`,
then re-points the frozen `eb_fixtures` machinery to an isolated held-out
root with a fresh opaque SEED, registers one dev-unseen family
(H10 reference replay), builds the held-out case set, and prints the
artifact hashes.

No frozen file is modified. Dev cases/labels/trust are untouched.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../experiment_b_20261019/heldout
BASE = HERE.parent                              # .../experiment_b_20261019
sys.path.insert(0, str(BASE))

FREEZE = BASE / "freeze" / "HEB_IARB_FREEZE.json"
FREEZE_SHA = "cc0fde9e750b84baea80fe3d9bf58f6ca88ae53370b769b74508856de59e0570"

HELDOUT_SEED = "eb-iar-b-heldout-20261019"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_freeze() -> dict:
    actual_manifest = sha256_file(FREEZE)
    if actual_manifest != FREEZE_SHA:
        raise SystemExit(
            f"FREEZE MANIFEST MISMATCH: {actual_manifest} != {FREEZE_SHA}"
        )
    man = json.loads(FREEZE.read_text())
    if man.get("schema") != "eb-iarb-freeze/1":
        raise SystemExit("freeze schema mismatch")

    def check(rel: str, expected: str) -> None:
        p = BASE / rel
        if not p.exists():
            p = BASE / Path(rel).name
        actual = sha256_file(p)
        if actual != expected:
            raise SystemExit(f"FROZEN BYTE MISMATCH: {rel} {actual} != {expected}")

    for name, digest in man.get("files", {}).items():
        check(name, digest)
    for rel, digest in man.get("labels", {}).items():
        check(rel, digest)
    for rel, digest in man.get("dev_pass_results", {}).items():
        check(rel, digest)
    print("freeze-verification: OK")
    return man


def build_cases_heldout():
    """H0–H9 + H10, then H7 levels, then H8 breaks, for both primitives."""
    cases = []
    prims = ("ecdsa", "chacha")
    families = ("H0", "H1", "H2", "H3", "H4", "H5", "H6a", "H6b", "H9", "H10")
    for prim in prims:
        for family in families:
            for idx in (1, 2):
                cases.append(F.FAMILIES[family](prim, idx))
        for k in range(1, 6):
            cases.append(F.fam_h7(prim, k))
        for tag in ("a", "b", "c", "d"):
            cases.append(F.fam_h8(prim, tag))
    return cases


def main() -> int:
    verify_freeze()
    global F
    import eb_fixtures as F  # noqa: E402  (imported after freeze verification)

    # Isolated held-out root; fresh seed; patchable globals.
    F.ROOT = BASE / "iar_b_heldout"
    F.CASES = F.ROOT / "cases" / "dev"
    F.PRIV = F.ROOT / "private" / "dev"
    F.LABELS = F.ROOT / "labels" / "heldout_labels.json"
    F.TRUST = F.ROOT / "trust" / "heldout_run_keys.json"
    F.SEED = HELDOUT_SEED

    # Dev-unseen family: H10 reference replay.
    def fam_h10(prim, idx):
        cid = F.cid_for("H10", prim, idx)
        c = F.base_case(cid, prim, "H10", "c1-foreign-authentic-reference")
        yr = F.make_run(cid, prim, "y", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
        zr = F.make_run(cid, prim, "z", "cond-0", c["inst_id"], c["tid"], c["inst"], "success")
        ev = [(k, yr["records"][k], yr["session"]) for k in F.EVIDENCE_ORDER]
        ev[3] = ("reference_acceptance", zr["records"]["reference_acceptance"], zr["session"])
        c.update({
            "cand": yr["cand"],
            "cred": yr["session"],
            "registry_runs": [zr, yr],
            "evidence": ev,
            "claims": dict(F.FULL_CLAIMS),
            "request_level": 6,
            "ops": [
                "reference_acceptance from another authentic successful run Z",
                "same target/condition; distinct candidate bytes per role",
            ],
            "expected_systems": {
                "v2": {"decision": "REJECT", "level": 3},
                "v3sig": {"decision": "ACCEPT", "supported": 6},
                "v3full": {"decision": "REJECT", "supported": 3},
            },
            "expected_adj": {
                "supported": 3,
                "truth_strong": False,
                "crypto_ok": True,
                "malformed": False,
            },
        })
        return c

    F.FAMILIES["H10"] = fam_h10
    F.build_cases = build_cases_heldout

    if F.ROOT.exists():
        shutil.rmtree(F.ROOT)

    labels = F.build_all()

    fam_counts: dict[str, int] = {}
    for entry in labels.values():
        fam_counts[entry["family"]] = fam_counts.get(entry["family"], 0) + 1

    expected_families = {
        "H0": 4, "H1": 4, "H2": 4, "H3": 4, "H4": 4, "H5": 4,
        "H6a": 4, "H6b": 4, "H9": 4, "H10": 4, "H7": 10, "H8": 8,
    }
    ok = fam_counts == expected_families
    print(json.dumps({
        "cases": len(labels),
        "families": dict(sorted(fam_counts.items())),
        "expected_families_ok": ok,
        "seed": F.SEED,
        "labels": str(F.LABELS),
        "labels_sha256": sha256_file(F.LABELS),
        "trust": str(F.TRUST),
        "trust_sha256": sha256_file(F.TRUST),
    }, indent=2, sort_keys=True))
    if len(labels) != 58 or not ok:
        raise SystemExit("held-out build count mismatch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
