#!/usr/bin/env python3
"""HEB-1 dev runner: orchestrate systems + adjudicator, validate fixtures,
compute metrics and gates, verify protected hashes and label isolation.

Offline: no network, no model/provider calls. Blind discipline: the three
systems receive ONLY each case's public directory; the adjudicator receives
public + private (run_registry.json, targets.json); nothing reads the labels
file except the label-isolation test, which only proves non-dependence.

Usage: python3 heb1_runner.py
Writes build/runs/dev_run_<timestamp>/results.json and prints a summary.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES = HERE / "cases" / "dev"
PRIV = HERE / "private" / "dev"
LABELS = HERE / "labels" / "dev_labels.json"
RUNS = HERE / "runs"
SYSTEMS = ["heb1_v0_schema_reference.py", "heb1_v1_hash_integrity.py",
           "heb1_v2_claim_binding.py"]
ADJ = "heb1_adjudicator.py"
ATTACK_FAMILIES = ["B1", "B2", "B3", "B4a", "B4b"]
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


def sha_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_script(script: str, args: list) -> dict:
    t0 = time.perf_counter()
    try:
        proc = subprocess.run([sys.executable, str(HERE / script), *args],
                              capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "ms": 120000.0}
    ms = (time.perf_counter() - t0) * 1000.0
    lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    if proc.returncode != 0 or not lines:
        return {"error": f"exit={proc.returncode}",
                "stderr": (proc.stderr or "")[-300:], "ms": ms}
    try:
        obj = json.loads(lines[-1])
    except Exception as e:
        return {"error": f"bad-json:{type(e).__name__}", "ms": ms}
    obj["ms"] = round(ms, 2)
    return obj


def protected_hashes() -> dict:
    out = {}
    for rel, expect in PROTECTED.items():
        p = REPO / rel
        got = sha_of(p) if p.is_file() else None
        out[rel] = {"sha256": got, "expected": expect, "ok": got == expect}
    return out


def validate_case(adj: dict, comp: dict) -> list:
    diffs = []
    intd = comp.get("intended", {})
    for key in ["joins_failed", "missing_kinds", "claim_mismatches"]:
        if sorted(adj.get(key) or []) != sorted(intd.get(key) or []):
            diffs.append(f"{key}: got {adj.get(key)} expected {intd.get(key)}")
    for key in ["level", "truth_strong", "malformed"]:
        if adj.get(key) != intd.get(key):
            diffs.append(f"{key}: got {adj.get(key)} expected {intd.get(key)}")
    if not adj.get("malformed") and not intd.get("malformed"):
        for key in ["crypto_cert", "crypto_requested"]:
            got = (adj.get(key) or {}).get("ok")
            if got != intd.get(key):
                diffs.append(f"{key}: got {got} expected {intd.get(key)}")
    return diffs


def stem_decision(rec: dict) -> dict:
    if "error" in rec:
        return {"decision": "ERROR", "level": None, "reason": rec["error"]}
    return {"decision": rec.get("decision"), "level": rec.get("level"),
            "reason": rec.get("reason", "")}


def main() -> int:
    prot_before = protected_hashes()
    results = {}
    case_ids = sorted(d.name for d in CASES.iterdir() if d.is_dir())
    labels_all = json.loads(LABELS.read_text())
    for cid in case_ids:
        pub = CASES / cid / "public"
        priv = PRIV / cid
        rec = {"family": labels_all[cid]["family"],
               "primitive": labels_all[cid]["primitive"],
               "systems": {}}
        for script in SYSTEMS:
            name = script.split("_")[1].upper()
            rec["systems"][name] = run_script(script, [str(pub)])
        adj = run_script(ADJ, [str(pub), str(priv)])
        rec["adjudicator"] = adj
        comp = json.loads((priv / "composition.json").read_text())
        rec["fixture_validation"] = validate_case(adj, comp)
        results[cid] = rec

    # ---- metrics ----
    def attack_stats(sysname: str):
        by_fam = {}
        n_fp = d = 0
        for cid, rec in results.items():
            fam = rec["family"]
            s = stem_decision(rec["systems"][sysname])
            fp = s["decision"] == "EMIT" and s["level"] == 6 and not rec["adjudicator"].get("truth_strong")
            if fam in ATTACK_FAMILIES:
                d += 1
                if fp:
                    n_fp += 1
                by_fam.setdefault(fam, [0, 0])
                by_fam[fam][1] += 1
                if fp:
                    by_fam[fam][0] += 1
        return n_fp, d, by_fam

    metrics = {"systems": {}, "fixture_validation_failures": 0}
    for cid, rec in results.items():
        if rec["fixture_validation"]:
            metrics["fixture_validation_failures"] += 1
    for sysname in ["V0", "V1", "V2"]:
        n_fp, d, by_fam = attack_stats(sysname)
        ta_b0 = ta_c1 = fr = anypos = errors = 0
        for cid, rec in results.items():
            s = stem_decision(rec["systems"][sysname])
            truth = rec["adjudicator"]
            if s["decision"] == "ERROR":
                errors += 1
                continue
            strong = s["decision"] == "EMIT" and s["level"] == 6
            if rec["family"] == "B0" and strong and truth.get("truth_strong"):
                ta_b0 += 1
            if rec["family"] == "C1" and strong and truth.get("truth_strong"):
                ta_c1 += 1
            if truth.get("truth_strong") and not strong:
                fr += 1
            lvl = s["level"] if isinstance(s["level"], int) else 0
            if lvl > (truth.get("level") or 0):
                anypos += 1
        agree = tot = 0
        if sysname == "V2":
            for cid, rec in results.items():
                s = rec["systems"][sysname]
                m = re.search(r"supported=(\d+)", s.get("reason", ""))
                if m:
                    tot += 1
                    if int(m.group(1)) == (rec["adjudicator"].get("level") or -1):
                        agree += 1
        n_err_ms = [r["systems"][sysname].get("ms", 0) for r in results.values()]
        metrics["systems"][sysname] = {
            "attack_fp": {"n": n_fp, "d": d,
                          "rate": round(n_fp / d, 4) if d else None,
                          "by_family": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_fam.items())}},
            "any_positive_gt_truth": anypos,
            "true_accept_b0": f"{ta_b0}/8",
            "true_accept_c1": f"{ta_c1}/4",
            "false_rejects": fr,
            "errors": errors,
            "stated_vs_adjudicated_level_agreement": f"{agree}/{tot}" if tot else None,
            "mean_ms": round(sum(n_err_ms) / len(n_err_ms), 2),
        }
    v0r = metrics["systems"]["V0"]["attack_fp"]["rate"]
    v1r = metrics["systems"]["V1"]["attack_fp"]["rate"]
    v2r = metrics["systems"]["V2"]["attack_fp"]["rate"]
    n1 = max(v0r if v0r is not None else 0, v1r if v1r is not None else 0) >= 0.5
    n2 = ((v2r if v2r is not None else 1) <= 0.10
          and metrics["systems"]["V2"]["true_accept_b0"] == "8/8"
          and metrics["systems"]["V2"]["true_accept_c1"] == "4/4")
    gates = {
        "N1_mechanism_exhibited": {
            "pass": n1,
            "max_fp_v0_v1": max(v0r or 0, v1r or 0),
            "threshold": 0.5},
        "N2_mitigation_valid": {
            "pass": n2,
            "v2_fp_rate": v2r,
            "threshold": 0.10,
            "v2_true_accept_b0": metrics["systems"]["V2"]["true_accept_b0"],
            "v2_true_accept_c1": metrics["systems"]["V2"]["true_accept_c1"]},
    }

    # ---- label isolation test ----
    original = LABELS.read_text()
    flip_cases = ["b1-ecdsa-01", "c1-chacha-01"]
    before = {cid: {"systems": {k: stem_decision(results[cid]["systems"][k]) for k in ["V0", "V1", "V2"]},
                    "adj": {k: v for k, v in results[cid]["adjudicator"].items() if k != "ms"}} for cid in flip_cases}
    isolation = {"flipped": flip_cases, "identical": None, "post_label_includes": None}
    try:
        flipped = json.loads(original)
        flipped["b1-ecdsa-01"]["family"] = "B0"
        flipped["c1-chacha-01"]["family"] = "B2"
        LABELS.write_text(json.dumps(flipped, indent=2, sort_keys=True) + "\n")
        isol_ok = True
        for cid in flip_cases:
            pub = CASES / cid / "public"
            priv = PRIV / cid
            for script in SYSTEMS:
                name = script.split("_")[1].upper()
                got = stem_decision(run_script(script, [str(pub)]))
                if got != before[cid]["systems"][name]:
                    isol_ok = False
            adj_got = run_script(ADJ, [str(pub), str(priv)])
            if {k: v for k, v in adj_got.items() if k != "ms"} != before[cid]["adj"]:
                isol_ok = False
        isolation["identical"] = isol_ok
    finally:
        LABELS.write_text(original)
    isolation["labels_file_restored"] = LABELS.read_text() == original

    # ---- static audit ----
    audit = {}
    for script in SYSTEMS + [ADJ]:
        src = (HERE / script).read_text()
        audit[script] = {"dev_labels_refs": src.count("dev_labels"),
                         "composition_refs": src.count("composition")}

    prot_after = protected_hashes()
    manifest = {"model_calls": 0, "provider_calls": 0, "network": "none",
                "systems": SYSTEMS, "adjudicator": ADJ,
                "case_count": len(case_ids), "labels_count": len(labels_all)}
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = RUNS / f"dev_run_{ts}"
    outdir.mkdir(parents=True, exist_ok=True)
    payload = {"timestamp": ts, "manifest": manifest, "metrics": metrics,
               "gates": gates, "label_isolation": isolation, "static_audit": audit,
               "protected_before": prot_before, "protected_after": prot_after,
               "cases": results}
    (outdir / "results.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(f"cases={len(case_ids)} fixture_validation_failures={metrics['fixture_validation_failures']}")
    for s in ["V0", "V1", "V2"]:
        m = metrics["systems"][s]
        print(f"{s}: attack_fp={m['attack_fp']['n']}/{m['attack_fp']['d']} "
              f"B0={m['true_accept_b0']} C1={m['true_accept_c1']} "
              f"anypos={m['any_positive_gt_truth']} errors={m['errors']} "
              f"stated_agreement={m['stated_vs_adjudicated_level_agreement']}")
    print(f"gates: N1={'PASS' if n1 else 'FAIL'} N2={'PASS' if n2 else 'FAIL'}")
    print(f"label_isolation_identical={isolation['identical']} "
          f"protected_ok={all(v['ok'] for v in prot_after.values())}")
    print(f"results: {outdir / 'results.json'}")
    return 0 if (n1 and n2 and not metrics['fixture_validation_failures']
                 and isolation['identical']) else 1


if __name__ == "__main__":
    sys.exit(main())
