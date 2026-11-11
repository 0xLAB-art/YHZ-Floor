#!/usr/bin/env python3
"""IAR-C offline evaluation runner (Experiment B, IAR-C).

Blind subprocess invocation of four systems over the independently generated
IAR-C case set (iar_c/eb_independent_gen.py output):

  v2       frozen HEB-1 claim-binding validator      (joins, no signatures)
  v3-sig   authenticated records, no cross-record joins (../eb_v3_sig.py)
  v3-full  authenticated records + cross-record joins    (../eb_v3_full.py)
  adj      IAR-C independent truth adjudicator (iar_c/eb_independent_adj.py)

The runner passes only public inputs (plus the trust anchor) to the systems and
only compares their verdicts with the generator labels and the independent
adjudicator's truth verdict. It never feeds private truth into a system.

Gates (truth-based, fixed in iar_c/freeze/IAR_C_FREEZE.json before the
preserved pass):
  G-C1  fixture integrity: adjudicator == generator labels on all cases
  G-C2  offline integrity: determinism, protected hashes, zero external calls
  G-C3  v3-full level-6 false promotions on attack families == 0
  G-C4  single-mechanism insufficiency: v2 and v3-sig both have level-6
        false promotions on attack families > 0
  G-C5  honest acceptance: v3-full false rejects == 0, overclaim == 0, and
        full agreement on every case whose request is within evidence

Usage: python3 eb_independent_runner.py
Exit 0 iff no fixture failures and all gates pass.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CASES = DATA / "cases"
PRIV = DATA / "private"
LABELS = DATA / "labels" / "iar_c_labels.json"
TRUST = DATA / "trust" / "iar_c_run_keys.json"
RUNS = HERE / "runs"
FREEZE = HERE / "freeze" / "IAR_C_FREEZE.json"

BASE = HERE.parent
V2 = BASE.parent / "heb1_crossboundary_20261019" / "build" / "heb1_v2_claim_binding.py"
V3SIG = BASE / "eb_v3_sig.py"
V3FULL = BASE / "eb_v3_full.py"
ADJ = HERE / "eb_independent_adj.py"

LEVELS = ["artifact_authorship", "execution_identity", "target_effect",
          "reference_oracle_acceptance", "boundary_enforcement", "attribution"]

HONEST = {"S1", "S2", "S3", "S13"}
ATTACK = {"S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S14", "S15"}

PROTECTED = {
    "sp2027/analysis/RESULTS_LOCK.json":
        "4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39",
    "sp2027/analysis/RESULTS_LOCK_H1PC.json":
        "8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103",
    "sp2027/paper/main.tex":
        "51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461",
    "sp2027/paper/main.pdf":
        "fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a",
}
PROTECTED_BASE = Path("/mnt/nvme5/ACTS-Attack")


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def invoke(cmd):
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    ms = (time.perf_counter() - t0) * 1000.0
    verdict = None
    for line in reversed(proc.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                verdict = json.loads(line)
            except json.JSONDecodeError:
                verdict = None
            break
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "verdict": verdict,
        "stderr_tail": proc.stderr[-200:] if proc.stderr else "",
        "ms": round(ms, 2),
    }


def asserted_level(system: str, verdict):
    if not verdict:
        return None
    if system == "v2":
        return verdict.get("level") if verdict.get("decision") == "EMIT" else None
    return verdict.get("supported") if verdict.get("decision") == "ACCEPT" else None


def level6_promotion(system: str, verdict) -> bool:
    if not verdict:
        return False
    if system == "v2":
        return verdict.get("decision") == "EMIT" and verdict.get("level") == 6
    return verdict.get("decision") == "ACCEPT" and verdict.get("supported") == 6


def main() -> int:
    labels = json.loads(LABELS.read_text())
    cids = sorted(labels)
    assert CASES.exists() and cids, "no cases found"

    protected_before = {k: sha_file(PROTECTED_BASE / k) for k in PROTECTED}

    frozen_check = None
    if FREEZE.exists():
        freeze = json.loads(FREEZE.read_text())
        frozen_check = {}
        components = {
            "eb_independent_gen.py": HERE / "eb_independent_gen.py",
            "eb_independent_adj.py": ADJ,
            "iab_runner": HERE / "eb_independent_runner.py",
            "eb_v3_sig.py": V3SIG,
            "eb_v3_full.py": V3FULL,
            "heb1_v2_claim_binding.py": V2,
            "labels": LABELS,
            "trust": TRUST,
        }
        declared = freeze.get("component_sha256", {})
        for name, path in components.items():
            if name not in declared:
                continue
            frozen_check[name] = {
                "declared": declared[name],
                "actual": sha_file(path),
                "match": sha_file(path) == declared[name],
            }

    per_case = []
    fixture_failures = []
    label_deviations = []
    determinism_mismatches = []
    system_failures = []
    overhead = {s: [] for s in ("v2", "v3-sig", "v3-full", "adj")}

    for cid in cids:
        pub = CASES / cid / "public"
        priv = PRIV / cid
        req = json.loads((pub / "request.json").read_text())
        requested = LEVELS.index(req["claimed"]["claim_level"]) + 1

        runs = {}
        for system, cmd in (
            ("v2", [sys.executable, str(V2), str(pub)]),
            ("v3-sig", [sys.executable, str(V3SIG), str(pub), str(TRUST)]),
            ("v3-full", [sys.executable, str(V3FULL), str(pub), str(TRUST)]),
            ("adj", [sys.executable, str(ADJ), str(pub), str(priv), str(TRUST)]),
        ):
            first = invoke(cmd)
            second = invoke(cmd)
            overhead[system].append(first["ms"])
            if first["verdict"] != second["verdict"]:
                determinism_mismatches.append({"cid": cid, "system": system})
            if first["verdict"] is None:
                system_failures.append({
                    "cid": cid, "system": system,
                    "returncode": first["returncode"], "stderr": first["stderr_tail"],
                })
            runs[system] = first["verdict"]

        adj = runs["adj"] or {}
        label = labels[cid]
        adj_cmp = {k: adj.get(k) for k in ("crypto_ok", "malformed", "supported", "truth_strong")}
        fixture_ok = adj_cmp == label["expected_adjudicator"]
        if not fixture_ok:
            fixture_failures.append({"cid": cid, "expected": label["expected_adjudicator"], "got": adj_cmp})

        for system in ("v2", "v3-sig", "v3-full"):
            exp = label["expected_systems"][{"v2": "v2", "v3-sig": "v3sig", "v3-full": "v3full"}[system]]
            got = runs[system] or {}
            if system == "v2":
                gv = {"decision": got.get("decision"), "level": got.get("level")}
            else:
                gv = {"decision": got.get("decision"), "supported": got.get("supported")}
            if gv != exp:
                label_deviations.append({"cid": cid, "system": system, "expected": exp, "got": gv})

        per_case.append({
            "cid": cid,
            "family": label["family"],
            "primitive": label["primitive"],
            "mechanism": label["mechanism"],
            "requested": requested,
            "adj": adj_cmp,
            "systems": {s: (runs[s] or {}).get("decision") for s in ("v2", "v3-sig", "v3-full")},
            "system_levels": {
                "v2": (runs["v2"] or {}).get("level"),
                "v3-sig": (runs["v3-sig"] or {}).get("supported"),
                "v3-full": (runs["v3-full"] or {}).get("supported"),
            },
            "asserted": {s: asserted_level(s, runs[s]) for s in ("v2", "v3-sig", "v3-full")},
            "level6_promotion": {s: level6_promotion(s, runs[s]) for s in ("v2", "v3-sig", "v3-full")},
            "fixture_ok": fixture_ok,
        })

    # ---- metrics -----------------------------------------------------------
    def fp_count(system, families=None):
        return sum(
            1 for row in per_case
            if row["adj"]["truth_strong"] is False
            and (families is None or row["family"] in families)
            and row["level6_promotion"][system]
        )

    def fp_by_family(system):
        out = {}
        for row in per_case:
            if row["adj"]["truth_strong"] is False and row["level6_promotion"][system]:
                out[row["family"]] = out.get(row["family"], 0) + 1
        return dict(sorted(out.items()))

    def overclaim_count(system):
        return sum(
            1 for row in per_case
            if not row["adj"]["malformed"]
            and row["asserted"][system] is not None
            and row["asserted"][system] > row["adj"]["supported"]
        )

    def honest_within_evidence(row):
        return (
            not row["adj"]["malformed"]
            and row["adj"]["supported"] >= 1
            and row["requested"] <= row["adj"]["supported"]
        )

    def false_reject_count(system):
        n = 0
        for row in per_case:
            if not honest_within_evidence(row):
                continue
            if row["asserted"][system] != row["adj"]["supported"]:
                n += 1
        return n

    def agreement_count(system):
        return sum(
            1 for row in per_case
            if row["asserted"][system] is not None
            and row["asserted"][system] == row["adj"]["supported"]
        )

    honest_within = [r for r in per_case if honest_within_evidence(r)]

    metrics = {
        "cases": len(per_case),
        "honest_within_evidence_cases": len(honest_within),
        "fixture_failures": len(fixture_failures),
        "label_deviations": len(label_deviations),
        "determinism_mismatches": len(determinism_mismatches),
        "system_failures": len(system_failures),
        "fp_level6": {
            s: {"all": fp_count(s), "attack": fp_count(s, ATTACK), "by_family": fp_by_family(s)}
            for s in ("v2", "v3-sig", "v3-full")
        },
        "overclaim": {s: overclaim_count(s) for s in ("v2", "v3-sig", "v3-full")},
        "false_reject": {s: false_reject_count(s) for s in ("v2", "v3-sig", "v3-full")},
        "agreement": {s: agreement_count(s) for s in ("v2", "v3-sig", "v3-full")},
        "honest_accept_full": {
            s: sum(
                1 for r in honest_within
                if r["asserted"][s] == r["adj"]["supported"] and r["adj"]["supported"] >= 1
            )
            for s in ("v2", "v3-sig", "v3-full")
        },
        "overhead_ms_mean": {
            s: round(sum(v) / max(1, len(v)), 2) for s, v in overhead.items()
        },
    }

    # ---- gates -------------------------------------------------------------
    def all_cases_have_family(families, pred):
        return all(pred(r) for f in families for r in per_case if r["family"] == f)

    g_c1 = not fixture_failures
    g_c2 = (
        not determinism_mismatches
        and not system_failures
        and (frozen_check is None or all(v["match"] for v in frozen_check.values()))
    )
    g_c3 = fp_count("v3-full", ATTACK) == 0
    g_c4 = fp_count("v3-sig", ATTACK) > 0 and fp_count("v2", ATTACK) > 0
    g_c5 = (
        false_reject_count("v3-full") == 0
        and overclaim_count("v3-full") == 0
        and all(
            r["asserted"]["v3-full"] == r["adj"]["supported"] for r in honest_within
        )
    )
    protected_after = {k: sha_file(PROTECTED_BASE / k) for k in PROTECTED}
    g_c2 = g_c2 and protected_before == protected_after and \
        all(protected_after[k] == v for k, v in PROTECTED.items())

    gates = {
        "G-C1": {"pass": bool(g_c1), "detail": "independent adjudicator == generator labels on all cases"},
        "G-C2": {"pass": bool(g_c2), "detail": "determinism, frozen components, protected hashes, offline"},
        "G-C3": {"pass": bool(g_c3), "detail": "v3-full level-6 false promotions on attack families == 0"},
        "G-C4": {"pass": bool(g_c4), "detail": "v2 > 0 and v3-sig > 0 level-6 false promotions on attack families"},
        "G-C5": {"pass": bool(g_c5), "detail": "v3-full: 0 false rejects, 0 overclaim, full agreement within evidence"},
    }

    results = {
        "experiment": "IAR-C independent adversarial replication (preserved pass)",
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "case_set": str(CASES),
        "systems": {"v2": str(V2), "v3-sig": str(V3SIG), "v3-full": str(V3FULL), "adj": str(ADJ)},
        "trust": str(TRUST),
        "labels": str(LABELS),
        "labels_sha256": sha_file(LABELS),
        "trust_sha256": sha_file(TRUST),
        "manifest": {"model_calls": 0, "provider_calls": 0, "network_calls": 0},
        "frozen_component_check": frozen_check,
        "protected_before": protected_before,
        "protected_after": protected_after,
        "metrics": metrics,
        "gates": gates,
        "label_deviations": label_deviations,
        "per_case": per_case,
        "fixture_failure_detail": fixture_failures,
        "system_failure_detail": system_failures,
    }

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir = RUNS / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "results.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    sha = sha_file(out_path)

    print(json.dumps({
        "cases": len(per_case),
        "fixture_failures": len(fixture_failures),
        "label_deviations": len(label_deviations),
        "determinism_mismatches": len(determinism_mismatches),
        "system_failures": len(system_failures),
        "fp_level6": {
            s: {"all": metrics["fp_level6"][s]["all"], "attack": metrics["fp_level6"][s]["attack"]}
            for s in ("v2", "v3-sig", "v3-full")
        },
        "overclaim": metrics["overclaim"],
        "false_reject": metrics["false_reject"],
        "agreement": metrics["agreement"],
        "honest_accept_full": metrics["honest_accept_full"],
        "gates": {k: v["pass"] for k, v in gates.items()},
        "results": str(out_path),
        "results_sha256": sha,
    }, indent=2, sort_keys=True))

    return 0 if all(v["pass"] for v in gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
