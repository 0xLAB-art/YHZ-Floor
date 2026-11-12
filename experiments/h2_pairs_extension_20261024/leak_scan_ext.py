#!/usr/bin/env python3
"""LEAK_SCAN for H2-CBC-PAIRS-EXT-20261024-v1.

Rule (PREREGISTRATION.md §9, mirroring the frozen cohort): no truth/key/prefix
material in prompts, raw provider responses, events, model-written programs,
or oracle usage files; truth hex in accepted programs' execution stdout is
expected (the program's own recovered output), per-seed counts must equal the
accepted-session counts. Runs after the sessions; non-model-visible forensic
captures are scanned separately from the model-visible set.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE  # the scan target is this namespace
sys.path.insert(0, str(NS.parent / "h2_cbc_agency_20261023" / "preflight"))
from fixture_cbc import instance  # noqa: E402

SEEDS = (65, 66, 67, 68, 69, 70, 71, 72, 73, 74)
SESS = NS / "sessions"

MODEL_VISIBLE_SUBSTRINGS = ("/sessions/prompts/", "/sessions/raw_provider_responses/",
                            "/sessions/events.jsonl")
MODEL_VISIBLE_PROGRAM = "/execution_captures/"  # agent.py files are model-written
FORENSIC = ("stdout.txt", "oracle_usage.json")


def classify(path_str):
    p = path_str.replace("\\", "/")
    if any(s in p for s in MODEL_VISIBLE_SUBSTRINGS):
        return "model_visible"
    if "/execution_captures/" in p and p.endswith("agent.py"):
        return "model_visible_program"
    if "/execution_captures/" in p and (".stdout.txt" in p or "oracle_usage" in p):
        return "forensic_stdout_or_usage"
    return "forensic_other"


def main():
    all_files = [p for p in SESS.rglob("*") if p.is_file()]
    scan = {str(p.relative_to(NS)): p.read_text(errors="replace") for p in all_files}
    violations = []
    per_seed = {}
    for seed in SEEDS:
        _pub, secret = instance(seed)
        needles = {
            "key": secret["key"].hex(), "iv": secret["iv"].hex(),
            "prefix": secret["prefix"].hex(), "truth": secret["plaintext"].hex(),
        }
        key_hits, prefix_hits, truth_model_visible, truth_stdout_expected = [], [], [], []
        for rel, text in scan.items():
            if needles["key"] in text:
                key_hits.append(rel)
            if needles["prefix"] in text:
                prefix_hits.append(rel)
            if needles["truth"] in text:
                kind = classify(rel)
                if kind in ("model_visible", "model_visible_program"):
                    truth_model_visible.append(rel)
                elif kind == "forensic_stdout_or_usage":
                    truth_stdout_expected.append(rel)
                else:
                    violations.append(f"truth hex in unexpected forensic file: {rel}")
        clean = not key_hits and not prefix_hits and not truth_model_visible
        per_seed[str(seed)] = {
            "clean": clean,
            "key_hex_anywhere_in_sessions": key_hits,
            "prefix_hex_anywhere_in_sessions": prefix_hits,
            "truth_hex_in_model_visible": truth_model_visible,
            "truth_hex_in_execution_stdout_expected": sorted(truth_stdout_expected),
        }
        if not clean:
            violations.append(f"seed {seed}: secret material outside expected locations")
    rows = [json.loads(l) for l in (NS / "results.jsonl").read_text().splitlines() if l.strip()]
    accepted_counts = {}
    for seed in SEEDS:
        accepted_counts[str(seed)] = sum(
            1 for r in rows if r["seed"] == seed and r["accepted"])
    stdout_counts_ok = all(
        len(per_seed[str(s)]["truth_hex_in_execution_stdout_expected"]) == accepted_counts[str(s)]
        for s in SEEDS)
    out = {
        "protocol": "H2-CBC-PAIRS-EXT-20261024-v1",
        "files_scanned": len(all_files),
        "per_seed": per_seed,
        "per_seed_accepted_sessions": accepted_counts,
        "stdout_truth_counts_match_accepted_sessions": stdout_counts_ok,
        "violations": violations,
        "rule": ("no truth/key/iv/prefix material in prompts, raw provider responses, events, "
                 "model-written programs, or oracle usage files; truth hex in accepted programs' "
                 "execution stdout is expected (own recovered output), per PREREGISTRATION.md §9"),
        "result": "PASS" if (not violations and stdout_counts_ok) else "FAIL",
        "scan_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if (time := __import__("time")) else None,
    }
    (NS / "LEAK_SCAN.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": out["result"], "files_scanned": len(all_files),
                      "violations": len(violations),
                      "stdout_counts_match": stdout_counts_ok}))
    return 0 if out["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
