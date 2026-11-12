#!/usr/bin/env python3
"""Matched re-run of one P016 within-route labels arm on the AgentRouter route.

The labels arms ran at token floor 2800 (their _LAUNCH.json), an earlier
generation than the 4200-floor cohorts, so they cannot go through
rerun_ar_clone.py (which asserts floor == 4200 and a _REGISTRATION.json).
This script rebuilds the arm's registration from its _LAUNCH.json +
run_info.json, writes it BEFORE the first call, injects a dedicated
floor-2800 adapter (one-line diff from the frozen p023 adapter), and runs
the same frozen runner via parallelize_cohort.

Usage: python3 rerun_p016_arm.py gpt_6_1_sol
"""
import hashlib, importlib.util, json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARM = sys.argv[1] if len(sys.argv) > 1 else "gpt_6_1_sol"
SRC = HERE / "info_contract_aesgcm_labels_20261102" / ARM
OUT = HERE / f"info_contract_aesgcm_labels_{ARM}__rerun_ar_20261103"

launch = json.loads((SRC / "_LAUNCH.json").read_text())
run_info = json.loads((SRC / "run_info.json").read_text())
SEEDS = tuple(int(s) for s in launch["seeds"])
LABEL = launch["model_label"]
FLOOR = int(launch["token_floor"])
assert FLOOR == 2800, f"unexpected floor {FLOOR}"

ADAPTER = HERE / "provider_adapter_agentrouter_p016_floor2800.py"
ADAPTER_SHA = hashlib.sha256(ADAPTER.read_bytes()).hexdigest()
RUNNER = HERE / "run_info_contract_2x2_aesgcm.py"
RUNNER_SHA = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
assert RUNNER_SHA == launch["runner_sha256"], (
    f"runner bytes drifted: {RUNNER_SHA[:12]} != registered {launch['runner_sha256'][:12]}")

PROTOCOL = launch["protocol"] + "-RERUN-AR-v1"
reg = {
    "protocol": PROTOCOL,
    "registered": "2026-11-03",
    "registered_before_first_call": True,
    "rerun_of": f"info_contract_aesgcm_labels_20261102/{ARM}",
    "rerun_reason": ("transport-damaged labels arm re-run on AgentRouter; same label, "
                     "seeds, fixture, prompts, oracle, and token floor 2800"),
    "seeds": list(SEEDS),
    "label": LABEL,
    "fixture": "aesgcm",
    "token_floor": FLOOR,
    "token_floor_effective": FLOOR,
    "adapter": ADAPTER.name,
    "adapter_sha256": ADAPTER_SHA,
    "adapter_delta": "P017_TOKEN_FLOOR 4200 -> 2800; every other byte identical to provider_adapter_agentrouter_p023.py",
    "runner_sha256": RUNNER_SHA,
    "cells": run_info.get("cells", ["C1", "C2", "C3", "C4"]),
    "workers": 6,
}
OUT.mkdir(exist_ok=True)
(OUT / "_REGISTRATION.json").write_text(json.dumps(reg, indent=1, sort_keys=True) + "\n")
prereg = (
    f"# {PROTOCOL} — pre-registered before first call\n\n"
    f"Re-run of the transport-damaged P016 labels arm `{ARM}` on the AgentRouter route.\n"
    f"- seeds: {len(SEEDS)} (byte-identical to `{SRC.name}/_LAUNCH.json`)\n"
    f"- label: `{LABEL}`\n- token floor: {FLOOR} (the arm's registered floor; "
    f"adapter `provider_adapter_agentrouter_p016_floor2800.py`, sha-pinned)\n"
    f"- runner: frozen `run_info_contract_2x2_aesgcm.py` (sha256 verified against the launch record)\n"
    f"- fixture/prompts/oracle/predicate: unchanged\n"
    f"- transport delta only: P023-generation adapter (registered retry, no stream_options bug)\n"
)
(OUT / "PREREGISTRATION.md").write_text(prereg)

os.environ["AGENTROUTER_LABEL_MODEL"] = LABEL
os.environ.setdefault("ACTS_FAILURE_LOG", str(OUT / "failure_log.jsonl"))

spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
injected = importlib.util.module_from_spec(spec)
sys.modules["provider_adapter"] = injected
spec.loader.exec_module(injected)

sys.path.insert(0, str(HERE))
import run_info_contract_2x2_aesgcm as base  # noqa: E402
if base.ClaudeProvider is not injected.ClaudeProvider:
    raise SystemExit("frozen runner did not bind the injected provider")

base.OUT = OUT
base.PROTOCOL = PROTOCOL
base.SEEDS = SEEDS
base.CELLS = tuple(reg["cells"])
base.ROTATIONS = {
    0: tuple(reg["cells"]),
    1: tuple(reg["cells"][1:] + reg["cells"][:1]),
    2: tuple(reg["cells"][2:] + reg["cells"][:2]),
    3: tuple(reg["cells"][3:] + reg["cells"][:1]),
}

import parallelize_cohort as pc  # noqa: E402
summary = pc.run(base, base.OUT, workers=6, phase="rerun_ar")
print(json.dumps(summary.get("per_cell", {}), indent=1), flush=True)
