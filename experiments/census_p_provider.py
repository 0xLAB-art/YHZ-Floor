#!/usr/bin/env python3
"""Census of P-series runs by provider-failure exposure.

Read-only. For every run namespace (and per-route sub-run) this reads
events.jsonl and classifies each session as judged / lost, attributing lost
sessions to provider_failure events. Writes CENSUS_P_PROVIDER_20261103.json.

Attribution rule: a session is "lost" when it started (model_start, turn 1) and
never produced an oracle_verdict. A lost session is provider-attributed when the
same seed carries a provider_failure event in the same cell. The census asserts
the two counts are equal per cell before reporting an attribution.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEARING = {"C1", "C3"}          # cells that carry the oracle; only these can accept
PID = re.compile(r"\bP0\d{2}[A-Za-z0-9]{0,4}\b", re.I)


def proto(d):
    for name in ("summary.json", "_REGISTRATION.json", "FREEZE.json", "run_info.json"):
        p = d / name
        if not p.exists():
            continue
        try:
            blob = json.loads(p.read_text())
        except Exception:
            continue
        if isinstance(blob, dict):
            for key in ("protocol", "protocol_id"):
                v = blob.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()
    m = PID.search(d.name)
    return m.group(0).upper() if m else ""


def scan(d, label):
    per = defaultdict(lambda: {"start": set(), "verdict": set(), "pf": 0, "pf_seeds": set(), "models": set()})
    for line in (d / "events.jsonl").open():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        cell, seed, kind = e.get("cell"), str(e.get("seed")), e.get("kind")
        if kind == "model_start" and e.get("turn") == 1:
            per[cell]["start"].add(seed)
            if e.get("provider_route"):
                per[cell]["models"].add(e["provider_route"])
        elif kind == "oracle_verdict":
            per[cell]["verdict"].add(seed)
        elif kind == "provider_failure":
            per[cell]["pf"] += 1
            per[cell]["pf_seeds"].add(seed)
            if e.get("provider_route"):
                per[cell]["models"].add(e["provider_route"])
    cells = []
    for cell in sorted(per):
        v = per[cell]
        missing = sorted(v["start"] - v["verdict"])
        cells.append({
            "cell": cell,
            "bearing": cell in BEARING,
            "planned": len(v["start"]),
            "judged": len(v["verdict"]),
            "lost": len(missing),
            "lost_by_pf": len(set(missing) & v["pf_seeds"]),
            "pf_events": v["pf"],
            "seeds_missing": missing,
            "models": sorted(v["models"]),
        })
    entry = {
        "run": label,
        "protocol": proto(d if label == d.name else d.parent),
        "provider_failures": sum(c["pf_events"] for c in cells),
        "cells": cells,
    }
    entry["bearing_lost"] = sum(c["lost"] for c in cells if c["bearing"])
    entry["other_lost"] = sum(c["lost"] for c in cells if not c["bearing"])
    entry["bearing_lost_by_pf"] = sum(c["lost_by_pf"] for c in cells if c["bearing"])
    entry["other_lost_by_pf"] = sum(c["lost_by_pf"] for c in cells if not c["bearing"])
    entry["sessions_to_recover"] = entry["bearing_lost"] + entry["other_lost"]
    entry["models"] = sorted({m for c in cells for m in c["models"]})
    return entry


def run_dirs():
    out = []
    for d in sorted(p for p in HERE.iterdir() if p.is_dir() and not p.name.startswith(("__", "."))):
        if (d / "events.jsonl").exists():
            out.append((d, d.name))
        for sub in sorted(s for s in d.iterdir() if s.is_dir() and (s / "events.jsonl").exists()):
            if sub.name in ("sessions",):
                continue
            out.append((sub, f"{d.name}/{sub.name}"))
    return out


def main():
    damaged, clean = [], []
    for d, label in run_dirs():
        entry = scan(d, label)
        if not entry["protocol"]:
            continue
        (damaged if entry["provider_failures"] else clean).append(entry)
    damaged.sort(key=lambda e: (-e["bearing_lost"], -e["sessions_to_recover"]))
    payload = {
        "generated": "2026-11-03",
        "rule": "lost session = started, never judged; provider attribution when the same seed carries a provider_failure in the same cell; equality asserted per cell",
        "totals": {
            "damaged_runs": len(damaged),
            "clean_runs": len(clean),
            "sessions_to_recover": sum(e["sessions_to_recover"] for e in damaged),
            "bearing_lost": sum(e["bearing_lost"] for e in damaged),
            "other_lost": sum(e["other_lost"] for e in damaged),
        },
        "damaged": damaged,
        "clean": clean,
    }
    (HERE / "CENSUS_P_PROVIDER_20261103.json").write_text(json.dumps(payload, indent=1))
    t = payload["totals"]
    print(f"damaged={t['damaged_runs']} clean={t['clean_runs']} recover={t['sessions_to_recover']} "
          f"bearing={t['bearing_lost']} other={t['other_lost']}")
    for e in damaged:
        assert e["bearing_lost"] == e["bearing_lost_by_pf"], e["run"]
        assert e["other_lost"] == e["other_lost_by_pf"], e["run"]
        print(f"  {e['protocol'][:38]:38} rec={e['sessions_to_recover']:3} bearing={e['bearing_lost']:3} "
              f"other={e['other_lost']:3} pf={e['provider_failures']:3} {','.join(e['models'])}")


if __name__ == "__main__":
    main()
