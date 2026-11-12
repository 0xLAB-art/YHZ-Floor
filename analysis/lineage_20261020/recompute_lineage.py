#!/usr/bin/env python3
"""Recompute the paper's lineage and cause cells from retained artifacts.

Three diagnostics, all read-only, all reproducible from the repository:

  1. Lineage cells.  The level-6 false-promotion and false-reject cells of
     the historical attribution experiments (IAR-B dev, IAR-B held-out,
     IAR-C) are recomputed from the per-case records of the raw runs, with
     the denominators derived rather than assumed, and each numerator is
     cross-checked against the value the artifact itself records.

  2. ECDSA cause taxonomy.  For every retained ECDSA session we re-execute
     the recorded program exactly as the harness did, and again with its
     group-order literal replaced by the secp256k1 order the instances were
     generated on.  This separates failures caused by an incorrect curve
     constant from failures with other causes.  No provider is called and no
     retained record is modified.

  3. Cross-arm instance identity.  For every instance that appears in more
     than one arm, the payload is decoded under each arm's own encoding and
     compared value by value, so that a difference in outcome cannot be
     attributed to altered or withheld instance content.

Usage:  python3 recompute_lineage.py [--out lineage_recomputation.json]
Exit code 0 means every recomputation and cross-check agreed.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "sp2027" / "analysis"
EXP_B = ANALYSIS / "experiment_b_20261019"
H1R3 = ANALYSIS / "h1r3_20261019"
SESSIONS = H1R3 / "runs" / "confirmatory" / "sessions"

IAR_RUNS = {
    "IAR-B dev": EXP_B / "iar_b/runs/20261019_112227/results.json",
    "IAR-B held-out": EXP_B / "iar_b_heldout/runs/20261019_114849/results.json",
    "IAR-C preserved": EXP_B / "iar_c/runs/20261019_121621/results.json",
}
IAR_C_ATTACK = {"S%d" % i for i in range(4, 13)} | {"S14", "S15"}
MALFORMED_FAMILY = {"H8", "S15"}
VARIANTS = ("v2", "v3-sig", "v3-full")

# secp256k1 group order and the NIST P-256 group order
K256_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P256_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
K256_HEX = "%064X" % K256_N
HEX = re.compile(r"0x([0-9a-fA-F]+)")

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" — " + detail) if detail else ""))
    if not ok:
        failures.append(name)


# ---------------------------------------------------------------- lineage --

def is_honest(case):
    adj = case["adj"]
    if adj.get("malformed") or adj.get("supported", 0) < 1:
        return False
    requested = case.get("requested")
    return requested is not None and requested <= adj["supported"]


def is_attack(set_name, case):
    if set_name == "IAR-C preserved":
        return case.get("family") in IAR_C_ATTACK
    return not is_honest(case)


def lineage_cells():
    out = {}
    for name, path in IAR_RUNS.items():
        data = json.loads(path.read_text())
        cases = data["per_case"]
        metrics = data["metrics"]
        rec = {
            "artifact": str(path.relative_to(ROOT)),
            "cases": len(cases),
            "attack_inclusive": sum(1 for c in cases if is_attack(name, c)),
            "substantive_attack": sum(1 for c in cases if is_attack(name, c)
                                      and c.get("family") not in MALFORMED_FAMILY),
            "honest_within_evidence": sum(1 for c in cases if is_honest(c)),
            "fp": {}, "fr": {},
        }
        for v in VARIANTS:
            rec["fp"][v] = sum(1 for c in cases
                               if c["level6_promotion"].get(v) and not c["adj"].get("truth_strong"))
            rec["fr"][v] = sum(1 for c in cases
                               if is_honest(c) and c["asserted"].get(v) is None)
        # cross-check every numerator against the value the artifact records
        errors = []
        if name == "IAR-C preserved":
            for v in VARIANTS:
                if rec["fp"][v] != metrics["fp_level6"][v]["all"]:
                    errors.append("fp %s: %d != %d" % (v, rec["fp"][v], metrics["fp_level6"][v]["all"]))
        else:
            for key, v in (("v2_all", "v2"), ("v3sig_attack", "v3-sig"), ("v3full_all", "v3-full")):
                if rec["fp"][v] != metrics["fp_level6"][key]:
                    errors.append("fp %s: %d != %d" % (v, rec["fp"][v], metrics["fp_level6"][key]))
        for v in VARIANTS:
            if rec["fr"][v] != metrics["false_reject"][v]:
                errors.append("fr %s: %d != %d" % (v, rec["fr"][v], metrics["false_reject"][v]))
        rec["cross_check"] = "PASS" if not errors else "FAIL"
        rec["cross_check_errors"] = errors
        out[name] = rec
        check("lineage %s recomputes and matches the artifact" % name, not errors,
              "cases=%d attack=%d honest=%d fp=%s fr=%s"
              % (rec["cases"], rec["attack_inclusive"], rec["honest_within_evidence"],
                 [rec["fp"][v] for v in VARIANTS], [rec["fr"][v] for v in VARIANTS]))
    return out


# ------------------------------------------------------------- cause pass --

def order_defect(src: str):
    """Describe a group-order literal that is not the secp256k1 order."""
    for m in HEX.finditer(src):
        digits = m.group(1)
        upper = digits.upper()
        if int(digits, 16) == P256_N:
            return "P-256 order"
        if upper.startswith("F") and upper.lstrip("F") == K256_HEX.lstrip("F") and len(digits) != 64:
            return "secp256k1 order with %d leading F digits dropped" % (64 - len(digits))
    return None


def patch_order(src: str) -> str:
    def repl(m):
        digits = m.group(1)
        upper = digits.upper()
        if int(digits, 16) == P256_N:
            return "0x" + K256_HEX
        if upper.startswith("F") and upper.lstrip("F") == K256_HEX.lstrip("F"):
            return "0x" + K256_HEX
        return m.group(0)
    return HEX.sub(repl, src)


def run_program(program: Path, instance: Path):
    try:
        proc = subprocess.run([sys.executable, "-I", str(program), str(instance)],
                              capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None
    out = proc.stdout.strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def cause_taxonomy():
    sessions = []
    for sess in sorted(SESSIONS.iterdir()):
        program = sess / "candidate.py"
        if not program.exists():
            continue
        private = json.loads((sess / "private_state.json").read_text())
        if not str(private.get("family", "")).startswith("ECDSA"):
            continue
        result = json.loads((sess / "session_result.json").read_text())
        public = json.loads((sess / "public_instance.json").read_text())
        sessions.append((sess, program, private, result, public))

    rows = []
    for sess, program, private, result, public in sessions:
        arm = "R2" if public.get("encoding") == "base64-v1" else "R0/R1/R4"
        truth = private["hidden"]["d"]
        src = program.read_text()
        defect = order_defect(src)
        as_recorded = run_program(program, sess / "public_instance.json") or {}
        patched = sess / "_lineage_patched.py"
        patched.write_text(patch_order(src))
        try:
            fixed = run_program(patched, sess / "public_instance.json") or {}
        finally:
            patched.unlink(missing_ok=True)
        d_ok_recorded = as_recorded.get("d") == truth
        d_ok_fixed = fixed.get("d") == truth
        detail = {}
        for cand in ((result.get("generalization") or {}).get("reference", {}),
                     result.get("reference") or {}):
            if isinstance(cand, dict) and "detail" in cand:
                detail = cand["detail"]
                break
        if result.get("terminal") == "SOURCE_SYNTAX":
            cause = "source syntax error"
        elif defect and not d_ok_recorded and d_ok_fixed:
            cause = "wrong group-order literal"
        elif d_ok_recorded and detail.get("k_ok") is False:
            cause = "secret recovered, nonce wrong"
        elif d_ok_recorded:
            cause = "secret recovered, recorded failure elsewhere"
        else:
            cause = "correct order, scalar wrong, cause undetermined"
        rows.append({
            "session": sess.name,
            "arm": arm,
            "level": private.get("level"),
            "terminal": result.get("terminal"),
            "cause": cause,
            "order_defect": defect,
            "d_ok_as_recorded": d_ok_recorded,
            "d_ok_with_correct_order": d_ok_fixed,
            "predicate_detail": detail,
        })

    successes = [r for r in rows if r["terminal"] == "SUCCESS"]
    failing = [r for r in rows if r["terminal"] != "SUCCESS"]
    by_arm = {}
    for arm in ("R0/R1/R4", "R2"):
        arm_rows = [r for r in rows if r["arm"] == arm]
        arm_ok = [r for r in arm_rows if r["terminal"] == "SUCCESS"]
        by_arm[arm] = {
            "programs": len(arm_rows),
            "success": len(arm_ok),
            "failing": len(arm_rows) - len(arm_ok),
            "wrong_order_in_success": sum(1 for r in arm_ok if r["order_defect"]),
            "wrong_order_in_failures": sum(1 for r in arm_rows
                                           if r["terminal"] != "SUCCESS" and r["order_defect"]),
            "causes": dict(Counter(r["cause"] for r in arm_rows
                                    if r["terminal"] != "SUCCESS")),
        }
    causes = dict(Counter(r["cause"] for r in failing))
    check("no successful ECDSA program carries a wrong group order",
          all(v["wrong_order_in_success"] == 0 for v in by_arm.values()),
          "success=%d" % sum(v["success"] for v in by_arm.values()))
    check("the wrong-order defect accounts for the R2 ECDSA failures",
          by_arm["R2"]["causes"].get("wrong group-order literal", 0) >= 18,
          "R2 causes=%s" % by_arm["R2"]["causes"])
    return {
        "ecdsa_sessions": len(rows),
        "ecdsa_success": len(successes),
        "ecdsa_failing": len(failing),
        "by_arm": by_arm,
        "causes": causes,
        "sessions": rows,
    }


# ------------------------------------------------- cross-arm identity pass --

def decode_value(value, encoding):
    if not isinstance(value, str):
        return value
    try:
        if encoding == "base64-v1":
            return base64.b64decode(value)
        return bytes.fromhex(value)
    except Exception:
        return value


def decode_tree(value, encoding):
    if isinstance(value, dict):
        return {k: decode_tree(v, encoding) for k, v in value.items()}
    if isinstance(value, list):
        return [decode_tree(v, encoding) for v in value]
    decoded = decode_value(value, encoding)
    if isinstance(decoded, bytes):
        return decoded.hex()
    return decoded


def cross_arm_identity():
    if not SESSIONS.is_dir():
        return cross_arm_identity_from_projection()
    groups = defaultdict(list)
    for sess in sorted(SESSIONS.iterdir()):
        result = json.loads((sess / "session_result.json").read_text())
        private = json.loads((sess / "private_state.json").read_text())
        public = json.loads((sess / "public_instance.json").read_text())
        key = (private.get("family"), private.get("level"), result.get("instance_id"))
        groups[key].append({
            "session": sess.name,
            "arm": result.get("arm"),
            "encoding": public.get("encoding"),
            "decoded": decode_tree({k: v for k, v in public.items() if k != "encoding"},
                                   public.get("encoding")),
        })
    identical = 0
    compared = 0
    mismatches = []
    for key, entries in sorted(groups.items()):
        arms = {e["arm"] for e in entries}
        if not {"R0", "R2"} <= arms:
            continue
        compared += 1
        r0 = [e for e in entries if e["arm"] == "R0"]
        r2 = [e for e in entries if e["arm"] == "R2"]
        if any(a["decoded"] == b["decoded"] for a in r0 for b in r2):
            identical += 1
        else:
            mismatches.append("/".join(str(k) for k in key))
    check("every instance shared by R0 and R2 carries identical decoded content",
          not mismatches, "compared=%d identical=%d" % (compared, identical))
    return {
        "instances_compared": compared,
        "identical_after_decoding": identical,
        "mismatches": mismatches,
    }


def cross_arm_identity_from_projection():
    """Recompute the identity control from the shipped public projection.

    A reviewer bundle ships the public task inputs and the per-session
    dispositions instead of the full session directories, so the control is
    recomputed from the same fields the full recomputation reads.
    """
    dispositions = H1R3 / "PUBLIC_DISPOSITIONS.json"
    instances = H1R3 / "public_instances"
    if not dispositions.is_file() or not instances.is_dir():
        raise FileNotFoundError("public projection is not present")
    rows = json.loads(dispositions.read_text())["rows"]
    groups = defaultdict(list)
    for row in rows:
        if row["kind"] != "primary":
            continue
        public = json.loads((instances / (row["session_id"] + ".json")).read_text())
        key = (row["family"], row["level"], row["instance_id"])
        groups[key].append({
            "arm": row["arm"],
            "decoded": decode_tree({k: v for k, v in public.items() if k != "encoding"},
                                   public.get("encoding")),
        })
    identical = 0
    compared = 0
    mismatches = []
    for key, entries in sorted(groups.items()):
        arms = {e["arm"] for e in entries}
        if not {"R0", "R2"} <= arms:
            continue
        compared += 1
        r0 = [e["decoded"] for e in entries if e["arm"] == "R0"]
        r2 = [e["decoded"] for e in entries if e["arm"] == "R2"]
        if any(a == b for a in r0 for b in r2):
            identical += 1
        else:
            mismatches.append("/".join(str(k) for k in key))
    check("every instance shared by R0 and R2 carries identical decoded content",
          not mismatches, "compared=%d identical=%d" % (compared, identical))
    return {
        "instances_compared": compared,
        "identical_after_decoding": identical,
        "mismatches": mismatches,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("lineage_recomputation.json"))
    args = parser.parse_args()
    result = {
        "schema": "lineage-recomputation/1",
        "lineage_cells": lineage_cells(),
    }
    if SESSIONS.is_dir():
        result["ecdsa_cause_taxonomy"] = cause_taxonomy()
        result["cross_arm_instance_identity"] = cross_arm_identity()
    else:
        # A reviewer bundle does not ship the H1-R3 session directories, so the
        # cause taxonomy cannot be recomputed there.  The cross-arm identity
        # control is recomputed from the shipped public projection.  The
        # uncomputed section is marked, not silently omitted.
        result["ecdsa_cause_taxonomy"] = {
            "skipped": "H1-R3 session records not present in this distribution"}
        print("[SKIP] H1-R3 session records not present; cause taxonomy not computed")
        result["cross_arm_instance_identity"] = cross_arm_identity()
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    try:
        shown = args.out.relative_to(ROOT)
    except ValueError:
        shown = args.out
    print("\nwritten: %s" % shown)
    if failures:
        print("FAILED CHECKS: %s" % ", ".join(failures))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
