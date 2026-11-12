#!/usr/bin/env python3
"""HEB-1 held-out evaluation runner (single recorded pass).

Procedure (protocol section 8):
1. Verify frozen component bytes against both freeze manifests BEFORE running;
   abort on any mismatch (the pass must use frozen bytes only).
2. Run the three frozen systems and the frozen adjudicator as subprocesses on
   every held-out case (blind: systems receive only each case's public dir;
   the adjudicator additionally receives run_registry.json + targets.json).
3. Metrics mirror the frozen dev runner, with the defect set extended by the
   new held-out pattern B5 (split-half session composition).
4. Gates N3: mechanism = max(FP(V0), FP(V1)) >= 0.5; mitigation = FP(V2) <=
   0.15 on the held-out defect suites.
5. Safeguards: protected-hash check before/after; label-isolation flip test on
   two held-out ids; static audit; forbidden-field audit and private-path
   audit over every public input file.
6. Write heldout/heldout_results.json. One pass only; no retuning; all
   outcomes preserved, no case dropped.

Usage: python3 heldout/heb1_heldout_runner.py
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent            # .../heb1_crossboundary_20261019/heldout
ROOT = HERE.parent
REPO = HERE.parents[3]
BUILD = ROOT / "build"
CASES = BUILD / "cases" / "heldout"
PRIV = BUILD / "private" / "heldout"
LABELS = BUILD / "labels" / "heldout_labels.json"
OUT = HERE / "heldout_results.json"
FREEZE = ROOT / "freeze"
SYSTEMS = ["heb1_v0_schema_reference.py", "heb1_v1_hash_integrity.py",
           "heb1_v2_claim_binding.py"]
ADJ = "heb1_adjudicator.py"
ATTACK_FAMILIES = ["B1", "B2", "B3", "B4a", "B4b", "B5"]
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
FORBIDDEN_TOKENS = ["raw_verdict", "reference_verdict", "validator_verdict",
                    "expected_reference_verdict", "hidden_secret", "defect_label"]
PRIVATE_TOKENS = ["private", "labels"]


def sha_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_frozen() -> dict:
    checks = {}
    for tag in ("validator", "config"):
        man = FREEZE / f"HEB1_{tag.upper()}_FREEZE.json"
        m = json.loads(man.read_text())
        for rel, exp in m["files"].items():
            p = ROOT / rel
            got = sha_of(p) if p.is_file() else None
            checks[rel] = {"expected": exp, "got": got, "ok": got == exp}
    return checks


def run_script(script: str, args: list) -> dict:
    t0 = time.perf_counter()
    try:
        proc = subprocess.run([sys.executable, str(BUILD / script), *args],
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


def input_audits(case_ids: list) -> dict:
    forbidden = {}
    private_hits = {}
    for cid in case_ids:
        for f in sorted((CASES / cid / "public").rglob("*")):
            if not f.is_file():
                continue
            text = f.read_text(errors="replace")
            rel = str(f.relative_to(ROOT))
            for tok in FORBIDDEN_TOKENS:
                if tok in text:
                    forbidden.setdefault(rel, []).append(tok)
            for tok in PRIVATE_TOKENS:
                if tok in text:
                    private_hits.setdefault(rel, []).append(tok)
    return {"forbidden_field_hits": forbidden,
            "private_path_hits": private_hits,
            "clean": not forbidden and not private_hits}


def main() -> int:
    frozen = verify_frozen()
    frozen_ok = all(v["ok"] for v in frozen.values())
    if not frozen_ok:
        bad = [k for k, v in frozen.items() if not v["ok"]]
        print(f"ABORT: frozen-byte mismatch in {bad}; no pass performed")
        return 2

    prot_before = protected_hashes()
    labels_all = json.loads(LABELS.read_text())
    case_ids = sorted(d.name for d in CASES.iterdir() if d.is_dir())
    assert set(case_ids) == set(labels_all), "case/label id mismatch"

    results = {}
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

    # ---- metrics (mirror frozen dev runner; defect set extended by B5) ----
    def attack_stats(sysname: str):
        by_fam = {}
        n_fp = d = 0
        for cid, rec in results.items():
            fam = rec["family"]
            s = stem_decision(rec["systems"][sysname])
            fp = (s["decision"] == "EMIT" and s["level"] == 6
                  and not rec["adjudicator"].get("truth_strong"))
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
        ms_list = [r["systems"][sysname].get("ms", 0) for r in results.values()]
        b0_total = sum(1 for r in results.values() if r["family"] == "B0")
        c1_total = sum(1 for r in results.values() if r["family"] == "C1")
        metrics["systems"][sysname] = {
            "attack_fp": {"n": n_fp, "d": d,
                          "rate": round(n_fp / d, 4) if d else None,
                          "by_family": {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_fam.items())}},
            "any_positive_gt_truth": anypos,
            "true_accept_b0": f"{ta_b0}/{b0_total}",
            "true_accept_c1": f"{ta_c1}/{c1_total}",
            "false_rejects": fr,
            "errors": errors,
            "stated_vs_adjudicated_level_agreement": f"{agree}/{tot}" if tot else None,
            "mean_ms": round(sum(ms_list) / len(ms_list), 2),
        }

    v0r = metrics["systems"]["V0"]["attack_fp"]["rate"]
    v1r = metrics["systems"]["V1"]["attack_fp"]["rate"]
    v2r = metrics["systems"]["V2"]["attack_fp"]["rate"]
    n3_mech = max(v0r or 0, v1r or 0) >= 0.5
    n3_mit = (v2r if v2r is not None else 1) <= 0.15
    gates = {
        "N3_heldout_mechanism_exhibited": {
            "pass": n3_mech, "max_fp_v0_v1": max(v0r or 0, v1r or 0),
            "threshold": 0.5},
        "N3_heldout_mitigation_valid": {
            "pass": n3_mit, "v2_fp_rate": v2r, "threshold": 0.15,
            "v2_true_accept_b0": metrics["systems"]["V2"]["true_accept_b0"],
            "v2_true_accept_c1": metrics["systems"]["V2"]["true_accept_c1"]},
    }

    # ---- label isolation test (two held-out ids) ----
    b0_ids = sorted(c for c, v in labels_all.items() if v["family"] == "B0")
    b1_ids = sorted(c for c, v in labels_all.items() if v["family"] == "B1")
    flip_cases = [b0_ids[0], b1_ids[0]]
    original = LABELS.read_text()
    before = {cid: {"systems": {k: stem_decision(results[cid]["systems"][k])
                                for k in ["V0", "V1", "V2"]},
                    "adj": {k: v for k, v in results[cid]["adjudicator"].items() if k != "ms"}}
              for cid in flip_cases}
    isolation = {"flipped": flip_cases, "identical": None, "labels_file_restored": None}
    try:
        flipped = json.loads(original)
        flipped[flip_cases[0]]["family"] = "B4b"
        flipped[flip_cases[1]]["family"] = "C1"
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

    # ---- static audit + input audits ----
    audit = {}
    for script in SYSTEMS + [ADJ]:
        src = (BUILD / script).read_text()
        audit[script] = {
            "labels_refs": src.count("dev_labels") + src.count("heldout_labels"),
            "composition_refs": src.count("composition")}
    audits = input_audits(case_ids)

    prot_after = protected_hashes()
    manifest = {"model_calls": 0, "provider_calls": 0, "network": "none",
                "systems": SYSTEMS, "adjudicator": ADJ,
                "case_count": len(case_ids), "labels_count": len(labels_all),
                "attack_families": ATTACK_FAMILIES}
    provenance = {
        "frozen_verification": frozen,
        "freeze_manifests_sha256": {
            "validator": sha_of(FREEZE / "HEB1_VALIDATOR_FREEZE.json"),
            "config": sha_of(FREEZE / "HEB1_CONFIG_FREEZE.json")},
        "component_sha256": {
            rel: sha_of(ROOT / rel) for rel in
            [f"build/{s}" for s in SYSTEMS] + [
                f"build/{ADJ}", "build/heb1_certificate_schema.json",
                "build/heb1_common.py", "build/heb1_crypto_lib.py",
                "build/heb1_fixtures.py",
                "heldout/heb1_heldout_gen.py",
                "build/labels/heldout_labels.json"]},
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    supplementary = {
        "fixture_validation_failures": metrics["fixture_validation_failures"],
        "v2_true_accept_b0": metrics["systems"]["V2"]["true_accept_b0"],
        "v2_true_accept_c1": metrics["systems"]["V2"]["true_accept_c1"],
        "label_isolation_identical": isolation["identical"],
        "protected_ok": all(v["ok"] for v in prot_after.values()),
        "input_audits_clean": audits["clean"],
        "frozen_bytes_ok": frozen_ok,
    }
    payload = {
        "timestamp": ts,
        "operator_notes": [
            "single recorded held-out evaluation pass; no retuning; all outcomes preserved",
            "adjudicator-only suite-integrity check was performed pre-pass; systems were not invoked before this pass",
            "frozen component bytes verified against both freeze manifests immediately before the pass",
        ],
        "manifest": manifest, "metrics": metrics, "gates": gates,
        "supplementary_checks": supplementary,
        "label_isolation": isolation, "static_audit": audit,
        "input_audits": audits,
        "protected_before": prot_before, "protected_after": prot_after,
        "provenance": provenance,
        "cases": results,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(f"heldout cases={len(case_ids)} "
          f"fixture_validation_failures={metrics['fixture_validation_failures']}")
    for s in ["V0", "V1", "V2"]:
        m = metrics["systems"][s]
        print(f"{s}: attack_fp={m['attack_fp']['n']}/{m['attack_fp']['d']} "
              f"by_family={m['attack_fp']['by_family']} "
              f"B0={m['true_accept_b0']} C1={m['true_accept_c1']} "
              f"anypos={m['any_positive_gt_truth']} errors={m['errors']} "
              f"stated_agreement={m['stated_vs_adjudicated_level_agreement']}")
    print(f"gates: N3_mech={'PASS' if n3_mech else 'FAIL'} "
          f"N3_mit={'PASS' if n3_mit else 'FAIL'}")
    print(f"isolation_identical={isolation['identical']} "
          f"protected_ok={supplementary['protected_ok']} "
          f"audits_clean={audits['clean']} frozen_ok={frozen_ok}")
    print(f"results: {OUT}")
    return 0 if (n3_mech and n3_mit
                 and not metrics["fixture_validation_failures"]
                 and isolation["identical"] and isolation["labels_file_restored"]
                 and supplementary["protected_ok"] and audits["clean"]) else 1


if __name__ == "__main__":
    sys.exit(main())
