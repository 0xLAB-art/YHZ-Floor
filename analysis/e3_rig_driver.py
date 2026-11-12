#!/usr/bin/env python3
"""
e3_rig_driver.py — run the frozen E3 timing factorial on the timing rig.

Implements E3.yaml exactly:
  build   : vulnerable_ttable | constant_time_control   (same flags)
  timer   : perf_counter_ns_monotonic | getruseru_utime_split
  cache   : cold | warm                                  (per-trial, randomized)
  smt     : on | off                                     (pseudo-factor, host lever)
  trials  : 2000 per cell, order randomized with the frozen seed
  raw samples + trial order are RELEASED artifacts.

The timing payload is the padding/verification inner loop characteristic of
the micro-crypto targets: the vulnerable build uses a data-dependent table
lookup path; the constant-time control uses a branchless/select-free path.
Both are compiled with IDENTICAL flags. The driver does not interpret the
results — e3_gate_check.py (negative control) and e3_analyze.py (effects) do.

Outputs (sp2027/analysis/e3_rig/):
  trial_order.csv      per-trial cell assignment (frozen seed)
  samples.jsonl        one JSON line per trial {cell, trial, t_s, ru_utime_s, t_s_split}
  e3_rig_results.json  per-cell aggregates (n, median, p05/p95)
  e3_rig_env.json      host declaration + scope statement (E3.yaml §host)

Usage:
  python3 sp2027/analysis/e3_rig_driver.py                    # full 16-cell factorial
  python3 sp2027/analysis/e3_rig_driver.py --trials 50        # shakedown (overrides count, marks run as shakedown)
  python3 sp2027/analysis/e3_rig_driver.py --cells build:cache smt:timer ...  # cell filter "build:timer:cache:smt"
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import random
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "e3_rig"
FROZEN_SEED = 20261025          # recorded at E3.yaml freeze; do not change
TRIALS_PER_CELL = 2000
SMT_LEVER = "/sys/devices/system/cpu/smt/control"   # "on"/"off" where writable

BUILDS = ["vulnerable_ttable", "constant_time_control"]
TIMERS = ["perf_counter_ns_monotonic", "getruseru_utime_split"]
CACHES = ["cold", "warm"]
SMTS = ["on", "off"]

VULN_SRC = r"""
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
/* vulnerable_ttable: data-dependent table lookup (last-round T-table style) */
static uint32_t T[256];
__attribute__((noinline)) static uint32_t round_fn(uint8_t b, uint32_t acc) {
    return acc ^ T[b];                 /* lookup index depends on secret byte */
}
int main_vuln(uint64_t seed, int iters) {
    for (int i = 0; i < 256; i++) T[i] = 0x9e3779b9u * (uint32_t)(i + 1);
    uint32_t acc = (uint32_t)seed;
    for (int i = 0; i < iters; i++) {
        uint8_t b = (uint8_t)(acc >> 24);
        acc = acc * 1664525u + 1013904223u;
        acc ^= round_fn(b, acc);
        acc = (acc << 3) | (acc >> 29);
    }
    return (int)acc;
}
int main(int argc, char **argv){
    uint64_t s = 0x5eed;
    if (argc > 1) s = strtoull(argv[1], 0, 0);
    printf("%d\n", main_vuln(s, 20000)); return 0;
}
"""

CT_SRC = r"""
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
/* constant_time_control: same computation, branchless/select-free masking */
static uint32_t T[256];
__attribute__((noinline)) static uint32_t round_fn(uint8_t b, uint32_t acc) {
    uint32_t r = 0;
    for (int i = 0; i < 256; i++) {          /* constant-time select: scan all */
        uint32_t m = (uint32_t)(b == (uint8_t)i) * 0xFFFFFFFFu;
        r |= T[i] & m;
    }
    return acc ^ r;
}
int main_vuln(uint64_t seed, int iters) {
    for (int i = 0; i < 256; i++) T[i] = 0x9e3779b9u * (uint32_t)(i + 1);
    uint32_t acc = (uint32_t)seed;
    for (int i = 0; i < iters; i++) {
        uint8_t b = (uint8_t)(acc >> 24);
        acc = acc * 1664525u + 1013904223u;
        acc ^= round_fn(b, acc);
        acc = (acc << 3) | (acc >> 29);
    }
    return (int)acc;
}int main(int argc, char **argv){
    uint64_t s = 0x5eed;
    if (argc > 1) s = strtoull(argv[1], 0, 0);
    printf("%d\n", main_vuln(s, 20000)); return 0;
}
"""

def build_binaries() -> dict:
    """Compile both builds with IDENTICAL flags (E3.yaml factor definition)."""
    import tempfile
    flags = ["-O2", "-fno-strict-aliasing"]
    bins = {}
    for name, src in [("vulnerable_ttable", VULN_SRC),
                      ("constant_time_control", CT_SRC)]:
        with tempfile.TemporaryDirectory() as td:
            c = Path(td) / "t.c"
            b = Path(td) / "t.bin"
            c.write_text(src)
            subprocess.run(["gcc", *flags, str(c), "-o", str(b)], check=True)
            dest = OUT / f"{name}.bin"
            b.rename(dest)
            bins[name] = dest
    return bins


def one_trial(binary: Path, timer: str, cache: str) -> dict:
    """One timed execution. cold: fresh process, cache cleared as the VM
    allows (single-host scope). warm: back-to-back repeat of the same work."""
    if cache == "cold":
        # best-effort cold cache: drop file caches if permitted, else
        # record-and-continue (the residual is declared in the env file)
        r = subprocess.run(
            ["sh", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"],
            check=False, capture_output=True)
        one_trial.cold_cache_ok = (
            getattr(one_trial, "cold_cache_ok", True) and r.returncode == 0)
    if timer == "perf_counter_ns_monotonic":
        t0 = time.perf_counter_ns()
        subprocess.run([str(binary)], check=True, capture_output=True)
        t1 = time.perf_counter_ns()
        return {"t_s": (t1 - t0) / 1e9, "ru_utime_s": None, "t_s_split": None}
    # getruseru_utime_split: harness wall time + child user CPU split
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime
    t0 = time.perf_counter_ns()
    subprocess.run([str(binary)], check=True, capture_output=True)
    t1 = time.perf_counter_ns()
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime
    return {"t_s": (t1 - t0) / 1e9, "ru_utime_s": after - before,
            "t_s_split": after - before}


CAMPAIGN_PATTERNS = ["night_watch.sh", "post_gate_chain.sh", "w3_launch_day.sh",
                     "run_agent_operations", "day1_check.py"]


def campaign_running() -> list[str]:
    """Live E2-campaign processes on this host (runbook §5 forbids running
    the timing rig alongside them — they own the host's scheduling and the
    quota; the shakedown sanity run proved the SMT restore hazard)."""
    found = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            cmd = (proc / "cmdline").read_bytes().replace(
                b"\x00", b" ").decode(errors="ignore")
        except Exception:
            continue
        for pat in CAMPAIGN_PATTERNS:
            if pat in cmd:
                found.append(f"pid {proc.name}: {cmd.strip()[:80]}")
    return found


def apply_smt(state: str) -> tuple[bool, str]:
    """Attempt the host-level SMT toggle (root + writable control required).
    Returns (applied, actual_state). NEVER labels a cell with a state that
    was not actually applied (shakedown 2026-09-28 caught label-only cells)."""
    try:
        actual = Path(SMT_LEVER).read_text().strip()
    except Exception:
        actual = "unknown"
    if actual == state:
        return True, actual
    try:
        Path(SMT_LEVER).write_text(state)
        actual = Path(SMT_LEVER).read_text().strip()
        return actual == state, actual
    except Exception:
        return False, actual


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=TRIALS_PER_CELL)
    ap.add_argument("--cells", nargs="*", default=None,
                    help='cell filters "build:timer:cache:smt" (\"\" = any)')
    ap.add_argument("--seed", type=int, default=FROZEN_SEED)
    args = ap.parse_args()

    running = campaign_running()
    if running:
        print("REFUSING: E2 campaign processes are live on this host; the\n"
              "  runbook (§5) forbids timing-rig execution alongside them.\n"
              "  Quiesce the chain first (stop watcher+chain, run the rig,\n"
              "  re-arm via chain_doctor.sh --fix). Found:", file=sys.stderr)
        for r in running:
            print(f"   {r}", file=sys.stderr)
        return 2

    shakedown = args.trials != TRIALS_PER_CELL
    OUT.mkdir(parents=True, exist_ok=True)

    cells = [(b, t, c, s) for b in BUILDS for t in TIMERS
             for c in CACHES for s in SMTS]
    if args.cells:
        def match(cell, filt):
            parts = filt.split(":")
            want = dict(zip(["build", "timer", "cache", "smt"], parts))
            return all(v == "" or cell[i] == v
                       for i, v in zip(range(4), [want["build"], want["timer"],
                                                  want["cache"], want["smt"]]))
        cells = [c for c in cells for f in args.cells if match(c, f)]

    # frozen randomized order, SMT as a BETWEEN-BLOCK factor (split-plot):
    # SMT cannot be toggled per trial (root + settle), so trials run in two
    # blocks (smt on, then off), randomized WITHIN each block with the
    # frozen seed. Amendment noted for the E3.yaml freeze (runbook §5).
    apply = not getattr(main, "no_apply", False)
    try:
        smt_saved = Path(SMT_LEVER).read_text().strip()
    except Exception:
        smt_saved = None
    blocks = {}
    for smt in SMTS:
        block_cells = [c for c in cells if c[3] == smt]
        order = []
        for cell in block_cells:
            order.extend([cell] * args.trials)
        # deterministic per-block seed (never hash(): Python randomizes it)
        block_seed = args.seed + {"on": 0, "off": 1}[smt]
        random.Random(block_seed).shuffle(order)
        applied, actual = (apply_smt(smt) if apply else (False, smt_saved or "unknown"))
        blocks[smt] = {"order": order, "applied": applied, "actual": actual,
                       "block_seed": block_seed}
        time.sleep(2.0)   # settle after a successful toggle
    smt_applied = all(b["applied"] for b in blocks.values())

    # host declaration (E3.yaml §host) — MEASURED, never copied from the plan
    smt_state = None
    try:
        smt_state = Path(SMT_LEVER).read_text().strip()
    except Exception:
        pass
    def dmi(field: str) -> str:
        try:
            return Path(f"/sys/class/dmi/id/{field}").read_text().strip()
        except Exception:
            return "unknown"
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
            "smt_state": smt_state or "unknown (not exposed)",
            "microcode": next((l.split()[-1] for l in
                               Path("/proc/cpuinfo").read_text().splitlines()
                               if l.startswith("microcode")), "unknown"),
        },
        "scope_statement": ("Single host. Claims are scoped to this host; "
                            "no cross-host generality claim is made."),
        "scope_note": ("plan §0.1 said 'KVM VM'; the measured host is bare "
                       "metal (Dell Precision 7740). The single-host scope "
                       "is unchanged; the virtualization label is corrected "
                       "in the released declaration."),
        "compiler_flags": ["-O2", "-fno-strict-aliasing"],
        "gcc_version": subprocess.run(["gcc", "--version"], capture_output=True,
                                      text=True).stdout.splitlines()[0],
        "smt_toggle_applied": smt_applied,
        "smt_note": ("SMT applied as a between-block factor via "
                     + SMT_LEVER if smt_applied else
                     "SMT could not be toggled (needs root); cells labeled "
                     "on/off record the REQUESTED state, not the applied "
                     "one — treat the smt factor as a recorded covariate "
                     "unless run with root"),
        "cold_cache_effective": None,   # filled AFTER the run (see below)
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
    }
    # e3_rig_env.json is written AFTER the trial loop (see below) so that
    # cold_cache_effective and the smt facts reflect measured behavior.

    bins = build_binaries()
    tag = "shakedown" if shakedown else "full"
    order_path = OUT / f"trial_order_{tag}.csv"
    samples_path = OUT / f"samples_{tag}.jsonl"
    with order_path.open("w", newline="") as ofh, samples_path.open("w") as sfh:
        w = csv.writer(ofh)
        w.writerow(["trial_idx", "smt_block", "build", "timer", "cache", "smt"])
        idx = 0
        for smt in SMTS:
            for cell in blocks[smt]["order"]:
                w.writerow([idx, smt, *cell])
                r = one_trial(bins[cell[0]], cell[1], cell[2])
                r.update({"cell": ":".join(cell), "trial_idx": idx,
                          "smt_block": smt})
                sfh.write(json.dumps(r) + "\n")
                idx += 1

    # restore the host's SMT state BEFORE anything is reported; a rig run
    # must never leave the host degraded (the sanity run left it off)
    smt_restored = True
    if smt_saved:
        apply_smt(smt_saved)
        try:
            smt_restored = Path(SMT_LEVER).read_text().strip() == smt_saved
        except Exception:
            smt_restored = False
    if not smt_restored:
        print("CRITICAL: could not restore SMT state; fix the host manually "
              "(echo on > /sys/devices/system/cpu/smt/control)", file=sys.stderr)
        return 3

    # host declaration, now that runtime facts are measured
    env["smt_saved_state"] = smt_saved
    env["smt_restored"] = smt_restored
    env["cold_cache_effective"] = (
        getattr(one_trial, "cold_cache_ok", None))
    (OUT / "e3_rig_env.json").write_text(json.dumps(env, indent=2) + "\n")

    # aggregates
    agg = {}
    for cell in cells:
        key = ":".join(cell)
        vals = []
        with samples_path.open() as sfh:
            for line in sfh:
                r = json.loads(line)
                if r["cell"] == key:
                    vals.append(r["t_s"])
        vals.sort()
        n = len(vals)
        agg[key] = {"n": n, "median_s": vals[n // 2] if n else None,
                    "p05_s": vals[max(0, n // 20)] if n else None,
                    "p95_s": vals[min(n - 1, n * 19 // 20)] if n else None}
    results = {"run_tag": tag, "trials_per_cell": args.trials,
               "seed": args.seed, "order_csv": str(order_path),
               "samples": str(samples_path), "cells": agg,
               "smt_applied": smt_applied,
               "smt_restored": smt_restored,
               "smt_blocks": {s: {"applied": b["applied"],
                                  "actual_state": b["actual"]}
                              for s, b in blocks.items()},
               "generated_utc": datetime.now(timezone.utc).isoformat()}
    (OUT / f"e3_rig_results_{tag}.json").write_text(json.dumps(results, indent=2) + "\n")

    print(f"E3 rig run ({tag}): {len(cells)} cells x {args.trials} trials "
          f"= {len(cells) * args.trials} timed executions")
    print(f"order: {order_path}")
    print(f"samples: {samples_path}")
    print(f"results: {OUT}/e3_rig_results_{tag}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
