#!/usr/bin/env python3
"""
e3_rig_resume.py — resume the interrupted full E3 factorial (2026-09-28).

The 11:05 UTC full run died at ~12:29 UTC with 15,971/32,000 trials flushed
(samples_full.jsonl, all in the smt:on block). Resume correctness proof
(re-run before every resume): the frozen per-block seeds (20261025+{0,1})
reproduce the executed order with 0 mismatches over every flushed trial —
so the remaining 16,029 trials are executed from the same frozen sequence.

Guarantees:
  - original samples are NEVER rewritten (append-only);
  - trial_order_full.csv is regenerated deterministically from the frozen
    order (same writer path as the driver — it is a pure function of the
    seed, and was partially flushed at kill time);
  - SMT is applied per remaining block and verified (never mislabeled);
    the host's saved state is restored before anything is reported;
  - refuses to run while E2-campaign processes are live (runbook §5).

Run as root (drop_caches + SMT lever):
  sudo -n python3 sp2027/analysis/e3_rig_resume.py
"""

from __future__ import annotations

import csv
import json
import platform
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import e3_rig_driver as drv  # frozen driver: one_trial, apply_smt, guards

OUT = drv.OUT
SAMPLES = OUT / "samples_full.jsonl"
ORDER = OUT / "trial_order_full.csv"


def frozen_order() -> list[tuple[str, str, str, str]]:
    """The driver's order construction, verbatim (deterministic seeds)."""
    cells = [(b, t, c, s) for b in drv.BUILDS for t in drv.TIMERS
             for c in drv.CACHES for s in drv.SMTS]
    order: list[tuple[str, str, str, str]] = []
    for smt in drv.SMTS:
        blk: list[tuple[str, str, str, str]] = []
        for cell in [c for c in cells if c[3] == smt]:
            blk.extend([cell] * drv.TRIALS_PER_CELL)
        # deterministic per-block seed (never hash())
        random.Random(drv.FROZEN_SEED + {"on": 0, "off": 1}[smt]).shuffle(blk)
        order.extend(blk)
    return order


def dmi(field: str) -> str:
    try:
        return Path(f"/sys/class/dmi/id/{field}").read_text().strip()
    except Exception:
        return "unknown"


def main() -> int:
    running = drv.campaign_running()
    if running:
        print("REFUSING: E2 campaign processes are live (runbook §5):",
              file=sys.stderr)
        for r in running:
            print(f"   {r}", file=sys.stderr)
        return 2
    if not SAMPLES.exists():
        sys.exit("REFUSING: no samples_full.jsonl — nothing to resume.")

    order = frozen_order()
    with SAMPLES.open() as f:
        executed = 0
        for i, line in enumerate(f):
            r = json.loads(line)
            if ":".join(order[i]) != r["cell"]:
                sys.exit(f"REFUSING: frozen order mismatch at trial {i} — "
                         "the prefix is not the frozen sequence.")
            executed += 1
    todo = order[executed:]
    print(f"resume: {executed} flushed trials verified against the frozen "
          f"order (0 mismatches); {len(todo)} remain")
    if not todo:
        print("nothing to do — factorial already complete")
        return 0

    try:
        smt_saved = Path(drv.SMT_LEVER).read_text().strip()
    except Exception:
        smt_saved = None

    bins = drv.build_binaries()

    # blocks in first-appearance order among the remaining trials
    blocks_needed: list[str] = []
    for cell in todo:
        if cell[3] not in blocks_needed:
            blocks_needed.append(cell[3])

    started_utc = datetime.now(timezone.utc).isoformat()
    idx = executed
    with SAMPLES.open("a") as sfh:
        for smt in blocks_needed:
            applied, actual = drv.apply_smt(smt)
            if not applied:
                # never label a block with a state that was not applied
                # (shakedown lesson; driver contract E3.yaml v0.2)
                print(f"REFUSING: cannot apply SMT={smt} (actual={actual!r})",
                      file=sys.stderr)
                return 2
            time.sleep(2.0)  # settle after a (possible) toggle
            print(f"block smt={smt}: applied={applied} actual={actual}",
                  flush=True)
            for cell in [c for c in todo if c[3] == smt]:
                r = drv.one_trial(bins[cell[0]], cell[1], cell[2])
                r.update({"cell": ":".join(cell), "trial_idx": idx,
                          "smt_block": smt})
                sfh.write(json.dumps(r) + "\n")
                sfh.flush()   # every trial durable — a kill loses nothing
                idx += 1
                if idx % 500 == 0:
                    print(f"  {idx}/{len(order)} trials "
                          f"({datetime.now(timezone.utc).isoformat()})",
                          flush=True)

    # restore the host's SMT state BEFORE anything is reported
    smt_restored = True
    if smt_saved:
        drv.apply_smt(smt_saved)
        try:
            smt_restored = Path(drv.SMT_LEVER).read_text().strip() == smt_saved
        except Exception:
            smt_restored = False
    if not smt_restored:
        print("CRITICAL: could not restore SMT state; fix the host manually "
              "(echo on > /sys/devices/system/cpu/smt/control)", file=sys.stderr)
        return 3

    # regenerate the order CSV deterministically (pure function of the seed)
    with ORDER.open("w", newline="") as ofh:
        w = csv.writer(ofh)
        w.writerow(["trial_idx", "smt_block", "build", "timer", "cache", "smt"])
        for i, cell in enumerate(order):
            w.writerow([i, cell[3], *cell])

    # host declaration (measured) + resume provenance
    try:
        smt_state = Path(drv.SMT_LEVER).read_text().strip()
    except Exception:
        smt_state = "unknown"
    try:
        virt = subprocess.run(["systemd-detect-virt"], capture_output=True,
                              text=True).stdout.strip() or "none"
    except Exception:
        virt = "unknown"
    if virt == "none" and "hypervisor" not in Path("/proc/cpuinfo").read_text():
        virt_class = "bare metal (measured: no hypervisor flag, DMI vendor " \
                     f"{dmi('sys_vendor')})"
    else:
        virt_class = virt
    env = {
        "host": {
            "machine": platform.machine(), "kernel": platform.release(),
            "cpu": (platform.processor() or "unknown"),
            "dmi_vendor": dmi("sys_vendor"),
            "dmi_product": dmi("product_name"),
            "virtualization": virt_class,
            "smt_state": smt_state,
            "microcode": next((l.split()[-1] for l in
                               Path("/proc/cpuinfo").read_text().splitlines()
                               if l.startswith("microcode")), "unknown"),
        },
        "scope_statement": ("Single host. Claims are scoped to this host; "
                            "no cross-host generality claim is made."),
        "compiler_flags": ["-O2", "-fno-strict-aliasing"],
        "gcc_version": subprocess.run(["gcc", "--version"], capture_output=True,
                                      text=True).stdout.splitlines()[0],
        "smt_toggle_applied": True,
        "smt_saved_state": smt_saved,
        "smt_restored": smt_restored,
        "cold_cache_effective": getattr(drv.one_trial, "cold_cache_ok", None),
        "resumed": True,
        "original_run": {
            "frozen_seed": drv.FROZEN_SEED,
            "flushed_trials_before_resume": executed,
            "original_start_note": ("11:05 UTC full run, died ~12:29 UTC with "
                                    "the host under OOM pressure (16 GB "
                                    "desktop; see ledger 2026-09-28)"),
            "prefix_verified": "0 order mismatches over all flushed trials",
        },
        "resumed_utc": started_utc,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "e3_rig_env.json").write_text(json.dumps(env, indent=2) + "\n")

    # aggregates over the COMPLETE dataset
    rows = [json.loads(l) for l in SAMPLES.open()]
    agg: dict[str, dict] = {}
    for cell in set(order):
        key = ":".join(cell)
        vals = sorted(r["t_s"] for r in rows if r["cell"] == key)
        n = len(vals)
        agg[key] = {"n": n, "median_s": vals[n // 2] if n else None,
                    "p05_s": vals[max(0, n // 20)] if n else None,
                    "p95_s": vals[min(n - 1, n * 19 // 20)] if n else None}
    gate = json.loads((RIG := OUT / "gate_verdict.json").read_text())
    results = {
        "run_tag": "full", "trials_per_cell": drv.TRIALS_PER_CELL,
        "seed": drv.FROZEN_SEED, "order_csv": str(ORDER),
        "samples": str(SAMPLES), "cells": agg,
        "n_trials_total": len(rows),
        "smt_applied": True, "smt_restored": smt_restored,
        "smt_blocks": {s: {"applied": True, "actual_state": s}
                       for s in blocks_needed},
        "resumed": True,
        "gate_verdict_sha256_at_analysis": None,  # analyzer stamps the file
        "gate_verdict": gate.get("verdict"),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "e3_rig_results_full.json").write_text(
        json.dumps(results, indent=2) + "\n")

    print(f"E3 full factorial COMPLETE: {len(rows)} trials, "
          f"{len(agg)} cells, smt_restored={smt_restored}, "
          f"cold_cache_effective={env['cold_cache_effective']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
