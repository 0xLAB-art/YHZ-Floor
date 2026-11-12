#!/usr/bin/env python3
"""Amendment 10: regenerate the 30 ceiling-censored slots at 32000 output tokens.

Derived from run_pa_{61,56}.py by three textual injections, exactly the
Amendment-6 pattern:

  1. MAX_OUTPUT_TOKENS = 12_000  ->  32_000
  2. results_path = HERE / "results.jsonl"  ->  HERE / "results_c32.jsonl"
     (the original wave's evidence is never rewritten; the sweep prefers these
     rows for the slots they cover)
  3. a post-validation plan filter keeping only the censored tasks and this
     shard's seed: almost_xor, another_xor, crack_me.

Everything else (prompts, fixtures, oracle, codings, taxonomy, falsifiers,
turn cap, reasoning effort, halt thresholds, frozen client) is untouched.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSORED = ("2017q-cry-almost_xor", "2017q-cry-another_xor", "2021q-cry-crack_me")
SEEDS = (501, 502, 503, 504, 505)
BASE = {"61": "run_pa_61.py", "56": "run_pa_56.py"}

ANCHOR_SEED = "plan = build_plan(combos)\n"
ANCHOR_CEIL = "MAX_OUTPUT_TOKENS = 12_000\n"
ANCHOR_RES = '    results_path = HERE / "results.jsonl"\n'

INJECT = (
    "SHARD_SEED = {seed}\n"
    "CENSORED_TASKS = {censored!r}\n"
    "\n"
)


def make(tag: str, seed: int) -> Path:
    src = (HERE / BASE[tag]).read_text()
    for anchor in (ANCHOR_CEIL, ANCHOR_RES, ANCHOR_SEED):
        assert src.count(anchor) == 1, (tag, anchor)

    src = src.replace(ANCHOR_CEIL, "MAX_OUTPUT_TOKENS = 32_000\n")
    src = src.replace(ANCHOR_RES, '    results_path = HERE / "results_c32.jsonl"\n')

    # keyword args must match the base build_plan signature (label, task, rep, seed)
    src = src.replace(
        ANCHOR_SEED,
        ANCHOR_SEED
        + "    plan = [slot for slot in plan\n"
        "            if slot[3] == SHARD_SEED and slot[1] in CENSORED_TASKS]\n",
    )

    # bind the shard constants next to the protocol constants
    src = src.replace('PROTOCOL = "PHASE2-EXTERNAL-PUBLISHED-AUDIT-v1"\n',
                      'PROTOCOL = "PHASE2-EXTERNAL-PUBLISHED-AUDIT-v1"\n'
                      + INJECT.format(seed=seed, censored=CENSORED))

    out = HERE / f"run_pa_{tag}_s{seed}_c32.py"
    out.write_text(src)
    return out


if __name__ == "__main__":
    made = [make(tag, s) for tag in BASE for s in SEEDS]
    for p in made:
        print(f"wrote {p.name}  ({p.stat().st_size} bytes)")
    print(f"ceiling shard variants: {len(made)}")
