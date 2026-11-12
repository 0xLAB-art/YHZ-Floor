#!/usr/bin/env python3
"""Corrected provider census — separates floor-exhaustion from transport loss.

The 2026-11-03 causal analysis (EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md)
proved that EMPTY_RESPONSE on this route is model-side floor exhaustion
(HTTP 200, output_tokens == floor exactly, stop_reason "length", empty text
block): the route never fails for these. The original census counted every
provider_failure event as provider-caused loss; this correction reclassifies:

  FLOOR_EXHAUSTED  — provider_failure events with category EMPTY_RESPONSE
                     (model deliberation outlasted the token floor; surfaced
                     as an empty text block by the route)
  TRANSPORT        — every other category (HTTP_ERROR, TIMEOUT, ...): the
                     route actually failed

Lost-session attribution is recomputed per class with the same
(seed, cell) matching rule as the original census. Where failure_log.jsonl
bodies exist for empty events, the signature (output_tokens == registered
floor) is verified and reported.
"""
import json, re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEARING = {"C1", "C3"}
FLOOR_EXHAUSTED = {"EMPTY_RESPONSE"}

def proto(d):
    for f in ("_REGISTRATION.json", "FREEZE.json", "_LAUNCH.json"):
        p = d / f
        if p.exists():
            try:
                return json.loads(p.read_text()).get("protocol", "")
            except Exception:
                pass
    return ""

def floor_of(d):
    for f in ("_REGISTRATION.json", "FREEZE.json", "_LAUNCH.json"):
        p = d / f
        if p.exists():
            try:
                return int(json.loads(p.read_text()).get("token_floor") or 0)
            except Exception:
                pass
    return 0

def scan(d, label):
    evs = [json.loads(l) for l in (d / "events.jsonl").read_text().splitlines() if l.strip()]
    per = defaultdict(lambda: {"start": set(), "verdict": set(),
                               "pf_floor": set(), "pf_transport": set(),
                               "pf_events_floor": 0, "pf_events_transport": 0})
    for e in evs:
        cell, seed, kind = e.get("cell"), str(e.get("seed")), e.get("kind")
        if kind == "model_start":
            per[cell]["start"].add(seed)
        elif kind == "oracle_verdict":
            per[cell]["verdict"].add(seed)
        elif kind == "provider_failure":
            if e.get("category") in FLOOR_EXHAUSTED:
                per[cell]["pf_floor"].add(seed)
                per[cell]["pf_events_floor"] += 1
            else:
                per[cell]["pf_transport"].add(seed)
                per[cell]["pf_events_transport"] += 1
    cells = []
    for cell in sorted(per):
        v = per[cell]
        missing = sorted(v["start"] - v["verdict"], key=int)
        cells.append({
            "cell": cell,
            "bearing": cell in BEARING,
            "planned": len(v["start"]),
            "judged": len(v["verdict"] & v["start"]),
            "lost": len(missing),
            "lost_floor_exhausted": len(set(missing) & v["pf_floor"]),
            "lost_transport": len(set(missing) & v["pf_transport"]),
            "pf_events_floor_exhausted": v["pf_events_floor"],
            "pf_events_transport": v["pf_events_transport"],
            "seeds_missing": missing,
        })
    entry = {"run": label, "protocol": proto(d), "cells": cells}
    entry["sessions_to_recover"] = sum(c["lost"] for c in cells)
    entry["lost_floor_exhausted"] = sum(c["lost_floor_exhausted"] for c in cells)
    entry["lost_transport"] = sum(c["lost_transport"] for c in cells)
    entry["bearing_lost"] = sum(c["lost"] for c in cells if c["bearing"])
    return entry

def verify_signature(runs):
    """Where failure_log bodies exist for empty events, check output_tokens == floor."""
    checked = ok = 0
    for d, _ in runs:
        fl = d / "failure_log.jsonl"
        if not fl.exists():
            continue
        fl_floor = floor_of(d) or 4200
        for line in fl.read_text().splitlines():
            if not line.strip():
                continue
            ev = json.loads(line)
            if ev.get("category") != "EMPTY_RESPONSE":
                continue
            m = re.search(r'"output_tokens":\s*(\d+)', ev.get("body_excerpt", ""))
            s = re.search(r'"stop_reason":"([^"]+)"', ev.get("body_excerpt", ""))
            if not m:
                continue
            checked += 1
            if int(m.group(1)) == fl_floor and (not s or s.group(1) == "length"):
                ok += 1
    return checked, ok

def main():
    runs = []
    for d in sorted(p for p in HERE.iterdir() if p.is_dir() and not p.name.startswith(("__", "."))):
        if (d / "events.jsonl").exists():
            runs.append((d, d.name))
        for sub in sorted(s for s in d.iterdir() if s.is_dir() and (s / "events.jsonl").exists()):
            if sub.name == "sessions":
                continue
            runs.append((sub, f"{d.name}/{sub.name}"))
    damaged = [scan(d, lb) for d, lb in runs]
    damaged = [e for e in damaged if e["sessions_to_recover"]]
    damaged.sort(key=lambda e: (-e["lost_transport"], -e["sessions_to_recover"]))
    checked, ok = verify_signature(runs)
    payload = {
        "generated": "2026-11-03",
        "supersedes_note": ("reclassification layer for CENSUS_P_PROVIDER_20261103: "
                            "EMPTY_RESPONSE events are model-side floor exhaustion "
                            "(see EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md), not "
                            "provider failure"),
        "signature_check": {"empty_bodies_checked": checked,
                            "output_tokens_eq_floor_and_stop_length": ok},
        "totals": {
            "damaged_runs": len(damaged),
            "sessions_to_recover": sum(e["sessions_to_recover"] for e in damaged),
            "lost_floor_exhausted": sum(e["lost_floor_exhausted"] for e in damaged),
            "lost_transport": sum(e["lost_transport"] for e in damaged),
        },
        "damaged": damaged,
    }
    (HERE / "CENSUS_P_PROVIDER_20261103_CORRECTED.json").write_text(json.dumps(payload, indent=1))
    t = payload["totals"]
    print(f"damaged={t['damaged_runs']} recover={t['sessions_to_recover']} "
          f"floor_exhausted={t['lost_floor_exhausted']} transport={t['lost_transport']} "
          f"| signature verified {ok}/{checked}")
    for e in damaged[:20]:
        print(f"  {e['run'][:52]:52} lost={e['sessions_to_recover']:3} "
              f"floor={e['lost_floor_exhausted']:3} transport={e['lost_transport']:3}")

if __name__ == "__main__":
    main()
