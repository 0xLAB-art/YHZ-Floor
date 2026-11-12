#!/usr/bin/env python3
"""P016 launcher (one model label per process).

Same injection pattern as P010L3/P011/P014: the AgentRouter adapter is
registered in sys.modules["provider_adapter"] before the frozen runner import,
the runner bytes are asserted against _REGISTRATION.json, and _LAUNCH.json is
written before the first provider call.

Registered labels only; one directory per label; sequential scheduling (the
watch script runs this only after the P014 process exits) so two cohorts never
share one key.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

LABEL = os.environ.get("AGENTROUTER_LABEL_MODEL", "").strip()
if not LABEL:
    raise SystemExit("AGENTROUTER_LABEL_MODEL must name exactly one registered label")

REG = json.loads((HERE / "_REGISTRATION.json").read_text())
if LABEL not in REG["labels"]:
    raise SystemExit(f"label {LABEL!r} is not registered; registered={REG['labels']}")

FROZEN = ROOT / REG["runner_path"]
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != REG["runner"]:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got} != {REG['runner']}")

ADAPTER = ROOT / "provider_adapter_agentrouter.py"
adapter_sha = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)
if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
    raise SystemExit("injected adapter missing ClaudeProvider/ProviderFailure")

os.environ["AGENTROUTER_LABEL_MODEL"] = LABEL
import run_info_contract_2x2_aesgcm as base  # noqa: E402

if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did NOT bind the injected provider — aborting")
if base.ClaudeProvider.__module__ != "provider_adapter":
    raise SystemExit(f"unexpected provider module binding: {base.ClaudeProvider.__module__}")

slug = re.sub(r"[^A-Za-z0-9]+", "_", LABEL).strip("_")
OUT = HERE / slug
OUT.mkdir(parents=True, exist_ok=True)
for sub in ("raw_provider_responses", "prompts", "execution_captures"):
    (OUT / sub).mkdir(parents=True, exist_ok=True)

base.OUT = OUT
base.PROTOCOL = REG["protocol"]
base.LABEL = LABEL
base.SEEDS = tuple(int(v) for v in REG["seeds"])
base.ROTATIONS = {i: base.ROTATIONS[i % 4] for i in range(max(len(base.SEEDS), 4))}

provider_probe = injected.ClaudeProvider()  # resolves endpoint/model/key; no call
launch = {
    "protocol": base.PROTOCOL,
    "namespace": str(OUT.relative_to(ROOT)),
    "model_label": provider_probe.model,
    "route": "agentrouter",
    "endpoint_host": provider_probe.endpoint.split("//")[-1].split("/")[0],
    "runner_sha256": got,
    "adapter_sha256": adapter_sha,
    "seeds": list(base.SEEDS),
    "sessions_registered": 4 * len(base.SEEDS),
    "token_floor": getattr(injected, "LABEL2_TOKEN_FLOOR", None),
    "user_agent": getattr(injected, "LABEL2_UA", None),
    "started": time.time(),
}
(OUT / "_LAUNCH.json").write_text(json.dumps(launch, indent=2, sort_keys=True) + "\n")
print(json.dumps(launch, indent=2, sort_keys=True), flush=True)

if (OUT / "results.jsonl").exists():
    recorded = {}
    for line in (OUT / "results.jsonl").read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            recorded.setdefault(rec["seed"], set()).add(rec["cell"])
    complete = {s for s, cells in recorded.items() if cells >= set(base.CELLS)}
    if complete:
        base.SEEDS = tuple(s for s in base.SEEDS if s not in complete)
        (OUT / "resume_note.json").write_text(json.dumps(
            {"skipped_complete_seeds": sorted(complete),
             "seeds_to_run": list(base.SEEDS)}, indent=1, sort_keys=True) + "\n")

base.main()
