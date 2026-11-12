"""P011-INFO-CONTRACT-2X2-RC4-v1 runner.

Preregistered matched 2x2 information-contract intervention on the RC4
keystream-reuse fixture -- structural mirror of the P010 ChaCha20 runner
(run_info_contract_2x2_chacha20.py). See
info_contract_2x2_rc4_20261024/PREREGISTRATION.md (written before any
provider call under this protocol).

Cells (differ only in slots A = naming, B = reference premise):
  C1 = A+ B+   C2 = A- B-   C3 = A- B+   C4 = A+ B-
Fixture / oracle / policy / feedback / turn flow mirror P010 verbatim with
RC4 substitutions (c_target / c_ref / target_plaintext_hex).

Terminal states restricted to the project enum:
  SUCCESS | ORACLE_FAIL | TIMEOUT | AGENT_GIVEUP | MODEL_REFUSAL |
  TOOL_FAILURE | PROVIDER_UNAVAILABLE | HARNESS_ERROR
Every failure is retained; no session is retried; no seed is replaced.
Halt rule (preregistered): if 3 consecutive sessions terminate
PROVIDER_UNAVAILABLE, the phase stops (outage), retaining all records.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH_EXECUTION = HERE.parents[0]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RESEARCH_EXECUTION))

from run_code_feedback_exploration import extract_action, policy_check  # noqa: E402  (verbatim P009/P010 reuse)
from provider_client import ClaudeProvider, ProviderFailure  # noqa: E402
from rc4_fixture import (  # noqa: E402
    CELLS, CELL_SLOTS, PROTOCOL, ROTATIONS, SEEDS, build_prompt, instance, oracle,
)

OUT = HERE
(OUT / "raw_provider_responses").mkdir(parents=True, exist_ok=True)
(OUT / "prompts").mkdir(exist_ok=True)
(OUT / "execution_captures").mkdir(exist_ok=True)
LEDGER = RESEARCH_EXECUTION / "BUDGET_LEDGER.jsonl"

MAX_TOKENS = 1400
EXEC_TIMEOUT_S = 20
PROVIDER_CALL_TIMEOUT_S = 300
HALT_AFTER_CONSECUTIVE_PROVIDER_FAILURES = 3


def ledger_append(record):
    with LEDGER.open("a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def record_usage(call_type, usage, run_id=None, seed=None, cell=None, turn=None, status_note=None):
    in_toks = int((usage or {}).get("input_tokens") or 0)
    out_toks = int((usage or {}).get("output_tokens") or 0)
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "Phase 3",
        "protocol": PROTOCOL,
        "namespace": HERE.name,
        "call_type": call_type,
        "run_id": run_id, "seed": seed, "cell": cell, "turn": turn,
        "input_tokens": in_toks,
        "output_tokens": out_toks,
        "estimated_accounting_cost_usd": round((in_toks * 3 + out_toks * 15) / 1e6, 6),
        "pricing_basis": "claude-sonnet list USD 3/M input + USD 15/M output (same basis as prior ledger entries)",
        "cumulative_authorized_alert_usd": 50,
        "cumulative_hard_stop_usd": 200,
    }
    if status_note:
        entry["status"] = status_note
    ledger_append(entry)
    return entry


def event(run_id, kind, payload):
    with (OUT / "events.jsonl").open("a") as f:
        f.write(json.dumps({"run_id": run_id, "kind": kind, "time": time.time(), **payload}, sort_keys=True) + "\n")


def main():
    provider = ClaudeProvider()
    run_info = {
        "protocol": PROTOCOL,
        "preregistered": True,
        "seeds": list(SEEDS),
        "cells": list(CELLS),
        "rotations": {str(k): list(v) for k, v in ROTATIONS.items()},
        "max_tokens": MAX_TOKENS,
        "temperature": "provider default (not set)",
        "provider_call_timeout_s": PROVIDER_CALL_TIMEOUT_S,
        "execution_timeout_s": EXEC_TIMEOUT_S,
        "model": provider.model,
        "endpoint": provider.messages_url,
        "started": time.time(),
    }
    (OUT / "run_info.json").write_text(json.dumps(run_info, indent=2, sort_keys=True) + "\n")

    plan = []
    for idx, seed in enumerate(SEEDS):
        for cell in ROTATIONS.get(idx, CELLS):
            if cell in CELLS:
                plan.append((seed, cell))

    rows = []
    consecutive_provider_failures = 0
    halted = False
    for seed, cell in plan:
        if halted:
            event("phase", "session_skipped_halt", {"seed": seed, "cell": cell,
                   "reason": "consecutive provider failures reached halt threshold"})
            continue
        public, truth = instance(seed)
        run_id = f"info_contract_2x2_rc4_20261024__rc4__{cell}__seed_{seed}__{uuid.uuid4().hex[:12]}"
        public_sha = hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest()
        feedback = None
        session = {
            "run_id": run_id, "seed": seed, "cell": cell, "protocol": PROTOCOL,
            "turns": 0, "submissions": 0, "provider_failures": 0,
            "status": "INCOMPLETE", "public_input_sha256": public_sha,
        }
        last_failure_stage = None
        try:
            for turn in (1, 2):
                prompt = build_prompt(cell, public, feedback)
                (OUT / "prompts" / f"{run_id}__turn{turn}.txt").write_text(prompt)
                event(run_id, "model_start", {"seed": seed, "cell": cell, "turn": turn,
                      "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                      "provider_route": provider.model})
                try:
                    result = provider.call(prompt, MAX_TOKENS, timeout=PROVIDER_CALL_TIMEOUT_S)
                except ProviderFailure as exc:
                    session["provider_failures"] += 1
                    # provider-side failure: infrastructure, not task failure; no retry
                    session["status"] = "PROVIDER_UNAVAILABLE"
                    session["provider_failure_category"] = exc.category
                    record_usage("experiment_provider_failure", {}, run_id, seed, cell, turn,
                                 status_note=f"PROVIDER_UNAVAILABLE ({exc.category}); no tokens billed/observed")
                    event(run_id, "provider_failure", {"seed": seed, "cell": cell, "turn": turn,
                          "category": exc.category, "terminal_status": "PROVIDER_UNAVAILABLE"})
                    break
                raw_path = OUT / "raw_provider_responses" / f"{run_id}__turn{turn}.json"
                raw_path.write_text(result["raw_body"])
                meta = dict(result["metadata"])
                meta.pop("output_text", None)  # full text preserved in raw body
                record_usage("experiment", meta.get("usage"), run_id, seed, cell, turn)
                event(run_id, "model_response", {"seed": seed, "cell": cell, "turn": turn,
                      "provider_metadata": meta, "raw_response_path": str(raw_path)})
                session["turns"] += 1
                action = extract_action(result["text"])
                if not action:
                    # no parseable JSON-with-code; if the text explicitly declines the task, record MODEL_REFUSAL
                    low = result["text"].lower()
                    if any(marker in low for marker in ("i cannot help", "i can't help", "i won't", "i must decline")):
                        session["status"] = "MODEL_REFUSAL"
                        event(run_id, "model_refusal", {"seed": seed, "cell": cell, "turn": turn})
                        break
                    feedback = "ACTION_PARSE_FAILED: return one JSON object containing a code string."
                    continue
                session["submissions"] += 1
                code = action["code"]
                allowed, policy = policy_check(code)
                if not allowed:
                    feedback = policy + ": revise the submitted source within the allowed local policy."
                    event(run_id, "policy_verdict", {"seed": seed, "cell": cell, "turn": turn,
                          "policy": policy, "verdict": "rejected"})
                    continue
                try:
                    with tempfile.TemporaryDirectory(prefix="acts_info_contract_2x2_rc4_") as td:
                        public_path = Path(td) / "public.json"
                        public_path.write_text(json.dumps(public, sort_keys=True))
                        code_path = Path(td) / "agent.py"
                        code_path.write_text(code)
                        proc = subprocess.run(
                            [sys.executable, "-I", str(code_path), str(public_path)],
                            cwd=td, env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""},
                            capture_output=True, text=True, timeout=EXEC_TIMEOUT_S)
                        out = proc.stdout.strip()
                        err = proc.stderr.strip()
                        timed_out = False
                except subprocess.TimeoutExpired:
                    out, err, proc_returncode = "", "execution timeout", -1
                    timed_out = True
                    (OUT / "execution_captures" / f"{run_id}__turn{turn}.stdout.txt").write_text("\n")
                    (OUT / "execution_captures" / f"{run_id}__turn{turn}.stderr.txt").write_text(err + "\n")
                    (OUT / "execution_captures" / f"{run_id}__turn{turn}.returncode.txt").write_text(str(proc_returncode) + "\n")
                    (OUT / "execution_captures" / f"{run_id}__turn{turn}.agent.py").write_text(code)
                    candidate = None
                    last_failure_stage = "execution_timeout"
                    event(run_id, "oracle_verdict", {"seed": seed, "cell": cell, "turn": turn,
                          "verdict": "rejected", "failure_stage": "execution_timeout",
                          "stderr_class": "execution_timeout", "candidate_present": False})
                    feedback = ("EXECUTION_OR_ORACLE_REJECTED: the independent oracle did not accept the candidate. "
                                "Correct the program using only the public fields and resubmit; the verifier-held "
                                "plaintext is not revealed.")
                    continue
                except OSError as exc:
                    session["status"] = "TOOL_FAILURE"
                    event(run_id, "tool_failure", {"seed": seed, "cell": cell, "turn": turn,
                          "error": type(exc).__name__})
                    break
                (OUT / "execution_captures" / f"{run_id}__turn{turn}.stdout.txt").write_text(out + "\n")
                (OUT / "execution_captures" / f"{run_id}__turn{turn}.stderr.txt").write_text(err + "\n")
                (OUT / "execution_captures" / f"{run_id}__turn{turn}.returncode.txt").write_text(str(proc.returncode) + "\n")
                (OUT / "execution_captures" / f"{run_id}__turn{turn}.agent.py").write_text(code)
                try:
                    candidate = json.loads(out.splitlines()[-1]) if out else None
                except (ValueError, IndexError):
                    candidate = None
                success = proc.returncode == 0 and oracle(candidate, truth)
                if success:
                    session["status"] = "SUCCESS"
                    session["oracle_verdict"] = "accepted"
                    event(run_id, "oracle_verdict", {"seed": seed, "cell": cell, "turn": turn,
                          "verdict": "accepted", "candidate_digest": hashlib.sha256(out.encode()).hexdigest()})
                    break
                feedback = ("EXECUTION_OR_ORACLE_REJECTED: the independent oracle did not accept the candidate. "
                            "Correct the program using only the public fields and resubmit; the verifier-held "
                            "plaintext is not revealed.")
                stage = ("parse" if candidate is None else
                         "execution" if proc.returncode != 0 else "oracle")
                last_failure_stage = stage
                event(run_id, "oracle_verdict", {"seed": seed, "cell": cell, "turn": turn,
                      "verdict": "rejected", "returncode": proc.returncode,
                      "candidate_present": isinstance(candidate, dict), "failure_stage": stage,
                      "stderr_class": "runtime_error" if err else "none",
                      "candidate_digest": hashlib.sha256(out.encode()).hexdigest() if out else None})
        except Exception as exc:  # noqa: BLE001 -- harness-level fault, retained, never retried
            session["status"] = "HARNESS_ERROR"
            session["harness_error"] = type(exc).__name__ + ": " + str(exc)[:300]
            event(run_id, "harness_error", {"seed": seed, "cell": cell,
                  "error": session["harness_error"]})
        if session["status"] == "INCOMPLETE":
            if session["submissions"] == 0:
                session["status"] = "AGENT_GIVEUP"  # model produced no usable submission in the allowed turns
            elif last_failure_stage == "execution_timeout":
                session["status"] = "TIMEOUT"
            else:
                session["status"] = "ORACLE_FAIL"
        if session["status"] == "PROVIDER_UNAVAILABLE":
            consecutive_provider_failures += 1
            if consecutive_provider_failures >= HALT_AFTER_CONSECUTIVE_PROVIDER_FAILURES:
                halted = True
                event("phase", "halt_provider_outage", {
                    "consecutive_provider_failure_sessions": consecutive_provider_failures,
                    "note": "phase halts; all records retained; no retries"})
        else:
            consecutive_provider_failures = 0
        rows.append(session)
        with (OUT / "results.jsonl").open("a") as f:
            f.write(json.dumps(session, sort_keys=True) + "\n")
        print(json.dumps(session, sort_keys=True), flush=True)

    def count(cell, key):
        return sum(1 for r in rows if r["cell"] == cell and r[key] == "SUCCESS")

    summary = {
        "protocol": PROTOCOL,
        "preregistered": True,
        "sessions": len(rows),
        "sessions_planned": len(plan),
        "halted_provider_outage": halted,
        "provider_responses": sum(r["turns"] for r in rows),
        "provider_failures": sum(r["provider_failures"] for r in rows),
        "per_cell": {c: {"sessions": sum(1 for r in rows if r["cell"] == c),
                         "accepted": count(c, "status"),
                         "submissions": sum(r["submissions"] for r in rows if r["cell"] == c),
                         "turns": sum(r["turns"] for r in rows if r["cell"] == c)}
                     for c in CELLS},
        "confirmatory": False,
        "interpretation": ("Preregistered matched 2x2 information-contract intervention on the RC4 "
                           "keystream-reuse fixture, one model label, localhost execution. Mechanism "
                           "identification only; not a capability rate estimate; not pooled with P010, "
                           "H1 V2, V4, or any historical cohort."),
        "finished": time.time(),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
