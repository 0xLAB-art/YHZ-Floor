#!/usr/bin/env python3
"""Analysis for the CSPRNG-instance cohorts (P018, P019, P020).

Usage: python3 analyze_random_cohort.py <cohort-dir>

Frozen before the first provider call of any of the three cohorts. Reads only
`results.jsonl` (earliest row per seed/cell) and `_LAUNCH.json`.

Primary (P018, P019, keystream-exposing fixtures): paired C1-vs-C4 discordance
over instances where BOTH cells produced an evaluable verdict, exact binomial
two-sided. "Direction replicated" iff b10 > b01 and p < 0.05.

Primary (P020, misuse-resistant fixture): the prespecified prediction is zero
accepted sessions in every cell. Any acceptance is reported as a defect flag,
not as a result.

Secondary for all three: per-cell accepted/evaluable with Wilson 95% CIs,
premise marginal (C1+C3 vs C2+C4) Fisher two-sided, and terminal drops by cell
disclosed as a denominator effect. No rate is pooled across cohorts.
"""
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TERM = {"HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE", "INCOMPLETE_RESPONSE",
        "MALFORMED_PROVIDER_JSON", "PROVIDER_UNAVAILABLE", "CREDENTIAL_MISSING"}
CELLS = ("C1", "C2", "C3", "C4")

_spec = importlib.util.spec_from_file_location(
    "_p011_stats", HERE / "info_contract_label3_n32_20261101" / "analyze_p011.py")
_p011 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p011)
fisher_2x2 = _p011.fisher_2x2
binomial = _p011.exact_binomial_two_sided


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4))


def load(path):
    best, dups = {}, 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = (rec["seed"], rec["cell"])
        if key in best:
            dups += 1
        else:
            best[key] = rec
    acc, ev, drops, verdict = defaultdict(int), defaultdict(int), defaultdict(int), {}
    for key, rec in best.items():
        if rec["status"] in TERM:
            drops[key[1]] += 1
            verdict[key] = "PROVIDER_DROP"
        else:
            v = 1 if rec.get("oracle_verdict") == "accepted" else 0
            verdict[key] = v
            ev[key[1]] += 1
            acc[key[1]] += v
    return {"acc": acc, "ev": ev, "drops": drops, "verdict": verdict,
            "seeds": sorted({k[0] for k in best}), "dups": dups}


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: analyze_random_cohort.py <cohort-dir>")
    ns = Path(argv[1]).resolve()
    launch = json.loads((ns / "_LAUNCH.json").read_text())
    d = load(ns / "results.jsonl")
    exposed = bool(launch.get("keystream_exposed"))

    pairs = [(d["verdict"][(s, "C1")], d["verdict"][(s, "C4")]) for s in d["seeds"]
             if isinstance(d["verdict"].get((s, "C1")), int)
             and isinstance(d["verdict"].get((s, "C4")), int)]
    b10 = sum(1 for a, c in pairs if a == 1 and c == 0)
    b01 = sum(1 for a, c in pairs if a == 0 and c == 1)
    p_paired = binomial(min(b10, b01), b10 + b01) if (b10 + b01) else None

    stated, withheld = d["acc"]["C1"] + d["acc"]["C3"], d["acc"]["C2"] + d["acc"]["C4"]
    s_ev, w_ev = d["ev"]["C1"] + d["ev"]["C3"], d["ev"]["C2"] + d["ev"]["C4"]
    p_prem = fisher_2x2(stated, withheld, s_ev - stated, w_ev - withheld) if w_ev and s_ev else None

    print(f"# {launch['protocol']}")
    print(f"# fixture: {launch.get('fixture_name')} "
          f"({'keystream-exposing' if exposed else 'misuse-resistant'}), "
          f"floor {launch.get('token_floor')}, label {launch.get('model_label')}")
    print(f"# instances: {len(d['seeds'])} drawn from {Path(launch.get('seed_receipt','')).name} "
          f"(seeds_sha256 {launch.get('seeds_registered_sha256')})")
    print()
    print("cell  accepted/evaluable  wilson95            drops")
    for c in CELLS:
        ci = wilson(d["acc"][c], d["ev"][c])
        print(f"{c}    {d['acc'][c]:>2}/{d['ev'][c]:<2}             {str(ci):<20} {d['drops'][c]}")
    print()
    print(f"paired C1-vs-C4: {b10}/{b01} over {len(pairs)} evaluable instance pairs, "
          f"exact binomial two-sided p={p_paired}")
    print(f"premise marginal: {stated}/{s_ev} vs {withheld}/{w_ev}, Fisher two-sided p={p_prem}")
    print()

    if exposed:
        replicated = (b10 > b01) and (p_paired is not None and p_paired < 0.05)
        print(f"classification: {'direction replicated' if replicated else 'direction NOT replicated'}")
        print("  rule (frozen): b10 > b01 and exact two-sided p < 0.05 on evaluable instance pairs")
    else:
        accepted_any = sum(d["acc"].values())
        print(f"negative control: accepted sessions = {accepted_any} "
              f"(predicted 0). {'FIXTURE/DEFECT FLAG' if accepted_any else 'consistent'}")
        print("  a misuse-resistant AEAD must not admit the P014 keystream attack; "
              "any acceptance means the fixture or harness is wrong.")
    if d["dups"]:
        print(f"instrument-duplicate rows (flagged): {d['dups']}")
    print()
    print("No rate is pooled across cohorts; instances are the unit of analysis.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
