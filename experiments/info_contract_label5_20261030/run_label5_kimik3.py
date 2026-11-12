#!/usr/bin/env python3
"""P010L5-INFO-CONTRACT-2X2-CHACHA20-LABEL5-v1 — fifth-label replication.
Label: free/kimi-k3 (Moonshot AI) on https://api.apinex.bond.
"""
import hashlib, importlib.util, json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]
sys.path.insert(0, str(ROOT))
FROZEN = ROOT / "run_info_contract_2x2_chacha20.py"
FROZEN_SHA = "a08eab6f4be2401aacf1b39a47ba6960373164dcc57640d3672d8c36583ee198"
if hashlib.sha256(FROZEN.read_bytes()).hexdigest() != FROZEN_SHA:
    raise SystemExit("FROZEN RUNNER HASH MISMATCH")
ADAPTER = ROOT / "provider_adapter_apinex.py"
spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
inj = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = inj
spec.loader.exec_module(inj)
if not hasattr(inj, "ClaudeProvider"):
    raise SystemExit("no ClaudeProvider")
import run_info_contract_2x2_chacha20 as base
if base.ClaudeProvider is not inj.ClaudeProvider:
    raise SystemExit("binding failed")
base.OUT = HERE
base.PROTOCOL = "P010L5-INFO-CONTRACT-2X2-CHACHA20-LABEL5-v1"
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (HERE / sub).mkdir(parents=True, exist_ok=True)
os.environ["APINEX_LABEL_MODEL"] = "free/kimi-k3"
SEEDS = tuple(int(v) for v in os.environ.get(
    "ACTS_SEEDS", "221,222,223,224,225,226,227,228").split(",") if v.strip())
base.SEEDS = SEEDS
base.ROTATIONS = {i: base.ROTATIONS[i % 4] for i in range(max(len(SEEDS), 4))}
if (HERE / "results.jsonl").exists():
    recorded = {}
    for line in (HERE / "results.jsonl").read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            recorded.setdefault(rec["seed"], set()).add(rec["cell"])
    complete = {s for s, cells in recorded.items() if cells >= set(base.CELLS)}
    if complete:
        base.SEEDS = tuple(s for s in base.SEEDS if s not in complete)
        (HERE / "resume_note.json").write_text(
            json.dumps({"skipped": sorted(complete)}, indent=1))
base.main()
