#!/usr/bin/env python3
"""IAR-B offline evaluation runner (Experiment B).

Blind subprocess invocation of four independent systems over the frozen dev
case set:

  v2      frozen HEB-1 claim-binding validator (no signatures; contrast)
  v3-sig  authenticated records, no cross-record joins  (eb_v3_sig.py)
  v3-full authenticated records + cross-record joins     (eb_v3_full.py)
  adj     independent generator-side truth adjudicator   (eb_adjudicator.py)

The runner never reads private truth into a system; it only compares system
verdicts with the frozen labels and the adjudicator's independent verdict.

Exit 0 iff the adjudicator matches every frozen label (fixture integrity) and
all gates G-B1..G-B5 pass.
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "iar_b"
CASES = ROOT / "cases" / "dev"
PRIV = ROOT / "private" / "dev"
LABELS = ROOT / "labels" / "dev_labels.json"
TRUST = ROOT / "trust" / "dev_run_keys.json"
RUNS = ROOT / "runs"

V2 = HERE.parent / "heb1_crossboundary_20261019" / "build" / "heb1_v2_claim_binding.py"
V3SIG = HERE / "eb_v3_sig.py"
V3FULL = HERE / "eb_v3_full.py"
ADJ = HERE / "eb_adjudicator.py"

LEVELS = ["artifact_authorship", "execution_identity", "target_effect",
          "reference_oracle_acceptance", "boundary_enforcement", "attribution"]

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

FP_FAMILIES_V3SIG = {"H1", "H2", "H3", "H4", "H6b", "H9"}
FP_FAMILIES_V3FULL = {"H1", "H2", "H3", "H4"}


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
        if verdict.get("decision") == "EMIT":
            return verdict.get("level")
        return None
    if verdict.get("decision") == "ACCEPT":
        return verdict.get("supported")
    return None


def level6_promotion(system: str, verdict) -> bool:
    if not verdict:
        return False
    if system == "v2":
        return verdict.get("decision") == "EMIT" and verdict.get("level") == 6
    return verdict.get("decision") == "ACCEPT" and verdict.get("supported") == 6


def rejected(system: str, verdict) -> bool:
    if not verdict:
        return True
    if system == "v2":
        return verdict.get("decision") != "EMIT"
    return verdict.get("decision") == "REJECT"


def main() -> int:
    labels = json.loads(LABELS.read_text())
    cids = sorted(labels.keys())

    protected_before = {k: sha_file(PROTECTED_BASE / k) for k in PROTECTED}

    per_case = []
    fixture_failures = []
    label_deviations = []
    determinism_mismatches = []
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
            runs[system] = first["verdict"]

        adj = runs["adj"] or {}
        label = labels[cid]
        exp_adj = label["expected_adjudicator"]
        adj_cmp = {k: adj.get(k) for k in ("malformed", "supported", "truth_strong", "crypto_ok")}
        fixture_ok = adj_cmp == exp_adj
        if not fixture_ok:
            fixture_failures.append({"cid": cid, "expected": exp_adj, "got": adj_cmp})

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
            "requested": requested,
            "adj": adj_cmp,
            "systems": {
                s: (runs[s] or {}).get("decision") for s in ("v2", "v3-sig", "v3-full")
            },
            "asserted": {s: asserted_level(s, runs[s]) for s in ("v2", "v3-sig", "v3-full")},
            "level6_promotion": {s: level6_promotion(s, runs[s]) for s in ("v2", "v3-sig", "v3-full")},
            "fixture_ok": fixture_ok,
        })

    # ---- metrics -----------------------------------------------------------
    def fp_count(system, families=None, require_truth_false=True):
        n = 0
        for row in per_case:
            if families and row["family"] not in families:
                continue
            if require_truth_false and row["adj"]["truth_strong"] is True:
                continue
            if row["level6_promotion"][system]:
                n += 1
        return n

    def overclaim_count(system):
        n = 0
        for row in per_case:
            if row["adj"]["malformed"]:
                continue
            asserted = row["asserted"][system]
            if asserted is not None and asserted > row["adj"]["supported"]:
                n += 1
        return n

    def false_reject_count(system):
        n = 0
        for row in per_case:
            if row["adj"]["malformed"]:
                continue
            if row["adj"]["supported"] < 1:
                continue
            if row["requested"] > row["adj"]["supported"]:
                continue
            system_verdict = {"v2": None, "v3-sig": None, "v3-full": None}
            # recovered from per-case rows
            if row["family"] and row["systems"][system] in (None, "REJECT"):
                n += 1
        return n

    def agreement_count(system):
        n = 0
        for row in per_case:
            if row["asserted"][system] is not None and row["asserted"][system] == row["adj"]["supported"]:
                n += 1
        return n

    metrics = {
        "cases": len(per_case),
        "fixture_failures": len(fixture_failures),
        "label_deviations": label_deviations,
        "determinism_mismatches": determinism_mismatches,
        "fp_level6": {
            "v2_all": fp_count("v2"),
            "v3sig_attack": fp_count("v3-sig", FP_FAMILIES_V3SIG),
            "v3full_h1_h4": fp_count("v3-full", FP_FAMILIES_V3FULL),
            "v3full_all": fp_count("v3-full"),
        },
        "overclaim": {s: overclaim_count(s) for s in ("v2", "v3-sig", "v3-full")},
        "false_reject": {s: false_reject_count(s) for s in ("v2", "v3-sig", "v3-full")},
        "agreement": {s: agreement_count(s) for s in ("v2", "v3-sig", "v3-full")},
        "overhead_ms_mean": {
            s: round(sum(v) / max(1, len(v)), 2) for s, v in overhead.items()
        },
    }

    # ---- gates -------------------------------------------------------------
    by_fam = {}
    for row in per_case:
        by_fam.setdefault(row["family"], []).append(row)

    def fam_all(families, pred):
        return all(pred(r) for f in families for r in by_fam.get(f, []))

    g_b1 = fp_count("v3-full", FP_FAMILIES_V3FULL) == 0
    g_b2 = fp_count("v3-sig", FP_FAMILIES_V3SIG) > 0
    g_b3 = fam_all({"H5", "H6a"}, lambda r: r["level6_promotion"]["v2"]) and \
        fam_all({"H5", "H6a"}, lambda r: rejected("v3-sig", {"decision": r["systems"]["v3-sig"]})) and \
        fam_all({"H5", "H6a"}, lambda r: rejected("v3-full", {"decision": r["systems"]["v3-full"]}))
    g_b4 = (
        fam_all({"H0"}, lambda r: r["asserted"]["v3-sig"] == 6 and r["asserted"]["v3-full"] == 6) and
        fam_all({"H0", "H7"}, lambda r: not r["level6_promotion"]["v3-sig"] or r["adj"]["truth_strong"]) and
        fam_all({"H0", "H7"}, lambda r: not r["level6_promotion"]["v3-full"] or r["adj"]["truth_strong"]) and
        fam_all({"H7"}, lambda r: r["asserted"]["v3-sig"] == r["requested"] == r["adj"]["supported"]) and
        fam_all({"H7"}, lambda r: r["asserted"]["v3-full"] == r["requested"] == r["adj"]["supported"])
    )
    protected_after = {k: sha_file(PROTECTED_BASE / k) for k in PROTECTED}
    g_b5 = (
        not determinism_mismatches and
        protected_before == protected_after and
        all(protected_after[k] == v for k, v in PROTECTED.items())
    )

    gates = {
        "G-B1": {"pass": bool(g_b1), "detail": "v3-full level6 FP on H1-H4 == 0"},
        "G-B2": {"pass": bool(g_b2), "detail": "v3-sig level6 FP on attack families > 0"},
        "G-B3": {"pass": bool(g_b3), "detail": "H5/H6a: v2 EMIT6 while v3-sig+v3-full reject"},
        "G-B4": {"pass": bool(g_b4), "detail": "H0 accept 6; H7 accept at k; no promotion; no false rejects"},
        "G-B5": {"pass": bool(g_b5), "detail": "determinism, protected hashes, offline manifest"},
    }

    results = {
        "experiment": "IAR-B dev pass (authenticated provenance vs composition)",
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "case_set": str(CASES),
        "systems": {"v2": str(V2), "v3-sig": str(V3SIG), "v3-full": str(V3FULL), "adj": str(ADJ)},
        "trust": str(TRUST),
        "manifest": {"model_calls": 0, "provider_calls": 0, "network_calls": 0},
        "protected_before": protected_before,
        "protected_after": protected_after,
        "metrics": metrics,
        "gates": gates,
        "per_case": per_case,
        "fixture_failure_detail": fixture_failures,
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
        "fp_level6": metrics["fp_level6"],
        "overclaim": metrics["overclaim"],
        "false_reject": metrics["false_reject"],
        "agreement": metrics["agreement"],
        "overhead_ms_mean": metrics["overhead_ms_mean"],
        "gates": {k: v["pass"] for k, v in gates.items()},
        "results": str(out_path),
        "results_sha256": sha,
    }, indent=2, sort_keys=True))

    all_pass = all(v["pass"] for v in gates.values()) and not fixture_failures
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
