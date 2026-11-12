#!/usr/bin/env python3
"""P015 cross-family cohort launcher (one model label per process).

Injects the APINEX transport adapter before importing the frozen AES-GCM
runner, asserts the runner bytes against `_REGISTRATION.json`, pins the label
and seeds for this process, and writes `_LAUNCH.json` (adapter SHA, resolved
model label, endpoint host, token floor) BEFORE the first provider call.

Deviation surface (identical in shape to P010L3/P011/P014, transport disclosed
in the preregistration and in the adapter docstring):

  1. PROVIDER INJECTION: adapter registered in sys.modules["provider_adapter"]
     before the runner import; the runner file stays byte-for-byte untouched
     and its SHA is asserted.
  2. TRANSPORT: APINEX OpenAI-compatible /v1/chat/completions, not Anthropic
     /v1/messages; temperature omitted (provider default).
  3. TOKEN FLOOR: 2800 uniform, recorded per call as max_tokens_sent.

One label per process, one namespace directory per label: no label ever shares
a results file, a seed set, or an analysis with another label.

Resume rule: interrupted launches resume at SEED granularity; provider-failure
sessions are terminal and never retried.
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
ROOT = HERE.parents[0]
sys.path.insert(0, str(ROOT))

LABEL = os.environ.get("APINEX_LABEL_MODEL", "").strip()
if not LABEL:
    raise SystemExit("APINEX_LABEL_MODEL must name exactly one registered label")

REG = json.loads((HERE / "_REGISTRATION.json").read_text())
if LABEL not in REG["labels"]:
    raise SystemExit(f"label {LABEL!r} is not in the registered label list {REG['labels']}")

FROZEN = ROOT / REG["runner_path"]
got = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
if got != REG["runner"]:
    raise SystemExit(f"FROZEN RUNNER HASH MISMATCH: {got} != {REG['runner']}")

ADAPTER = ROOT / "provider_adapter_apinex_l6.py"
adapter_sha = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)
if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
    raise SystemExit("injected adapter missing ClaudeProvider/ProviderFailure")

os.environ["APINEX_LABEL_MODEL"] = LABEL
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

provider_probe = injected.ClaudeProvider(model=LABEL)  # resolves key; no call
launch = {
    "protocol": base.PROTOCOL,
    "namespace": str(OUT.relative_to(ROOT.parent)),
    "model_label": provider_probe.model,
    "route": "apinex",
    "endpoint_host": provider_probe.endpoint.split("//")[-1].split("/")[0],
    "transport": "openai_chat_completions",
    "runner_sha256": got,
    "adapter_sha256": adapter_sha,
    "seeds": list(base.SEEDS),
    "sessions_registered": 4 * len(base.SEEDS),
    "token_floor": getattr(injected, "APINEX_TOKEN_FLOOR", None),
    "user_agent": getattr(injected, "APINEX_UA", None),
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
