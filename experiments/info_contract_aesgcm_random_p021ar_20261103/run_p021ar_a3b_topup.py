#!/usr/bin/env python3
"""Amendment A3b — recover the A3-pass pairs lost to transport (HTTP_ERROR).

The A3 top-up re-ran the 51 floor-exhausted pairs; 18 of them failed with
retryable transport errors (route load under the concurrent queue). This pass
re-runs exactly those (seed, C2) pairs, stamped A3B, into amendment_a3b/.
No other session is touched. Any session returning the floor-exhaustion
signature (HTTP 200, output_tokens == floor, stop_reason length, empty text)
is FLOOR_EXHAUSTED per EMPTY_RESPONSE_CAUSAL_ANALYSIS_20261103.md and is
reported as such, not retried.
"""
import hashlib, importlib.util, json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

REG = json.loads((HERE / "_REGISTRATION.json").read_text())
ADAPTER = ROOT / REG["adapter"]
if hashlib.sha256(ADAPTER.read_bytes()).hexdigest() != REG["adapter_sha256"]:
    raise SystemExit("adapter hash mismatch")
os.environ["AGENTROUTER_LABEL_MODEL"] = REG["label"]
os.environ.setdefault("ACTS_FAILURE_LOG", str(HERE / "amendment_a3b" / "failure_log.jsonl"))

spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)

import run_info_contract_2x2_aesgcm as base  # noqa: E402
if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did not bind the injected provider")

a3rows = [json.loads(l) for l in (HERE / "amendment_a3" / "results.jsonl").read_text().splitlines() if l.strip()]
failed = {(int(r["seed"]), r["cell"]) for r in a3rows if r["status"] == "HTTP_ERROR"}
if not failed:
    raise SystemExit("no HTTP_ERROR pairs to recover")

seeds = tuple(int(s) for s in REG["seeds"])
affected = [i for i, s in enumerate(seeds) if any((s, c) in failed for c in base.CELLS)]

base.OUT = HERE / "amendment_a3b"
base.OUT.mkdir(exist_ok=True)
base.PROTOCOL = REG["protocol"] + "-A3B-TRANSPORT-RECOVERY"
base.SEEDS = tuple(seeds[i] for i in affected)
base.CELLS = tuple(sorted({c for (_, c) in failed}))
base.ROTATIONS = {pos: tuple(c for c in ("C1", "C2", "C3", "C4") if (seeds[i], c) in failed)
                  for pos, i in enumerate(affected)}

manifest = {
    "amendment": "A3B",
    "source_pass": "amendment_a3",
    "basis": "pairs whose A3-pass row has status HTTP_ERROR (retryable transport)",
    "pairs": sorted([s, c] for s, c in failed),
    "sessions_planned": sum(len(v) for v in base.ROTATIONS.values()),
    "note": "floor-exhaustion signatures in this pass are reported as FLOOR_EXHAUSTED, not retried",
}
(base.OUT / "_A3B_MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
print(json.dumps(manifest, indent=1), flush=True)

import parallelize_cohort as pc  # noqa: E402
summary = pc.run(base, base.OUT, workers=3, phase="amendment_a3b")
print(json.dumps(summary.get("per_cell", {}), indent=1), flush=True)
