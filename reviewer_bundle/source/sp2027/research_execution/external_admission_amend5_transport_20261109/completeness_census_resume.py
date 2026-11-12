#!/usr/bin/env python3
"""Amendment-5 completeness-census RESUME: completes the suspended census.

The census (completeness_census_amend5.py) was suspended at 20/24 probes
by the operator account's quota exhaustion (HTTP 403, remaining quota
−$304.72, 2026-11-09) and the operator's stop order. Every raw row is
preserved verbatim in COMPLETENESS_CENSUS_stream.jsonl (append-only).

This script (registered, prereg §9/D1):
  1. reads the stream, computes which of the 24 expected (pair, label)
     combinations lack a TERMINAL measurement row (PASS / rumination
     overflow / completed-empty / completed-no-JSON);
  2. runs one cheap quota-guard auth probe FIRST — a still-overdrawn
     account is refused before any census spend;
  3. probes ONLY the missing combinations at the registered cap 12000
     with the effort field omitted, appending every raw row to the stream;
  4. assembles the final COMPLETENESS_CENSUS_AMEND5.json in the census's
     own schema (external-admission-amend5-completeness-census/1) from
     stream + new rows, last occurrence winning per combination — a
     re-probed row SUPERSEDES a quota-403 PROVIDER_FAILURE row (quota
     failures are transient account state, never a registered transport
     boundary; the stream keeps both rows for the record).

Non-evidence throughout (evidence=false). Run AFTER the operator account
is re-funded.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT_HASHES = HERE / "PROMPT_HASHES.json"
STREAM = HERE / "COMPLETENESS_CENSUS_stream.jsonl"
OUT = HERE / "COMPLETENESS_CENSUS_AMEND5.json"

LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
BASE_URL = (os.environ.get("AGENTROUTER_BASE_URL")
            or "https://agentrouter.org").rstrip("/")
CAP = 12000

# blocked thrice before (messages-wave, responses re-probe, funded account):
FROZEN_BLOCKED_PAIRS = [
    ["2015q-cry-eps_part2", "R0"],
    ["2015q-cry-eps_part2", "RT"],
    ["2017q-cry-almost_xor", "RT"],
    ["2018q-cry-babycrypto", "R0"],
    ["2018q-cry-babycrypto", "RT"],
    ["2018q-cry-lowe", "RT"],
]

TERMINAL_OUTCOMES = {"PASS_VISIBLE_JSON", "COMPLETION_RUMINATION_OVERFLOW",
                     "COMPLETED_EMPTY_TEXT", "COMPLETED_NO_JSON"}

from responses_client import AgentRouterResponsesClient, ProviderFailure  # noqa: E402


def classify(text: str, status, usage: dict) -> str:
    if status == "completed" and text.strip() and "\"code\"" in text:
        return "PASS_VISIBLE_JSON"
    if status == "incomplete" and not text.strip():
        return "COMPLETION_RUMINATION_OVERFLOW"
    if not text.strip():
        return "COMPLETED_EMPTY_TEXT"
    return "COMPLETED_NO_JSON"


def main() -> int:
    key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("AGENTROUTER_API_KEY not set in environment")

    manifest = json.loads(PROMPT_HASHES.read_text())
    prompts = {(e["task_id"], e["representation"]): e
               for e in manifest["instantiated_prompts"]}
    pairs = []
    for task, rep in sorted(prompts):
        if [task, rep] in FROZEN_BLOCKED_PAIRS:
            continue
        pairs.append((task, rep))
    expected = [(task, rep, label)
                for task, rep in pairs for label in LABELS]

    stream_rows = []
    if STREAM.exists():
        for line in STREAM.read_text().splitlines():
            if line.strip():
                stream_rows.append(json.loads(line))
    terminal_before = {(r["task_id"], r["representation"], r["label"])
                       for r in stream_rows
                       if r.get("outcome") in TERMINAL_OUTCOMES}
    missing = [c for c in expected if c not in terminal_before]
    print(json.dumps({"stream_rows": len(stream_rows),
                      "terminal_before_resume": len(terminal_before),
                      "re_probe_combinations": len(missing),
                      "missing": [list(c) for c in missing]}, indent=1,
                     sort_keys=True))

    # --- quota guard: one cheap probe; a blocked account burns nothing ---
    guard = AgentRouterResponsesClient(key, LABELS[0], BASE_URL, effort=None)
    try:
        g = guard.call('Reply with exactly: {"code": "print(1+1)"}', 256)
        guard_ok = bool((g["text"] or "").strip())
        guard_detail = ""
    except ProviderFailure as exc:
        guard_ok = False
        guard_detail = f"{exc.category}: {exc.detail[:200]}"
    if not guard_ok:
        raise SystemExit("quota guard FAILED — account still blocked, "
                         "re-fund before resuming: " + guard_detail)
    print(json.dumps({"quota_guard": "OK"}), flush=True)

    new_rows = []
    for task, rep, label in missing:
        entry = prompts[(task, rep)]
        path = HERE / entry["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise SystemExit(f"prompt hash mismatch: {path}")
        prompt = path.read_text()
        t0 = time.time()
        client = AgentRouterResponsesClient(key, label, BASE_URL,
                                            effort=None)
        try:
            r = client.call(prompt, CAP)
            text = r["text"]
            usage = r["metadata"]["usage"]
            status = r["metadata"].get("finish_reason")
            outcome = classify(text, status, usage)
            row = {"label": label, "task_id": task, "representation": rep,
                   "outcome": outcome, "status": status,
                   "text_chars": len(text),
                   "reasoning_tokens": usage.get("reasoning_tokens", 0),
                   "output_tokens": usage.get("output_tokens"),
                   "elapsed_s": round(time.time() - t0, 1), "cap": CAP}
        except ProviderFailure as exc:
            row = {"label": label, "task_id": task, "representation": rep,
                   "outcome": "PROVIDER_FAILURE", "category": exc.category,
                   "detail": exc.detail[:200],
                   "elapsed_s": round(time.time() - t0, 1), "cap": CAP}
        new_rows.append(row)
        with STREAM.open("a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        print(json.dumps(row, sort_keys=True), flush=True)

    # --- assemble: last occurrence wins per combination ---
    by_combo = {}
    for r in stream_rows + new_rows:
        if r.get("label"):
            by_combo[(r["task_id"], r["representation"], r["label"])] = r
    final_rows = [by_combo[c] for c in sorted(by_combo)]
    pass_rows = [r for r in final_rows
                 if r.get("outcome") == "PASS_VISIBLE_JSON"]
    pass_map = [[r["task_id"], r["representation"], r["label"]]
                for r in pass_rows]
    still_failing = [r for r in final_rows
                     if r.get("outcome") == "PROVIDER_FAILURE"]
    if still_failing:
        raise SystemExit(
            "census assembly refuses: "
            f"{len(still_failing)} combination(s) remain PROVIDER_FAILURE "
            "after the resume — a quota failure must never freeze as a "
            "registered boundary; resolve the account and re-run")

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
        "resume": {
            "stream_rows_at_resume": len(stream_rows),
            "terminal_before_resume": len(terminal_before),
            "re_probed_combinations": len(missing),
            "note": ("the census was suspended 2026-11-09 at the operator "
                     "account's quota 403 (remaining −$304.72) and the "
                     "operator's stop order; a re-probed row supersedes a "
                     "quota-403 PROVIDER_FAILURE row; the stream file keeps "
                     "every raw row verbatim (append-only)"),
        },
        "pass_combinations": pass_map,
        "grid_sessions": len(pass_rows) * 4,
        "rows": final_rows,
        "boundary": (
            "PASS entries define the registered plan; rumination-overflow "
            "and blocked entries are measured transport/reasoning-budget "
            "boundaries recorded as two-sided exclusions with rows — never "
            "zeros, never agent behavior"),
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pass_combinations": len(pass_map),
                      "grid_sessions": len(pass_rows) * 4,
                      "rumination_overflow":
                          sum(1 for r in final_rows
                              if r.get("outcome") ==
                              "COMPLETION_RUMINATION_OVERFLOW"),
                      "pass_pairs_by_task":
                          sorted({(r["task_id"], r["representation"])
                                  for r in pass_rows})},
                     indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
