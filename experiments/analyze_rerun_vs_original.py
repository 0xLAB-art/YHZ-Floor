#!/usr/bin/env python3
"""Unified rerun-vs-original analysis for the 2026-11-03 transport-repair wave.

For every rerun namespace (`*__rerun_ar_20261103`, plus P021AR which re-ran
`info_contract_aesgcm_random_p021_20261102`), compare against its original:

  per cell:  accepted (SUCCESS) | text-failed (ORACLE_FAIL) |
             floor-exhausted (EMPTY_RESPONSE -> FLOOR_EXHAUSTED per
             EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md) | transport (rest)

Also reports the amendment cohorts (A3, A3b) and the P026 floor-sensitivity
cohort as separate blocks. Idempotent: safe to rerun as cohorts finish;
incomplete reruns are marked so.

Writes RERUN_VS_ORIGINAL_20261103.{json,md}.
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUFFIX = "__rerun_ar_20261103"
BEARING = {"C1", "C3"}
CELL_ORDER = ["C1", "C2", "C3", "C4"]

def bucket(status):
    if status == "SUCCESS":
        return "accepted"
    if status == "ORACLE_FAIL":
        return "text_fail"
    if status == "EMPTY_RESPONSE":
        return "floor_exhausted"
    return "transport"

def tally(ns):
    p = HERE / ns / "results.jsonl"
    if not p.exists():
        return None
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    # dedupe (seed, cell): sharded salvage can append a re-judged pair; keep the
    # LAST row (most recent judgment) per pair
    by_pair = {}
    for r in rows:
        by_pair.setdefault((r.get("seed"), r.get("cell")), []).append(r)
    dupes = len(rows) - len(by_pair)
    per = {c: Counter() for c in CELL_ORDER}
    for pair_rows in by_pair.values():
        # acceptance is monotone: a pair that ever produced an accepted
        # submission counts as accepted regardless of later re-judgments
        if any(r.get("status") == "SUCCESS" for r in pair_rows):
            merged = {"status": "SUCCESS"}
        else:
            merged = pair_rows[-1]
        c = merged.get("cell") or "?"
        per.setdefault(c, Counter())[bucket(merged.get("status", "?"))] += 1
        per[c]["sessions"] += 1
    floor = 0
    for f in ("_REGISTRATION.json", "FREEZE.json", "_LAUNCH.json"):
        fp = HERE / ns / f
        if fp.exists():
            try:
                floor = int(json.loads(fp.read_text()).get("token_floor") or 0)
            except Exception:
                pass
            break
    return {"per_cell": {c: dict(per[c]) for c in per},
            "rows": len(by_pair), "rows_raw": len(rows), "duplicate_rows": dupes,
            "token_floor": floor or None}

def cohort_pair(rerun_ns, orig_ns):
    return {"rerun": rerun_ns, "original": orig_ns,
            "original_tally": tally(orig_ns), "rerun_tally": tally(rerun_ns)}

def main():
    pairs = []
    for d in sorted(HERE.glob(f"*{SUFFIX}")):
        if not (d / "results.jsonl").exists():
            continue
        orig = d.name[:-len(SUFFIX)]
        pairs.append(cohort_pair(d.name, orig))
    if (HERE / "info_contract_aesgcm_random_p021ar_20261103" / "results.jsonl").exists():
        pairs.append(cohort_pair("info_contract_aesgcm_random_p021ar_20261103",
                                 "info_contract_aesgcm_random_p021_20261102"))
    specials = {}
    for name in ("info_contract_aesgcm_random_p021ar_20261103/amendment_a3",
                 "info_contract_aesgcm_random_p021ar_20261103/amendment_a3b",
                 "info_contract_aesgcm_c2_floor8000_p026_20261103"):
        t = tally(name)
        if t:
            specials[name] = t
    payload = {"generated_note": "idempotent; rerun as cohorts finish",
               "pairs": pairs, "specials": specials}
    (HERE / "RERUN_VS_ORIGINAL_20261103.json").write_text(json.dumps(payload, indent=1))

    lines = ["# Rerun vs original — transport-repair wave (2026-11-03)", ""]
    for p in pairs:
        o, r = p["original_tally"], p["rerun_tally"]
        complete = "COMPLETE" if (r and r.get("rows") and all(
            r["per_cell"].get(c, {}).get("sessions") for c in ("C1", "C2", "C3", "C4"))) else "partial"
        lines.append(f"## {p['rerun']}  [{complete}]")
        lines.append(f"- original: `{p['original']}` floor={o['token_floor'] if o else '?'} rows={o['rows'] if o else 0}")
        if r:
            lines.append(f"- rerun: floor={r['token_floor']} rows={r['rows']}")
            hdr = "| cell | orig acc | rerun acc | rerun text_fail | rerun floor_exh | rerun transport |"
            lines += [hdr, "|---|---|---|---|---|---|"]
            for c in CELL_ORDER:
                oc = (o or {}).get("per_cell", {}).get(c, {})
                rc = r["per_cell"].get(c, {})
                lines.append(f"| {c} | {oc.get('accepted', 0)}/{oc.get('sessions', 0)} "
                             f"| {rc.get('accepted', 0)}/{rc.get('sessions', 0)} "
                             f"| {rc.get('text_fail', 0)} | {rc.get('floor_exhausted', 0)} "
                             f"| {rc.get('transport', 0)} |")
        else:
            lines.append("- rerun: no results yet")
        lines.append("")
    if specials:
        lines += ["## Amendment / sensitivity cohorts", ""]
        for name, t in specials.items():
            tot = Counter()
            for c, v in t["per_cell"].items():
                for k, n in v.items():
                    tot[k] += n
            lines.append(f"- `{name}`: rows={t['rows']} " +
                         " ".join(f"{k}={v}" for k, v in sorted(tot.items())))
    (HERE / "RERUN_VS_ORIGINAL_20261103.md").write_text("\n".join(lines) + "\n")
    print(f"pairs={len(pairs)} specials={len(specials)} -> RERUN_VS_ORIGINAL_20261103.{{json,md}}")

if __name__ == "__main__":
    main()
