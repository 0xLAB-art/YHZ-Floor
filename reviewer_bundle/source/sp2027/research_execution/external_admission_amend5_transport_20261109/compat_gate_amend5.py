#!/usr/bin/env python3
"""Amendment-5 compat pre-gate: filter/route classification of the 14 frozen
(task, representation) prompt pairs BEFORE the freeze — the Amend-3 gate
discipline applied to Amendment-4's two measured transport killers:

  layer 1: empty-visible-content completions (hidden reasoning ate the
           budget under the /v1/messages facade) -> this gate requires the
           Responses transport to return NON-EMPTY visible text with the
           JSON contract present;
  layer 2: gateway content filter (HTTP 400 content-blocked) -> this gate
           verifies, per pair, whether the route serves the frozen prompt.

All calls are NON-EVIDENCE smokes (evidence=false; recorded per the
Amendment-4 AUTH_SMOKE precedent). One call per pair on a single label
(the filter was measured label-independent across all three labels in
Amendment-4: CONTENT_FILTER_MAP.json) + one AUTH smoke per label.

Output: COMPAT_GATE_AMEND5.json
  gate_pass_pairs: [(task, rep)] — pairs served with non-empty visible text
  gate_blocked_pairs: [(task, rep)] — HTTP 400 content-blocked pairs
  grid_defined_from_gate: 3 labels x pass pairs x seeds 425-428

The Amendment-5 runner refuses live mode until this file registers the
pair set, and it re-verifies every prompt hash against PROMPT_HASHES,
so a mid-run filter surprise on a registered-pass pair is classified
PROVIDER-side and stays an explicit event, never a silent default.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT_HASHES = HERE / "PROMPT_HASHES.json"
OUT = HERE / "COMPAT_GATE_AMEND5.json"

LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
GATE_LABEL = "gpt-5.6-sol"  # filter was label-independent in Amendment-4
BASE_URL = (os.environ.get("AGENTROUTER_BASE_URL") or "https://agentrouter.org")

from responses_client import AgentRouterResponsesClient, ProviderFailure  # noqa: E402


def main() -> int:
    key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("AGENTROUTER_API_KEY not set in environment")

    manifest = json.loads(PROMPT_HASHES.read_text())
    pairs = sorted((e["task_id"], e["representation"])
                   for e in manifest["instantiated_prompts"])

    client = AgentRouterResponsesClient(key, GATE_LABEL, BASE_URL)

    def probe(prompt: str, cap: int) -> dict:
        try:
            r = client.call(prompt, cap)
        except ProviderFailure as exc:
            return {"outcome": "PROVIDER_FAILURE",
                    "category": exc.category,
                    "detail": exc.detail[:200]}
        text = r["text"]
        usage = r["metadata"]["usage"]
        return {
            "outcome": ("PASS_VISIBLE_JSON" if ("\"code\"" in text and text.strip())
                        else "PASS_EMPTY_TEXT"),
            "text_chars": len(text),
            "finish_reason": r["metadata"]["finish_reason"],
            "reasoning_tokens": usage.get("reasoning_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "model_echo": r["metadata"].get("model_echo"),
            "transport": r["metadata"].get("transport"),
            "elapsed_s": r["metadata"].get("elapsed_s"),
        }

    passed, blocked, empty, rows = [], [], [], []
    for task, rep in pairs:
        path = (HERE / "fixtures" / "rt_transform" / task /
                f"prompt_{rep}.txt")
        prompt = path.read_text()
        sha = hashlib.sha256(prompt.encode()).hexdigest()
        entry = next(e for e in manifest["instantiated_prompts"]
                     if e["task_id"] == task and e["representation"] == rep)
        if sha != entry["sha256"]:
            raise SystemExit(f"prompt hash mismatch (pre-gate abort): {path}")
        res = probe(prompt, 4200)
        row = {"task_id": task, "representation": rep,
               "prompt_sha256": sha, **res}
        rows.append(row)
        if res["outcome"] == "PASS_VISIBLE_JSON":
            passed.append([task, rep])
        elif res["outcome"] == "PASS_VISIBLE_JSON_BAD" if False else \
             res["outcome"] == "PASS_EMPTY_TEXT":
            empty.append([task, rep])
        else:
            blocked.append([task, rep])
        print(json.dumps({"pair": [task, rep], **res}, sort_keys=True),
              flush=True)

    auth = {}
    for label in LABELS:
        lc = AgentRouterResponsesClient(key, label, BASE_URL)
        t0 = time.time()
        try:
            r = lc.call("Reply with exactly: {\"code\": \"print(1+1)\"}", 256)
            t = r["text"]
            auth[label] = {
                "outcome": "AUTH_SMOKE_OK" if t.strip() else
                           "AUTH_SMOKE_EMPTY_TEXT",
                "model_echo": r["metadata"].get("model_echo"),
                "finish_reason": r["metadata"].get("finish_reason"),
                "avg_elapsed_s": r["metadata"].get("elapsed_s"),
            }
        except ProviderFailure as exc:
            auth[label] = {"outcome": "AUTH_SMOKE_FAIL",
                           "category": exc.category,
                           "detail": exc.detail[:200]}

    expected_pairs = 14
    out = {
        "schema": "external-admission-amend5-compat-gate/1",
        "generated_date": time.strftime("%Y-%m-%d"),
        "evidence": False,
        "probe_class": "non-evidence route/prompt smokes (AUTH_SMOKE precedent)",
        "gate_label": GATE_LABEL,
        "labels_auth_smokes": auth,
        "total_pairs": expected_pairs,
        "gate_pass_pairs": passed,
        "gate_blocked_pairs": blocked,
        "gate_empty_text_pairs": empty,
        "defined_grid": {
            "labels": LABELS,
            "pass_pairs": len(passed),
            "seeds": [425, 426, 427, 428],
            "sessions": len(passed) * len(LABELS) * 4,
        },
        "rows": rows,
        "boundary": (
            "the content filter is a measured, gateway-wide transport "
            "property (blocked under both the prior and the funded account, "
            "and under both endpoints); blocked pairs are a registered "
            "boundary of the panel, excluded by the two-sided rule, never "
            "counted as zero or as agent behavior"),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("total_pairs", "gate_pass_pairs",
                                          "gate_blocked_pairs",
                                          "gate_empty_text_pairs",
                                          "defined_grid")},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
