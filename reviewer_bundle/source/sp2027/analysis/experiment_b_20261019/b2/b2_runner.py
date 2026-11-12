#!/usr/bin/env python3
"""B2 offline comparison runner.

Evaluates six content-addressed / execution-bound provenance model verifiers
(b2_prov_baselines.py) plus the frozen reference systems (v2, v3-sig, v3-full)
and the independent adjudicator over two frozen case sets:

  dev      54 frozen IAR-B development cases
  heldout  58 frozen IAR-B held-out cases

The B2 baselines are design-class models implemented offline from public
descriptions (content-addressed provenance in the in-toto/SLSA style; explicit
execution/session binding in the RATS style), not actual products.  The runner
never reads private truth into a system; only the adjudicator receives the
private directory.

One preserved pass: verifies the B2 freeze before executing, runs every system
twice per case (determinism), records pre-registered predictions vs observed
false promotions, and writes b2/runs/<ts>/results.json.

Exit 0 iff the adjudicator matches every frozen label (fixture integrity), the
freeze verifies, and gates B2-G1..B2-G5 pass.
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent

V2 = BASE.parent / "heb1_crossboundary_20261019" / "build" / "heb1_v2_claim_binding.py"
V3SIG = BASE / "eb_v3_sig.py"
V3FULL = BASE / "eb_v3_full.py"
ADJ = BASE / "eb_adjudicator.py"
B2CLI = HERE / "b2_prov_baselines.py"

FREEZE = HERE / "freeze" / "B2_FREEZE.json"
RUNS = HERE / "runs"

CONFIGS = ("digest-only", "digest-session", "abl-authjoin", "abl-refjoin",
           "abl-tracejoin", "abl-executor")
REFERENCE = ("v2", "v3-sig", "v3-full")
ALL_SYSTEMS = REFERENCE + CONFIGS
OVERHEAD_SYSTEMS = ALL_SYSTEMS + ("adj",)

SETS = (
    {
        "name": "dev",
        "cases": BASE / "iar_b" / "cases" / "dev",
        "private": BASE / "iar_b" / "private" / "dev",
        "labels": BASE / "iar_b" / "labels" / "dev_labels.json",
        "trust": BASE / "iar_b" / "trust" / "dev_run_keys.json",
    },
    {
        "name": "heldout",
        "cases": BASE / "iar_b_heldout" / "cases" / "dev",
        "private": BASE / "iar_b_heldout" / "private" / "dev",
        "labels": BASE / "iar_b_heldout" / "labels" / "heldout_labels.json",
        "trust": BASE / "iar_b_heldout" / "trust" / "heldout_run_keys.json",
    },
)

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


def verify_freeze():
    """Verify the pre-run freeze: module hashes, labels/trust hashes, counts."""
    if not FREEZE.exists():
        return None, {"ok": False, "problems": ["missing-freeze"], "freeze": str(FREEZE)}
    fz = json.loads(FREEZE.read_text())
    problems = []
    module_hashes = {}
    for name, expected in sorted(fz.get("modules", {}).items()):
        p = HERE / name
        got = sha_file(p) if p.exists() else None
        module_hashes[name] = got
        if got != expected:
            problems.append("module-hash:" + name)
    for s in SETS:
        entry = fz.get("sets", {}).get(s["name"], {})
        for key, path in (("labels_sha256", s["labels"]),
                          ("trust_sha256", s["trust"])):
            if not path.exists():
                problems.append(key + ":" + s["name"] + ":missing")
                continue
            if sha_file(path) != entry.get(key):
                problems.append(key + ":" + s["name"])
        if s["labels"].exists() and entry.get("cases") is not None:
            if len(json.loads(s["labels"].read_text())) != entry["cases"]:
                problems.append("case-count:" + s["name"])
    return fz, {
        "ok": not problems,
        "freeze": str(FREEZE),
        "freeze_sha256": sha_file(FREEZE),
        "module_hashes": module_hashes,
        "problems": problems,
    }


def run_set(setdef, predictions):
    labels = json.loads(setdef["labels"].read_text())
    cids = sorted(labels)
    trust = setdef["trust"]
    cases = setdef["cases"]
    private = setdef["private"]

    per_case = []
    fixture_failures = []
    reference_deviations = []
    determinism_mismatches = []
    wellformed_problems = []
    overhead = {s: [] for s in OVERHEAD_SYSTEMS}

    for cid in cids:
        pub = cases / cid / "public"
        priv = private / cid
        req = json.loads((pub / "request.json").read_text())
        requested = LEVELS.index(req["claimed"]["claim_level"]) + 1

        commands = [
            ("v2", [sys.executable, str(V2), str(pub)]),
            ("v3-sig", [sys.executable, str(V3SIG), str(pub), str(trust)]),
            ("v3-full", [sys.executable, str(V3FULL), str(pub), str(trust)]),
            ("adj", [sys.executable, str(ADJ), str(pub), str(priv), str(trust)]),
        ]
        commands += [(cfg, [sys.executable, str(B2CLI), cfg, str(pub), str(trust)])
                     for cfg in CONFIGS]

        runs = {}
        for system, cmd in commands:
            first = invoke(cmd)
            second = invoke(cmd)
            overhead[system].append(first["ms"])
            if first["verdict"] != second["verdict"]:
                determinism_mismatches.append({"cid": cid, "system": system})
            verdict = first["verdict"]
            runs[system] = verdict

            if system in CONFIGS:
                if not isinstance(verdict, dict):
                    wellformed_problems.append(
                        {"cid": cid, "system": system, "problem": "unparseable-verdict"})
                    continue
                if verdict.get("system") != system:
                    wellformed_problems.append(
                        {"cid": cid, "system": system,
                         "problem": "system-field:" + str(verdict.get("system"))})
                if verdict.get("decision") not in ("ACCEPT", "REJECT"):
                    wellformed_problems.append(
                        {"cid": cid, "system": system,
                         "problem": "decision:" + str(verdict.get("decision"))})
                sup = verdict.get("supported")
                if sup is not None and not (isinstance(sup, int) and 0 <= sup <= 6):
                    wellformed_problems.append(
                        {"cid": cid, "system": system, "problem": "supported:" + str(sup)})
                rq = verdict.get("requested")
                if rq is not None and not (isinstance(rq, int) and 1 <= rq <= 6):
                    wellformed_problems.append(
                        {"cid": cid, "system": system, "problem": "requested:" + str(rq)})

        adj = runs["adj"] or {}
        label = labels[cid]
        exp_adj = label["expected_adjudicator"]
        adj_cmp = {k: adj.get(k) for k in
                   ("malformed", "supported", "truth_strong", "crypto_ok")}
        fixture_ok = adj_cmp == exp_adj
        if not fixture_ok:
            fixture_failures.append({"cid": cid, "expected": exp_adj, "got": adj_cmp})

        for system in REFERENCE:
            key = {"v2": "v2", "v3-sig": "v3sig", "v3-full": "v3full"}[system]
            exp = label["expected_systems"][key]
            got = runs[system] or {}
            if system == "v2":
                gv = {"decision": got.get("decision"), "level": got.get("level")}
            else:
                gv = {"decision": got.get("decision"), "supported": got.get("supported")}
            if gv != exp:
                reference_deviations.append(
                    {"cid": cid, "system": system, "expected": exp, "got": gv})

        per_case.append({
            "cid": cid,
            "family": label["family"],
            "primitive": label["primitive"],
            "requested": requested,
            "adj": adj_cmp,
            "decisions": {s: (runs[s] or {}).get("decision") for s in ALL_SYSTEMS},
            "raw_levels": {
                s: ((runs[s] or {}).get("level") if s == "v2"
                    else (runs[s] or {}).get("supported"))
                for s in ALL_SYSTEMS
            },
            "asserted": {s: asserted_level(s, runs[s]) for s in ALL_SYSTEMS},
            "level6_promotion": {s: level6_promotion(s, runs[s]) for s in ALL_SYSTEMS},
            "verdicts": {s: runs[s] for s in ALL_SYSTEMS},
            "fixture_ok": fixture_ok,
        })

    # ---- metrics -----------------------------------------------------------
    def fp_count(system):
        return sum(
            1 for row in per_case
            if row["level6_promotion"][system] and row["adj"]["truth_strong"] is not True
        )

    def fp_families(system):
        return sorted({
            row["family"] for row in per_case
            if row["level6_promotion"][system] and row["adj"]["truth_strong"] is not True
        })

    def overclaim_count(system):
        return sum(
            1 for row in per_case
            if not row["adj"]["malformed"]
            and row["asserted"][system] is not None
            and row["asserted"][system] > row["adj"]["supported"]
        )

    def false_reject_count(system, families=None):
        n = 0
        for row in per_case:
            if families and row["family"] not in families:
                continue
            if row["adj"]["malformed"]:
                continue
            if row["adj"]["supported"] < 1:
                continue
            if row["requested"] > row["adj"]["supported"]:
                continue
            if row["decisions"][system] in (None, "REJECT"):
                n += 1
        return n

    def agreement_count(system):
        return sum(
            1 for row in per_case
            if row["asserted"][system] is not None
            and row["asserted"][system] == row["adj"]["supported"]
        )

    metrics = {
        "cases": len(per_case),
        "fixture_failures": len(fixture_failures),
        "reference_deviations": reference_deviations,
        "determinism_mismatches": determinism_mismatches,
        "wellformed_problems": wellformed_problems,
        "fp_level6": {s: fp_count(s) for s in ALL_SYSTEMS},
        "fp_families": {s: fp_families(s) for s in ALL_SYSTEMS},
        "overclaim": {s: overclaim_count(s) for s in ALL_SYSTEMS},
        "false_reject": {s: false_reject_count(s) for s in ALL_SYSTEMS},
        "agreement": {s: agreement_count(s) for s in ALL_SYSTEMS},
        "overhead_ms_mean": {
            s: round(sum(v) / max(1, len(v)), 2) for s, v in overhead.items()
        },
    }

    # ---- pre-registered predictions vs observed ---------------------------
    pred_vs_obs = {}
    for cfg in CONFIGS:
        pred = sorted(predictions.get(cfg, []))
        obs = fp_families(cfg)
        pred_vs_obs[cfg] = {
            "predicted_fp_families": pred,
            "observed_fp_families": obs,
            "match": pred == obs,
        }

    # ---- gates -------------------------------------------------------------
    malformed_rows = [r for r in per_case if r["adj"]["malformed"]]
    g1 = len(fixture_failures) == 0 and all(
        r["decisions"][cfg] == "REJECT" for r in malformed_rows for cfg in CONFIGS
    )

    g2 = not determinism_mismatches and not wellformed_problems

    g3 = True
    for cfg in ("digest-only", "digest-session"):
        h0 = [r for r in per_case if r["family"] == "H0"]
        h7 = [r for r in per_case if r["family"] == "H7"]
        if not h0 or not h7:
            g3 = False
            continue
        if not all(r["decisions"][cfg] == "ACCEPT" and r["asserted"][cfg] == 6
                   for r in h0):
            g3 = False
        if not all(r["asserted"][cfg] == r["requested"] == r["adj"]["supported"]
                   for r in h7):
            g3 = False
        if false_reject_count(cfg, {"H0", "H7"}) != 0:
            g3 = False

    g4 = all(v["match"] for v in pred_vs_obs.values())

    gates = {
        "B2-G1": {"pass": bool(g1),
                  "detail": "fixture integrity; all new baselines reject malformed cases"},
        "B2-G2": {"pass": bool(g2),
                  "detail": "double-run determinism; well-formed verdicts"},
        "B2-G3": {"pass": bool(g3),
                  "detail": "H0 accepted at 6; H7(k) accepted at k; no false rejects"},
        "B2-G4": {"pass": bool(g4),
                  "detail": "observed false-promotion families match pre-registered predictions"},
    }

    return {
        "name": setdef["name"],
        "paths": {
            "cases": str(cases),
            "private": str(private),
            "labels": str(setdef["labels"]),
            "trust": str(trust),
            "labels_sha256": sha_file(setdef["labels"]),
            "trust_sha256": sha_file(trust),
        },
        "metrics": metrics,
        "predicted_vs_observed": pred_vs_obs,
        "gates": gates,
        "per_case": per_case,
        "fixture_failure_detail": fixture_failures,
    }


def main() -> int:
    fz, freeze_info = verify_freeze()
    if not freeze_info.get("ok"):
        print(json.dumps({"error": "freeze verification failed", "freeze": freeze_info},
                         indent=2, sort_keys=True))
        return 2

    protected_before = {k: sha_file(PROTECTED_BASE / k) for k in PROTECTED}

    set_results = []
    for setdef in SETS:
        predictions = fz["predictions"][setdef["name"]]
        set_results.append(run_set(setdef, predictions))

    protected_after = {k: sha_file(PROTECTED_BASE / k) for k in PROTECTED}
    g5 = (
        freeze_info.get("ok") is True
        and protected_before == protected_after
        and all(protected_after[k] == v for k, v in PROTECTED.items())
    )

    all_gates = {}
    for sr in set_results:
        for gate, info in sr["gates"].items():
            all_gates[gate + "@" + sr["name"]] = info["pass"]
    all_gates["B2-G5"] = bool(g5)

    results = {
        "experiment": "B2 content-addressed vs execution-bound provenance comparison",
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "freeze": freeze_info,
        "systems": {
            "v2": str(V2), "v3-sig": str(V3SIG), "v3-full": str(V3FULL),
            "adj": str(ADJ), "b2-baselines": str(B2CLI),
        },
        "manifest": {"model_calls": 0, "provider_calls": 0, "network_calls": 0},
        "protected_before": protected_before,
        "protected_after": protected_after,
        "sets": set_results,
        "all_gates": all_gates,
    }

    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir = RUNS / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "results.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    sha = sha_file(out_path)

    summary = {
        "sets": {}
    }
    for sr in set_results:
        m = sr["metrics"]
        summary["sets"][sr["name"]] = {
            "cases": m["cases"],
            "fixture_failures": m["fixture_failures"],
            "reference_deviations": len(m["reference_deviations"]),
            "determinism_mismatches": len(m["determinism_mismatches"]),
            "wellformed_problems": len(m["wellformed_problems"]),
            "fp_level6": m["fp_level6"],
            "fp_families": m["fp_families"],
            "overclaim": m["overclaim"],
            "false_reject": m["false_reject"],
            "agreement": m["agreement"],
            "overhead_ms_mean": m["overhead_ms_mean"],
            "predicted_vs_observed": sr["predicted_vs_observed"],
        }
    summary["all_gates"] = all_gates
    summary["results"] = str(out_path)
    summary["results_sha256"] = sha
    print(json.dumps(summary, indent=2, sort_keys=True))

    return 0 if all(all_gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
