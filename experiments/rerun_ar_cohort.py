#!/usr/bin/env python3
"""Re-run one damaged P cohort on AgentRouter, byte-identically where possible.

Usage: python3 rerun_ar_cohort.py <original_namespace> [workers]

What it guarantees
------------------
* The frozen runner is resolved **by sha256**, not by filename: P018–P020 were run
  with a revision that now lives under a different name
  (`run_modern_aead_cohort.py`, sha `ec5bb5f1…`), so a filename lookup would
  silently swap the instrument.
* The registered seeds, cells, rotation, prompts, oracle and floor come from the
  original registration; only the transport changes.
* The transport is `provider_adapter_agentrouter_p023.py`: no `stream` /
  `stream_options` parameters (the P017 adapter's 400 defect) and the registered
  retry policy with backoff.

What it discloses
-----------------
* New namespace `<original>__rerun_ar_20261103` with its own `_REGISTRATION.json`,
  `_LAUNCH.json`, `PREREGISTRATION.md`, `failure_log.jsonl`.
* Label is the original label; no substitution.
"""
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ADAPTER = ROOT / "provider_adapter_agentrouter_p023.py"
BEARING = ("C1", "C3")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def runner_index():
    idx = {}
    for p in ROOT.glob("*.py"):
        try:
            idx[sha(p)] = p
        except OSError:
            continue
    return idx


def load_json(p):
    try:
        blob = json.loads(Path(p).read_text())
    except Exception:
        return {}
    return blob if isinstance(blob, dict) else {}


def seeds_of(reg):
    s = reg.get("seeds")
    if isinstance(s, str):
        try:
            s = json.loads(s)
        except Exception:
            return ()
    return tuple(int(v) for v in s) if isinstance(s, list) else ()


def resolve(orig_rel):
    orig = ROOT / orig_rel
    reg = load_json(orig / "_REGISTRATION.json")
    launch = load_json(orig / "_LAUNCH.json")
    if not reg and (orig.parent / "_REGISTRATION.json").exists():
        reg = load_json(orig.parent / "_REGISTRATION.json")
    label = (reg.get("label") or launch.get("model_label") or launch.get("model")
             or launch.get("label"))
    runner_sha = reg.get("runner") or launch.get("runner_sha256")
    return orig, reg, launch, label, runner_sha


def main(orig_rel, workers=8):
    orig, reg, launch, label, runner_sha = resolve(orig_rel)
    if not label:
        raise SystemExit(f"no label in {orig_rel}")
    if not runner_sha:
        raise SystemExit(f"no runner hash in {orig_rel}")

    idx = runner_index()
    runner = idx.get(runner_sha)
    if runner is None:
        raise SystemExit(f"no on-disk runner with sha {runner_sha[:16]} for {orig_rel}")

    seeds = seeds_of(reg)
    if not seeds:
        raise SystemExit(f"no registered seeds in {orig_rel}")

    ns = ROOT / (orig.name + "__rerun_ar_20261103")
    ns.mkdir(exist_ok=True)
    protocol = reg.get("protocol") or launch.get("protocol")
    protocol_rerun = f"{protocol}-RERUN-AR-v1"

    adapter_sha = sha(ADAPTER)
    reg_out = {
        "protocol": protocol_rerun,
        "rerun_of": orig_rel,
        "rerun_reason": "transport-damaged cohort re-run; same label, same seeds",
        "label": label,
        "runner": runner_sha,
        "runner_path": runner.name,
        "runner_resolution": "by sha256 (registered hash), not by filename",
        "adapter": ADAPTER.name,
        "adapter_sha256": adapter_sha,
        "seeds": list(seeds),
        "sessions_registered": 4 * len(seeds),
        "workers": workers,
        "registered": time.strftime("%Y-%m-%d"),
    }
    (ns / "_REGISTRATION.json").write_text(json.dumps(reg_out, indent=1, sort_keys=True) + "\n")
    (ns / "PREREGISTRATION.md").write_text(
        f"# {protocol_rerun}\n\n"
        f"Re-run of `{orig_rel}` on AgentRouter with the unchanged label `{label}`.\n\n"
        f"- Frozen runner resolved by sha256 `{runner_sha[:16]}…` → `{runner.name}`.\n"
        f"- Registered seeds: {len(seeds)}; sessions: {4 * len(seeds)}.\n"
        f"- Transport: `{ADAPTER.name}` (no `stream_options`, retry policy "
        f"`{getattr_retry()}`).\n"
        f"- Only the transport differs; prompts, cells, rotation, oracle and floor are\n"
        f"  the original bytes.\n"
        f"- Disclosure: rows carry `execution_concurrency`; retried attempts land in\n"
        f"  `failure_log.jsonl`.\n"
    )

    os.environ["AGENTROUTER_LABEL_MODEL"] = label
    os.environ.setdefault("ACTS_FAILURE_LOG", str(ns / "failure_log.jsonl"))

    spec = importlib.util.spec_from_file_location("provider_adapter", ADAPTER)
    injected = importlib.util.module_from_spec(spec)
    sys.modules["provider_adapter"] = injected
    spec.loader.exec_module(injected)
    if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
        raise SystemExit("adapter missing ClaudeProvider/ProviderFailure")

    modname = "frozen_" + runner.stem
    rspec = importlib.util.spec_from_file_location(modname, runner)
    base = importlib.util.module_from_spec(rspec)
    sys.modules[modname] = base
    rspec.loader.exec_module(base)
    if base.ClaudeProvider is not injected.ClaudeProvider:
        raise SystemExit("frozen runner did not bind the injected provider")
    if sha(runner) != runner_sha:
        raise SystemExit("runner changed under us")

    base.OUT = ns
    base.PROTOCOL = protocol_rerun
    base.SEEDS = seeds
    if not hasattr(base, "ROTATIONS") or not getattr(base, "ROTATIONS"):
        base.ROTATIONS = {0: ("C1", "C2", "C3", "C4"), 1: ("C2", "C3", "C4", "C1"),
                          2: ("C3", "C4", "C1", "C2"), 3: ("C4", "C1", "C2", "C3")}
    base.ROTATIONS = {i: base.ROTATIONS[i % len(base.ROTATIONS)]
                      for i in range(max(len(seeds), len(base.ROTATIONS)))}

    probe = injected.ClaudeProvider()
    (ns / "_LAUNCH.json").write_text(json.dumps({
        "protocol": protocol_rerun, "namespace": ns.name, "rerun_of": orig_rel,
        "model_label": probe.model, "route": "agentrouter",
        "endpoint": getattr(probe, "endpoint", None),
        "runner_sha256": runner_sha, "runner_file": runner.name,
        "adapter_sha256": adapter_sha, "seeds": len(seeds),
        "sessions_registered": 4 * len(seeds), "workers": workers,
        "started": time.time(),
    }, indent=2, sort_keys=True) + "\n")

    import parallelize_cohort as pc
    print(f"[{orig_rel}] -> {ns.name} label={label} sessions={4 * len(seeds)}", flush=True)
    return pc.run(base, ns, workers=workers)


def getattr_retry():
    try:
        spec = importlib.util.spec_from_file_location("adapter_peek", ADAPTER)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return getattr(m, "P023_POLICY", {}).get("max_attempts_per_call")
    except Exception:
        return "n/a"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: rerun_ar_cohort.py <original_namespace> [workers]")
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8)
