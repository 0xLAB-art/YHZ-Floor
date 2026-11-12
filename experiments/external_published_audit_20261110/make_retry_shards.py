#!/usr/bin/env python3
"""Amendment 14: parallel re-run of every still-unmeasured slot.

Two groups, one process per slot (all launched together):

  A. 13 transport-failed slots (gpt-6.1, HTTP 504 twice): 32000 tokens,
     1800s wall cap — identical instrument to Amendment 12.
  B. 7 slots still truncated after 4 turns x 32000 (gpt-5.6 almost_xor x5,
     crack_me s502/s505): ceiling raised to 64000 tokens, 1800s wall cap.

Derived from run_pa_{61,56}.py the same way as Amendments 4/6/10/12:
MAX_OUTPUT_TOKENS, the long-wall-cap client, a per-slot results file tagged
_r3 (so the previous attempts' rows are never overwritten and the runner's
resume-skip cannot swallow the retry), and a plan filter of one seed + one
task.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAG = {"gpt-6.1-sol": "61", "gpt-5.6-sol": "56"}   # 61=gpt-6.1, 56=gpt-5.6 (from LABELS in the runners)
BASE = {"61": "run_pa_61.py", "56": "run_pa_56.py"}

# Slots not yet covered by the (corrected) running wave: almost_xor gpt-6.1
# s501 is already solved and s502-s505 plus crack_me s502/s505 are running at
# 64k, so only the remaining 8 transport-failed slots are listed here.
GROUP_A_504 = [("gpt-6.1-sol", "2017q-cry-another_xor", s) for s in (501, 502, 503, 504, 505)]
GROUP_A_504 += [("gpt-6.1-sol", "2021q-cry-crack_me", s) for s in (501, 503, 504)]

GROUP_B_64K = [("gpt-5.6-sol", "2017q-cry-almost_xor", s) for s in (501, 502, 503, 504, 505)]
GROUP_B_64K += [("gpt-5.6-sol", "2021q-cry-crack_me", s) for s in (502, 505)]

ANCHOR_SEED = "plan = build_plan(combos)\n"
ANCHOR_CEIL = "MAX_OUTPUT_TOKENS = 12_000\n"
ANCHOR_PROTOCOL = 'PROTOCOL = "PHASE2-EXTERNAL-PUBLISHED-AUDIT-v1"\n'
ANCHOR_IMPORT = "from responses_client import AgentRouterResponsesClient, ProviderFailure  # noqa: E402\n"


def make(label: str, task: str, seed: int, tokens: int) -> Path:
    tag = TAG[label]
    src = (HERE / BASE[tag]).read_text()
    for anchor in (ANCHOR_CEIL, ANCHOR_SEED, ANCHOR_PROTOCOL, ANCHOR_IMPORT):
        assert src.count(anchor) == 1, (tag, anchor)

    taskkey = task.split("-", 1)[1].replace("-", "_")
    name = f"results_c32_slot_{tag}_{taskkey}_s{seed}_r4_{tokens // 1000}k.jsonl"

    src = src.replace(ANCHOR_CEIL, f"MAX_OUTPUT_TOKENS = {tokens:_}\n")
    src = src.replace(ANCHOR_IMPORT,
                      "from responses_client_long import AgentRouterResponsesClient, ProviderFailure  # noqa: E402\n")
    src = src.replace(ANCHOR_PROTOCOL,
                      ANCHOR_PROTOCOL
                      + f'SHARD_SEED = {seed}\nSHARD_TASK = "{task}"\n'
                      + f'RESULTS_NAME = "{name}"\n')
    src = src.replace(ANCHOR_SEED,
                      ANCHOR_SEED
                      + "    plan = [slot for slot in plan\n"
                      "            if slot[3] == SHARD_SEED and slot[1] == SHARD_TASK]\n")
    src = src.replace('    results_path = HERE / "results.jsonl"\n',
                      "    results_path = HERE / RESULTS_NAME\n")
    out = HERE / f"run_pa_{tag}_{taskkey}_s{seed}_r4_{tokens // 1000}k.py"
    out.write_text(src)
    return out


if __name__ == "__main__":
    made = [make(label, task, seed, 32_000) for label, task, seed in GROUP_A_504]
    made += [make(label, task, seed, 64_000) for label, task, seed in GROUP_B_64K]
    for p in made:
        print(p.name)
    print(f"retry variants: {len(made)}  (A 504-group {len(GROUP_A_504)}, B 64k-group {len(GROUP_B_64K)})")
