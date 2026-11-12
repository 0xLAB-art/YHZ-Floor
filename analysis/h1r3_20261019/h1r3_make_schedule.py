#!/usr/bin/env python3
"""Emit a frozen, globally randomized H1-R3 schedule from a design JSON file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from h1r3_run import build_schedule, sha_obj, write_json


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: h1r3_make_schedule.py design.json schedule.json")
        return 2
    design = json.loads(Path(sys.argv[1]).read_text())
    rows = build_schedule(design)
    payload = {"design": design, "schedule": rows, "schedule_seed": design["schedule_seed"],
               "n_sessions": len(rows), "schedule_hash": sha_obj([{k: r[k] for k in
               ("phase", "family", "level", "seed", "arm", "replicate_index", "kind", "ordinal")}
               for r in rows])}
    write_json(Path(sys.argv[2]), payload)
    counts = {}
    for row in rows:
        key = f"{row['family']}|{row['level']}|{row['arm']}|{row['kind']}"
        counts[key] = counts.get(key, 0) + 1
    print(json.dumps({"n_sessions": len(rows), "schedule_hash": payload["schedule_hash"],
                      "counts": counts}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
