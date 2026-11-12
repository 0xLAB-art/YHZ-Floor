#!/usr/bin/env python3
"""Amendment-5 completeness census (pre-gate v2, non-evidence).

Upgrade of compat_gate_amend5.py after the 2026-11-09 route calibration:
  - the backend IGNORES `reasoning.effort` (effort=low: reasoning consumed
    16,000 of a 16,000 budget, empty text) -> the census omits the effort
    field entirely;
  - the registered evidence-call budget is RE-CALIBRATED to
    max_output_tokens = 12000: at 4200 the lowe label-runs ruminated
    without finishing, while at 12000 gpt-6-astra (7,099 reasoning) and
    gpt-6.1-sol (4,142 reasoning) COMPLETED with a 2,076/2,052-char JSON
    program on the same frozen prompt;
  - the gateway filter set (6 pairs HTTP-400 content-blocked, including
    under the funded account and under /v1/responses) is NOT re-probed:
    measured thrice, label-independent; recorded as the frozen boundary.

Census: every NON-blocked pair x every registered label, one probe at the
registered cap, classified:
  PASS_VISIBLE_JSON   — status completed, JSON contract present
  COMPLETION_RUMINATION_OVERFLOW — status incomplete, reasoning == cap,
    empty text (a measured reasoning-budget boundary per (pair, label))
  other fields recorded for the register.

Output: COMPLETENESS_CENSUS_AMEND5.json — the runner's plan is built ONLY
from PASS (pair, label) entries; everything else is a registered two-sided
exclusion with its own row.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT_HASHES = HERE / "PROMPT_HASHES.json"
OUT = HERE / "COMPLETENESS_CENSUS_AMEND5.json"

LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
BASE_URL = (os.environ.get("AGENTROUTER_BASE_URL")
            or "https://agentrouter.org").rstrip("/")
CAP = 12000

# blocked thrice before (messages-wave, responses re-probe, new account):
FROZEN_BLOCKED_PAIRS = [
    ["2015q-cry-eps_part2", "R0"],
    ["2015q-cry-eps_part2", "RT"],
    ["2017q-cry-almost_xor", "RT"],
    ["2018q-cry-babycrypto", "R0"],
    ["2018q-cry-babycrypto", "RT"],
    ["2018q-cry-lowe", "RT"],
]

from responses_client import AgentRouterResponsesClient, ProviderFailure  # noqa: E402


def main() -> int:
    key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("AGENTROUTER_API_KEY not set in environment")

    manifest = json.loads(PROMPT_HASHES.read_text())
    prompts = {(e["task_id"], e["representation"]): e
               for e in manifest["instantiated_prompts"]}
    all_pairs = sorted(prompts)
    pairs = []
    for task, rep in all_pairs:
        if [task, rep] in FROZEN_BLOCKED_PAIRS:
            continue
        pairs.append((task, rep))

    rows = []
    for task, rep in pairs:
        entry = prompts[(task, rep)]
        path = HERE / entry["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise SystemExit(f"prompt hash mismatch: {path}")
        prompt = path.read_text()
        for label in LABELS:
            t0 = time.time()
            client = AgentRouterResponsesClient(key, label, BASE_URL,
                                                effort=None)
            try:
                r = client.call(prompt, CAP)
                text = r["text"]
                usage = r["metadata"]["usage"]
                reason_tok = usage.get("reasoning_tokens", 0)
                status = r["metadata"].get("finish_reason")
                if status == "completed" and text.strip() and "\"code\"" in text:
                    outcome = "PASS_VISIBLE_JSON"
                elif status == "incomplete" and not text.strip():
                    outcome = "COMPLETION_RUMINATION_OVERFLOW"
                elif not text.strip():
                    outcome = "COMPLETED_EMPTY_TEXT"
                else:
                    outcome = "COMPLETED_NO_JSON"
                row = {"label": label, "task_id": task,
                       "representation": rep,
                       "outcome": outcome,
                       "status": status,
                       "text_chars": len(text),
                       "reasoning_tokens": reason_tok,
                       "output_tokens": usage.get("output_tokens"),
                       "elapsed_s": round(time.time() - t0, 1),
                       "cap": CAP}
                rows.append(row)
            except ProviderFailure as exc:
                rows.append({"label": label, "task_id": task,
                             "representation": rep,
                             "outcome": "PROVIDER_FAILURE",
                             "category": exc.category,
                             "detail": exc.detail[:200],
                             "elapsed_s": round(time.time() - t0, 1),
                             "cap": CAP})
            print(json.dumps(rows[-1], sort_keys=True), flush=True)
            (HERE / "COMPLETENESS_CENSUS_stream.jsonl").open("a").write(
                json.dumps(rows[-1], sort_keys=True) + "\n")

    pass_rows = [r for r in rows if r.get("outcome") == "PASS_VISIBLE_JSON"]
    pass_map = [[r["task_id"], r["representation"], r["label"]]
                for r in pass_rows]
    n_slots = sum(1 for _ in pass_rows) * 4
    out = {
        "schema": "external-admission-amend5-completeness-census/1",
        "generated_date": time.strftime("%Y-%m-%d"),
        "evidence": False,
        "registered_cap": CAP,
        "effort_field": "omitted (backend measured to ignore it)",
        "frozen_blocked_pairs": FROZEN_BLOCKED_PAIRS,
        "frozen_blocked_note": ("HTTP 400 content-blocked verified on "
                                "/v1/messages (2026-11-07), /v1/responses "
                                "(2026-11-09), and under the funded account "
                                "(2026-11-09) — label-independent"),
        "pass_combinations": pass_map,
        "grid_sessions": n_slots,
        "rows": rows,
        "boundary": (
            "PASS entries define the registered plan; rumination-overflow "
            "and blocked entries are measured transport/reasoning-budget "
            "boundaries recorded as two-sided exclusions with rows — never "
            "zeros, never agent behavior"),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pass_combinations": len(pass_map),
                      "grid_sessions": n_slots,
                      "rumination_overflow":
                          sum(1 for r in rows
                              if r.get("outcome") ==
                              "COMPLETION_RUMINATION_OVERFLOW"),
                      "pass_pairs_by_task":
                          sorted({(r['task_id'], r['representation'])
                                  for r in pass_rows})},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
