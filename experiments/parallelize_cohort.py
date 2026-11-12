#!/usr/bin/env python3
"""Concurrent session driver for the frozen 2x2 information-contract cohorts.

## What this changes, and what it does not

The frozen runner (`run_info_contract_2x2_aesgcm.py`) executes its plan as

    for seed, cell in plan:      # one session at a time
        ...

so wall-clock time is the sum of every session's provider latency. Sessions are
mutually independent: each one owns its seed, its public input, its prompt, its
two-turn harness feedback and its oracle truth. Nothing is shared across
sessions except the provider endpoint and the append-only logs.

This module keeps the per-session code path **verbatim** (same `instance()`,
`build_prompt()`, `extract_action()`, `policy_check()`, `oracle()`, same two
turns, same feedback strings, same 20 s local subprocess, same session status
vocabulary) and changes only the *scheduling*: independent sessions run on a
thread pool instead of one after another. Turn 1 -> feedback -> turn 2 inside a
session stays strictly sequential, so no session can observe another session's
output and the sampled distribution per session is unchanged.

## Resume

Resumption is at `(seed, cell)` granularity, not seed granularity: any pair that
already has a row in `results.jsonl` is skipped, including pairs whose row is a
terminal provider drop. This is deliberately stricter than the seed-level resume
in the launchers (which trims completed seeds and would re-derive rotation
indices from a shortened list).

## Disclosure carried into the record

Every row written here carries `execution_concurrency` and `execution_phase`, and
`_CONCURRENCY.json` records the worker count, the driver hash, the number of
pairs skipped, and the start time. That lets the analysis separate the serial
prefix from the parallel suffix if transport behaviour shifts under load.
"""
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

MAX_TOKENS = 1400
_LOCK = threading.Lock()


def _event(out, run_id, kind, payload):
    line = json.dumps({"run_id": run_id, "kind": kind, "time": time.time(), **payload},
                      sort_keys=True)
    with _LOCK:
        with (out / "events.jsonl").open("a") as fh:
            fh.write(line + "\n")


def _append_results(out, session):
    with _LOCK:
        with (out / "results.jsonl").open("a") as fh:
            fh.write(json.dumps(session, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())


def _done_pairs(path, cells):
    done = set()
    if not path.exists():
        return done
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("cell") in cells and "seed" in rec:
            done.add((rec["seed"], rec["cell"]))
    return done


def _session(base, out, provider, seed, cell, meta):
    """One session, copied from the frozen runner's main() loop body."""
    started = time.time()
    public, truth = base.instance(seed)
    run_id = f"{base.OUT.name}__{cell}__seed_{seed}__{uuid.uuid4().hex[:12]}"
    public_sha = hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest()
    feedback = None
    session = {
        "run_id": run_id, "seed": seed, "cell": cell, "protocol": base.PROTOCOL,
        "turns": 0, "submissions": 0, "provider_failures": 0,
        "status": "INCOMPLETE", "public_input_sha256": public_sha,
        **meta,
    }
    for turn in (1, 2):
        prompt = base.build_prompt(cell, public, feedback)
        (out / "prompts" / f"{run_id}__turn{turn}.txt").write_text(prompt)
        _event(out, run_id, "model_start",
               {"seed": seed, "cell": cell, "turn": turn,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "provider_route": provider.model})
        try:
            result = provider.call(prompt, MAX_TOKENS)
        except base.ProviderFailure as exc:
            session["provider_failures"] += 1
            session["status"] = exc.category
            _event(out, run_id, "provider_failure",
                   {"seed": seed, "cell": cell, "turn": turn, "category": exc.category})
            break
        raw_path = out / "raw_provider_responses" / f"{run_id}__turn{turn}.json"
        raw_path.write_text(result["raw_body"])
        md = dict(result["metadata"])
        md.pop("output_text", None)
        _event(out, run_id, "model_response",
               {"seed": seed, "cell": cell, "turn": turn,
                "provider_metadata": md, "raw_response_path": str(raw_path)})
        session["turns"] += 1
        action = base.extract_action(result["text"])
        if not action:
            feedback = "ACTION_PARSE_FAILED: return one JSON object containing a code string."
            continue
        session["submissions"] += 1
        code = action["code"]
        allowed, policy = base.policy_check(code)
        if not allowed:
            feedback = policy + ": revise the submitted source within the allowed local policy."
            continue
        with tempfile.TemporaryDirectory(prefix="acts_parallel_session_") as td:
            public_path = Path(td) / "public.json"
            public_path.write_text(json.dumps(public, sort_keys=True))
            code_path = Path(td) / "agent.py"
            code_path.write_text(code)
            proc = subprocess.run(
                [sys.executable, "-I", str(code_path), str(public_path)],
                cwd=td, env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""},
                capture_output=True, text=True, timeout=20)
            out_text = proc.stdout.strip()
            err = proc.stderr.strip()
            cap = out / "execution_captures"
            (cap / f"{run_id}__turn{turn}.stdout.txt").write_text(out_text + "\n")
            (cap / f"{run_id}__turn{turn}.stderr.txt").write_text(err + "\n")
            (cap / f"{run_id}__turn{turn}.returncode.txt").write_text(str(proc.returncode) + "\n")
            (cap / f"{run_id}__turn{turn}.agent.py").write_text(code)
            try:
                candidate = json.loads(out_text.splitlines()[-1]) if out_text else None
            except (ValueError, IndexError):
                candidate = None
            success = proc.returncode == 0 and base.oracle(candidate, truth)
            if success:
                session["status"] = "SUCCESS"
                session["oracle_verdict"] = "accepted"
                _event(out, run_id, "oracle_verdict",
                       {"seed": seed, "cell": cell, "turn": turn, "verdict": "accepted",
                        "candidate_digest": hashlib.sha256(out_text.encode()).hexdigest()})
                break
            feedback = ("EXECUTION_OR_ORACLE_REJECTED: the independent oracle did not accept "
                        "the candidate. Correct the program using only the public fields and "
                        "resubmit; the verifier-held plaintext is not revealed.")
            stage = ("parse" if candidate is None else
                     "execution" if proc.returncode != 0 else "oracle")
            _event(out, run_id, "oracle_verdict",
                   {"seed": seed, "cell": cell, "turn": turn, "verdict": "rejected",
                    "returncode": proc.returncode,
                    "candidate_present": isinstance(candidate, dict),
                    "failure_stage": stage,
                    "stderr_class": "runtime_error" if err else "none",
                    "candidate_digest": hashlib.sha256(out_text.encode()).hexdigest() if out_text else None})
    if session["status"] == "INCOMPLETE":
        session["status"] = "ORACLE_FAIL" if session["submissions"] else "NO_SUBMISSION"
    session["session_wall_seconds"] = round(time.time() - started, 2)
    return session


def _summarize(out, protocol, workers, phase, skipped, wall):
    best = {}
    for line in (out / "results.jsonl").read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            best.setdefault((rec["seed"], rec["cell"]), rec)
    rows = list(best.values())
    cells = sorted({r["cell"] for r in rows})
    return {
        "protocol": protocol,
        "preregistered": True,
        "sessions": len(rows),
        "provider_responses": sum(r["turns"] for r in rows),
        "provider_failures": sum(r["provider_failures"] for r in rows),
        "per_cell": {c: {"sessions": sum(1 for r in rows if r["cell"] == c),
                         "accepted": sum(1 for r in rows
                                         if r["cell"] == c and r["status"] == "SUCCESS"),
                         "submissions": sum(r["submissions"] for r in rows if r["cell"] == c),
                         "turns": sum(r["turns"] for r in rows if r["cell"] == c)}
                     for c in cells},
        "confirmatory": False,
        "execution": {"mode": "thread_pool", "workers": workers, "phase": phase,
                      "pairs_skipped_on_resume": len(skipped),
                      "wall_seconds": round(wall, 1),
                      "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "interpretation": ("Scheduling-only change: sessions independent, each still two turns "
                           "at most with harness feedback in between. No prompt, cell, floor, "
                           "label, or oracle differs from the registered runner."),
        "finished": time.time(),
    }


def run(base, out, workers, phase="parallel"):
    out = Path(out)
    for sub in ("raw_provider_responses", "prompts", "execution_captures"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    provider = base.ClaudeProvider()

    plan = []
    for idx, seed in enumerate(base.SEEDS):
        for cell in base.ROTATIONS.get(idx, base.CELLS):
            if cell in base.CELLS:
                plan.append((seed, cell))
    done = _done_pairs(out / "results.jsonl", set(base.CELLS))
    todo = [p for p in plan if p not in done]

    (out / "_CONCURRENCY.json").write_text(json.dumps({
        "driver": "parallelize_cohort.py",
        "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "workers": workers,
        "phase": phase,
        "max_tokens_per_call": MAX_TOKENS,
        "plan_sessions": len(plan),
        "already_recorded_pairs": len(done),
        "pairs_skipped_on_resume": len(done),
        "to_run": len(todo),
        "started": time.time(),
        "disclosure": ("Scheduling only. Sessions already recorded at (seed, cell) granularity "
                       "are not repeated. Rows carry execution_concurrency so the serial prefix "
                       "and the parallel suffix can be analysed separately."),
    }, indent=2, sort_keys=True) + "\n")
    print(f"parallel run: {len(todo)} sessions to run, {len(done)} already recorded, "
          f"{workers} workers", flush=True)

    meta = {"execution_concurrency": workers, "execution_phase": phase}
    started = time.time()
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_session, base, out, provider, s, c, meta): (s, c)
                   for s, c in todo}
        for index, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            seed, cell = futures[fut]
            try:
                row = fut.result()
            except Exception as exc:  # a crashed session must not kill the cohort
                row = {"run_id": f"driver_exc__{cell}__seed_{seed}__{uuid.uuid4().hex[:12]}",
                       "seed": seed, "cell": cell, "protocol": base.PROTOCOL,
                       "turns": 0, "submissions": 0, "provider_failures": 0,
                       "status": "DRIVER_EXCEPTION", "error": f"{type(exc).__name__}: {exc}",
                       **meta}
            rows.append(row)
            _append_results(out, row)
            acc = sum(1 for r in rows if r["status"] == "SUCCESS")
            elapsed = time.time() - started
            rate = index / elapsed * 3600 if elapsed else 0
            remaining = (len(todo) - index) / (rate / 3600) if rate else float("inf")
            print(f"[{index}/{len(todo)}] {cell} seed={seed} {row['status']} "
                  f"accepted_so_far={acc} {rate:.0f}/h eta={remaining / 3600:.1f}h",
                  flush=True)
            _event(out, row["run_id"], "session_complete",
                   {"seed": seed, "cell": cell, "status": row["status"],
                    "wall_seconds": row.get("session_wall_seconds")})

    summary = _summarize(out, base.PROTOCOL, workers, phase, done, time.time() - started)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return summary
