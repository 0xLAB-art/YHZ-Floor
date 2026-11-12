#!/usr/bin/env python3
"""Pre-registration probe for the P024 token floor.

Runs AFTER P023 exits and BEFORE any P024 instance call. It replays the C2
condition on ONE already-spent P022 instance, so the diagnostic uses no P024
data and cannot contaminate the new cohort. Two samples at two ceilings:

  * 4200 (the P022 floor), then
  * 8400 (one doubling, not fitted to this sample).

Decision rule, fixed in the P024 preregistration before this script ran:
  text at 4200                        -> floor 4200
  no text at 4200, text at 8400       -> floor 8400
  no text at either ceiling           -> floor 4200, arm b expected model-level null

Writes probe_p024_floor.json next to this file.
"""
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADAPTER = HERE / "provider_adapter_agentrouter_p024.py"
P022_SEED = 2984588382247702924  # first seed of P022's receipt; already spent
DECISION_RULE = ("text@4200 -> 4200; no text@4200 and text@8400 -> 8400; "
                 "no text at either -> 4200 with arm-b model-level null flag")


def inject(floor):
    os.environ["ACTS_TOKEN_FLOOR"] = str(floor)
    spec = importlib.util.spec_from_file_location("provider_adapter_p024_probe", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    spec = importlib.util.spec_from_file_location(
        "frozen_runner", HERE / "run_info_contract_2x2_aesgcm.py")
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)

    public, _truth = base.instance(P022_SEED)
    prompt = base.build_prompt("C2", public)
    rows = []
    for floor in (4200, 8400):
        adapter = inject(floor)
        os.environ["ACTS_FAILURE_LOG"] = str(HERE / "probe_p024_failures.jsonl")
        provider = adapter.ClaudeProvider()
        os.environ["AGENTROUTER_LABEL_MODEL"] = "gpt-5.6-sol"
        provider.model = "gpt-5.6-sol"
        started = time.time()
        row = {"floor": floor, "label": "gpt-5.6-sol", "cell": "C2",
               "p022_seed": P022_SEED,
               "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
        try:
            result = provider.call(prompt, 1400, timeout=600)
            meta = result["metadata"]
            row.update({"outcome": "TEXT", "stop_reason": meta.get("finish_reason"),
                        "usage": meta.get("usage"),
                        "content_block_types": meta.get("content_block_types"),
                        "text_chars": len(result["text"]),
                        "body_excerpt": result["raw_body"][:300]})
        except adapter.ProviderFailure as exc:
            row.update({"outcome": "NO_TEXT", "category": exc.category,
                        "stop_reason": (exc.body_excerpt or "")[:300],
                        "text_chars": 0})
        row["latency_s"] = round(time.time() - started, 1)
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)

    text_4200 = rows[0]["outcome"] == "TEXT"
    text_8400 = rows[1]["outcome"] == "TEXT"
    if text_4200:
        floor = 4200
    elif text_8400:
        floor = 8400
    else:
        floor = 4200
    out = {
        "protocol": "P024-PROBE-TOKEN-FLOOR-v1",
        "decision_rule": DECISION_RULE,
        "decided_floor": floor,
        "arm_b_expected_model_level_null": (not text_4200 and not text_8400),
        "text_at_4200": text_4200,
        "text_at_8400": text_8400,
        "adapter_sha256": hashlib.sha256(ADAPTER.read_bytes()).hexdigest(),
        "rows": rows,
        "note": ("Diagnostic replay of one already-spent P022 instance. "
                 "No P024 seed is used; the sample enters no analysis."),
        "generated_at": time.time(),
    }
    (HERE / "probe_p024_floor.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
