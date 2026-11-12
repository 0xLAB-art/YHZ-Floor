#!/usr/bin/env python3
"""Shard a serial base.main() cohort across N concurrent processes.

The frozen 2x2 runner's main() executes its plan serially (~48 sessions/h).
Splitting the seeds across N shard namespaces — each importing the same frozen
runner with the same injected adapter, its own OUT, and its own seed bucket —
runs N concurrent serial plans (~N x 48/h). Rows are merged afterwards with
rerun_ar_clone.merge_shards; no row is rewritten.

Usage: shard_base_main.py <clone_namespace> <n_shards>
"""
import hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ns = HERE / sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8

reg = json.loads((ns / "_REGISTRATION.json").read_text())
ADAPTER = HERE / reg["adapter"]
assert hashlib.sha256(ADAPTER.read_bytes()).hexdigest() == reg["adapter_sha256"], "adapter hash mismatch"

seeds = [int(s) for s in reg["seeds"]]
buckets = [seeds[i::N] for i in range(N)]
shard_dirs = []
for i, bucket in enumerate(buckets):
    if not bucket:
        continue
    d = ns / f"shard_{i:02d}"
    d.mkdir(exist_ok=True)
    for sub in ("raw_provider_responses", "prompts", "execution_captures"):
        (d / sub).mkdir(exist_ok=True)
    sub_reg = dict(reg)
    sub_reg["seeds"] = bucket
    sub_reg["shard"] = {"index": i, "of": N, "parent": ns.name}
    (d / "_REGISTRATION.json").write_text(json.dumps(sub_reg, indent=1, sort_keys=True) + "\n")
    shard_dirs.append(d)

worker = r'''
import hashlib, importlib.util, json, os, sys
from pathlib import Path
HERE = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()
reg = json.loads((HERE / "_REGISTRATION.json").read_text())
ADAPTER = ROOT / reg["adapter"]
assert hashlib.sha256(ADAPTER.read_bytes()).hexdigest() == reg["adapter_sha256"]
os.environ["AGENTROUTER_LABEL_MODEL"] = reg["label"]
os.environ["APINEX_LABEL_MODEL"] = reg["label"]  # APINEX-routed cohorts (kimi-k3 labels) read this one
os.environ.setdefault("ACTS_FAILURE_LOG", str(HERE / "failure_log.jsonl"))
spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
inj = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = inj
spec.loader.exec_module(inj)
sys.path.insert(0, str(ROOT))
spec2 = importlib.util.spec_from_file_location("base_runner", str(ROOT / reg["runner_path"]))
base = importlib.util.module_from_spec(spec2)
sys.modules["base_runner"] = base
spec2.loader.exec_module(base)
assert base.ClaudeProvider is inj.ClaudeProvider, "frozen runner did not bind injected adapter"
base.OUT = HERE
base.PROTOCOL = reg["protocol"]
base.SEEDS = tuple(int(s) for s in reg["seeds"])
# resume: skip seeds whose every cell is already judged in THIS shard
_rp = HERE / "results.jsonl"
if _rp.exists():
    _recorded = {}
    for _line in _rp.read_text().splitlines():
        if _line.strip():
            _rec = json.loads(_line)
            _recorded.setdefault(_rec["seed"], set()).add(_rec["cell"])
    _complete = {s for s, cells in _recorded.items() if cells >= set(base.CELLS)}
    if _complete:
        base.SEEDS = tuple(s for s in base.SEEDS if s not in _complete)
base.main()
'''
(HERE / "_shard_worker.py").write_text(worker)

procs = []
for d in shard_dirs:
    log = (d / "console.log").open("w")
    env = dict(os.environ)
    env["AGENTROUTER_LABEL_MODEL"] = reg["label"]
    procs.append((subprocess.Popen([sys.executable, "-u", str(HERE / "_shard_worker.py"),
                                    str(d), str(HERE)], cwd=str(HERE), env=env,
                                   stdout=log, stderr=subprocess.STDOUT), log, d))
    time.sleep(0.3)
print(f"[shard] {len(procs)} shard workers started", flush=True)
bad = 0
for p, log, d in procs:
    rc = p.wait()
    log.close()
    if rc != 0:
        bad += 1
        print(f"[shard] {d.name} exit {rc}", flush=True)

sys.path.insert(0, str(HERE))
from rerun_ar_clone import merge_shards  # noqa: E402
summary = merge_shards(ns, shard_dirs, reg["protocol"], reg)
print(f"[shard] merged sessions={summary['sessions']} failures={summary['provider_failures']} bad_shards={bad}", flush=True)
sys.exit(0 if bad == 0 else 1)
