#!/usr/bin/env python3
"""Amendment 12: full re-run of the 30 ceiling-censored slots, one process per slot.

Derived from run_pa_{61,56}.py, appearing in the same way as Amendments 4/6/10:

  1. MAX_OUTPUT_TOKENS = 12_000           -> 32_000
  2. import of responses_client           -> responses_client_long (generated
     here), whose only change is the hard join cap 420s -> 1800s; the frozen
     responses_client.py is not touched
  3. results path per slot: results_c32_slot_{tag}_{taskkey}_s{seed}.jsonl, so
     30 concurrent processes never append to one file and the registered
     results.jsonl is never written
  4. post-validation plan filter: this shard's seed and this shard's task only
     (so each process runs exactly one session and slots stay disjoint)
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSORED = ("2017q-cry-almost_xor", "2017q-cry-another_xor", "2021q-cry-crack_me")
SEEDS = (501, 502, 503, 504, 505)
BASE = {"61": "run_pa_61.py", "56": "run_pa_56.py"}

ANCHOR_SEED = "plan = build_plan(combos)\n"
ANCHOR_CEIL = "MAX_OUTPUT_TOKENS = 12_000\n"
ANCHOR_PROTOCOL = 'PROTOCOL = "PHASE2-EXTERNAL-PUBLISHED-AUDIT-v1"\n'
ANCHOR_IMPORT = "from responses_client import AgentRouterResponsesClient, ProviderFailure  # noqa: E402\n"


def long_client() -> Path:
    out = HERE / "responses_client_long.py"
    src = (HERE / "responses_client.py").read_text()
    assert src.count("_th.join(420)") == 1
    assert src.count('raise TimeoutError("hard 420s wall-clock cap exceeded")') == 1
    src = src.replace("_th.join(420)", "_th.join(1800)")
    src = src.replace('raise TimeoutError("hard 420s wall-clock cap exceeded")',
                      'raise TimeoutError("hard 1800s wall-clock cap exceeded")')
    src = src.replace("def call(self, prompt: str, max_output_tokens: int,\n             timeout: int = 600)",
                      "def call(self, prompt: str, max_output_tokens: int,\n             timeout: int = 1800)")
    out.write_text(src)
    return out


def make(tag: str, task: str, seed: int) -> Path:
    src = (HERE / BASE[tag]).read_text()
    for anchor in (ANCHOR_CEIL, ANCHOR_SEED, ANCHOR_PROTOCOL, ANCHOR_IMPORT):
        assert src.count(anchor) == 1, (tag, anchor)

    src = src.replace(ANCHOR_CEIL, "MAX_OUTPUT_TOKENS = 32_000\n")
    src = src.replace(ANCHOR_IMPORT,
                      "from responses_client_long import AgentRouterResponsesClient, ProviderFailure  # noqa: E402\n")
    taskkey = task.split("-", 1)[1].replace("-", "_")
    results_name = f"results_c32_slot_{tag}_{taskkey}_s{seed}.jsonl"
    src = src.replace(
        ANCHOR_PROTOCOL,
        ANCHOR_PROTOCOL
        + f'SHARD_SEED = {seed}\nSHARD_TASK = "{task}"\n'
        + f'RESULTS_NAME = "{results_name}"\n',
    )
    src = src.replace(ANCHOR_SEED,
                      ANCHOR_SEED
                      + "    plan = [slot for slot in plan\n"
                      "            if slot[3] == SHARD_SEED and slot[1] == SHARD_TASK]\n")
    src = src.replace('    results_path = HERE / "results.jsonl"\n',
                      '    results_path = HERE / RESULTS_NAME\n')
    out = HERE / f"run_pa_{tag}_{taskkey}_s{seed}_c32.py"
    out.write_text(src)
    return out


if __name__ == "__main__":
    print("wrote", long_client().name)
    made = [make(tag, task, s) for tag in BASE for task in CENSORED for s in SEEDS]
    for p in made:
        print(f"  {p.name}")
    print(f"slot shard variants: {len(made)}")
