#!/usr/bin/env python3
"""AMENDMENT 6 (scheduling only): split each label-partitioned runner by SEED.

The registered plan is the census PASS combos x SEEDS (5 seeds). Amendment 4
partitioned by label (2 concurrent runners). This generator produces one
runner per (label, seed) slot — 10 concurrent processes — by injecting a
single post-validation plan filter into a copy of run_pa_61.py / run_pa_56.py.

Invariants preserved:
  * SEEDS stays [501..505] so the registered seed-range sweep check at
    verify_frozen_inputs() still matches seed_sweep_PUBLISHED_AUDIT.json.
  * the plan uniqueness check runs on the FULL plan (before the shard filter).
  * MAX_OUTPUT_TOKENS / MAX_TURNS / REASONING_EFFORT / protocol untouched.
  * the frozen runner (run_published_audit_sessions.py) is never modified.
  * shard plans are disjoint by seed, so no slot can be produced twice; the
    results.jsonl skip logic (run prefix) still covers restarts.
Zero model calls, zero network.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = [501, 502, 503, 504, 505]
SOURCES = {"61": "run_pa_61.py", "56": "run_pa_56.py"}

ANCHOR_SEEDS = 'SEEDS = [501, 502, 503, 504, 505]\n'
ANCHOR_PLAN = ('    plan = build_plan(combos)\n'
               '    if len({(l, t, r, s) for l, t, r, s in plan}) != len(plan):\n'
               '        fail("plan is not a unique slot list")\n')


def main() -> int:
    total = 0
    for tag, src in SOURCES.items():
        text = (HERE / src).read_text()
        if ANCHOR_SEEDS not in text:
            sys.exit(f"{src}: SEEDS anchor not found")
        if ANCHOR_PLAN not in text:
            sys.exit(f"{src}: plan anchor not found")
        for seed in SEEDS:
            body = text.replace(
                ANCHOR_SEEDS,
                ANCHOR_SEEDS + f'# AMENDMENT 6 seed shard: this process owns seed {seed}\n'
                               f'SHARD_SEED = {seed}\n', 1)
            body = body.replace(
                ANCHOR_PLAN,
                ANCHOR_PLAN + '    plan = [slot for slot in plan if slot[3] == SHARD_SEED]\n'
                              '    if not plan:\n'
                              '        fail("shard plan is empty")\n', 1)
            out = HERE / f"run_pa_{tag}_s{seed}.py"
            out.write_text(body)
            print(f"wrote {out.name}  ({len(body)} bytes)")
            total += 1
    print(f"shard variants: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
