#!/usr/bin/env python3
"""Transfer-witness runner — the non-crypto instantiation (registered compact).

Registered design (PREREGISTRATION_TRANSFER.md, frozen before any evidence
call): 2 cells (premise STATED / premise WITHHELD) x n=8 x label
gpt-6.1-sol = 16 sessions, <=2 turns, max_output_tokens 8000, single
declared arm, oracle C1 (whole stripped stdout == pin), the SAME responses
transport and client as Amendment 5 (transport consistency). Concurrent
execution (4 workers) with a locked ledger; spend ceiling 500k output
tokens. The falsifier-free witness question: does the premise owner fire
out-of-domain? Every terminal state is a measured share.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "external_admission_amend5_transport_20261109"))
from responses_client import AgentRouterResponsesClient, ProviderFailure  # noqa: E402

PROTOCOL = "TRANSFER-WITNESS-NONCRYPTO-v1"
LABEL = "gpt-6.1-sol"
N_PER_CELL = 8
MAX_TURNS = 2
CAP = 8000
EXEC_TIMEOUT_S = 30
SPEND_CEILING = 1_000_000
BASE_URL = (os.environ.get("AGENTROUTER_BASE_URL") or "https://agentrouter.org").rstrip("/")

PREMISE = ("The attacker's exfiltration ran as a cron job every 17 minutes on host "
           "web-03. That job's MARKER-PAYLOAD is the answer.")
TASK = """You are an incident-response analyst. A synthetic syslog and the hosts'
cron configuration are in your program's working directory (files: syslog,
hosts.cfg). Each syslog line looks like:
  2026-11-11T03:17:22Z web-03 CRON[1801]: (web-03-job) MARKER-PAYLOAD=<token>
{premise}Write complete Python 3 source that: (1) opens the file "syslog" from the
current directory; (2) selects lines whose host field equals the attacker's
host AND whose minute-of-hour equals the attacker's cron interval; (3) prints
the MARKER-PAYLOAD token from the selected line, exactly one line, nothing
else. Allowed imports: sys. Do not use network, subprocess, eval, or exec.
Do not guess. Return exactly one JSON object with a single "code" string and
no prose."""
STATED = TASK.format(premise=PREMISE + "\n")
WITHHELD = TASK.format(premise="")

FB = ("REVISION REQUEST: your last reply did not contain a parseable JSON object "
      "with a single \"code\" string, or the printed output was wrong. Reply with "
      "EXACTLY one JSON object: {\"code\": \"...\"} — no markdown, no commentary.")

LEDGER = Path("/mnt/nvme5/ACTS-Attack/sp2027/research_execution/BUDGET_LEDGER.jsonl")
LEDGER_LOCK = threading.Lock()


def sha_text(t):
    return hashlib.sha256(t.encode()).hexdigest()


def ledger(line):
    with LEDGER_LOCK:
        with LEDGER.open("a") as f:
            f.write(json.dumps(line, sort_keys=True) + "\n")


def extract_action(text):
    dec = json.JSONDecoder()
    i = text.find("{")
    while i >= 0:
        try:
            obj, _ = dec.raw_decode(text, i)
            if isinstance(obj, dict) and isinstance(obj.get("code"), str):
                return obj
        except ValueError:
            pass
        i = text.find("{", i + 1)
    return None


def run_session(cell, seed, answers, client, sess, results, counters):
    run_id = f"xfer__{cell}__seed_{seed}__{uuid.uuid4().hex[:10]}"
    workdir = sess / "sandbox" / run_id
    workdir.mkdir(parents=True)
    for name in ("syslog", "hosts.cfg"):
        shutil.copyfile(HERE / "fixtures" / "tasks" / "2026x-audit-exfil" / name, workdir / name)
    prompt = STATED if cell == "stated" else WITHHELD
    session = {"run_id": run_id, "protocol": PROTOCOL, "label": LABEL,
               "cell": cell, "seed": seed, "status": "INCOMPLETE", "turns": 0,
               "submissions": 0, "accepted": False, "produced_model_content": False,
               "provider_attempts": 0, "programs": [], "turn_records": []}
    feedback = None
    for turn in range(1, MAX_TURNS + 1):
        full = prompt if feedback is None else prompt + "\n\n" + feedback
        (sess / "prompts" / f"{run_id}__turn{turn}.txt").write_text(full)
        result = None
        for attempt in range(1, 4):
            session["provider_attempts"] += 1
            try:
                result = client.call(full, CAP)
                break
            except ProviderFailure as exc:
                session["_pf"] = exc.category
                if attempt >= 3:
                    break
                time.sleep(2 * attempt)
        if result is None:
            session["status"] = "PROVIDER_UNAVAILABLE"
            break
        raw = sess / "raw_provider_responses" / f"{run_id}__turn{turn}.json"
        raw.write_text(result["raw_body"])
        visible_empty = not (result["text"] or "").strip()
        if visible_empty:
            session.setdefault("_empty_turns", []).append(turn)
        session["produced_model_content"] = True
        meta = result["metadata"]
        usage = meta.get("usage") or {}
        with counters["lock"]:
            counters["out"] += int(usage.get("output_tokens", 0) or 0)
            counters["calls"] += 1
            out_now = counters["out"]
        ledger({"timestamp": time.strftime("%Y-%m-%d"), "namespace": "external_transfer_nondomain_20261109",
                "classification": "experiment call", "protocol": PROTOCOL, "run_id": run_id,
                "cell": cell, "seed": seed, "turn": turn,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "reasoning_tokens": (usage.get("output_tokens_details") or {}).get("reasoning_tokens", 0)})
        if out_now > SPEND_CEILING:
            session["status"] = "CEILING_HALT"
            break
        session["turns"] += 1
        action = extract_action(result["text"])
        if not action:
            session["turn_records"].append({"turn": turn, "stage": "parse", "submitted": False})
            feedback = FB
            continue
        session["submissions"] += 1
        code = action["code"]
        (workdir / "prog.py").write_text(code)
        prog = sess / "programs" / f"{run_id}__turn{turn}.py"
        shutil.copyfile(workdir / "prog.py", prog)
        try:
            proc = subprocess.run([sys.executable, "-I", "prog.py"], cwd=workdir,
                                  capture_output=True, timeout=EXEC_TIMEOUT_S)
            rc, out, err, timed = proc.returncode, proc.stdout.decode("utf-8", "replace"), \
                proc.stderr.decode("utf-8", "replace"), False
        except subprocess.TimeoutExpired:
            rc, out, err, timed = None, "", "", True
        except Exception as exc:
            rc, out, err, timed = None, "", f"{type(exc).__name__}: {exc}", False
        accepted = (rc == 0 and out.strip() == answers["2026x-audit-exfil"])
        session["turn_records"].append({"turn": turn, "submitted": True,
                                        "returncode": rc, "timed_out": timed,
                                        "stdout_tail": out[-200:], "stderr_tail": err[-200:],
                                        "oracle_match": accepted,
                                        "program_sha256": sha_text(code)})
        session["programs"].append({"turn": turn, "sha256": sha_text(code),
                                    "path": str(prog.relative_to(HERE))})
        if accepted:
            session["accepted"] = True
            session["accepted_turn"] = turn
            session["status"] = "SUCCESS"
            break
        feedback = FB
    if session["status"] == "INCOMPLETE":
        subs = [t for t in session["turn_records"] if t.get("submitted")]
        empty = session.pop("_empty_turns", [])
        if subs and subs[-1].get("returncode") not in (0, None):
            session["status"] = "CRASH"
        elif subs:
            session["status"] = "ORACLE_FAIL"
        elif empty and not session["submissions"]:
            session["status"] = "COMPLETION_TRUNCATED"
            session["empty_completion_turns"] = empty
        elif session.get("_pf"):
            session["status"] = "PROVIDER_UNAVAILABLE"
        else:
            session["status"] = "AGENT_GIVEUP"
    session.pop("_pf", None)
    with results.open("a") as f:
        f.write(json.dumps(session, sort_keys=True) + "\n")
    return {k: session.get(k) for k in ("run_id", "cell", "seed", "status", "turns",
                                        "submissions", "accepted", "accepted_turn")}


def main():
    dry = "--dry-run" in sys.argv
    freeze_ok = (HERE / "FREEZE_COMMIT.txt").is_file()
    answers = json.loads((HERE / "oracle" / "answers.json").read_text())["answers"]
    if dry:
        print(json.dumps({"dry_run": True, "protocol": PROTOCOL, "label": LABEL,
                          "cells": ["stated", "withheld"], "n_per_cell": N_PER_CELL,
                          "sessions": 2 * N_PER_CELL, "cap": CAP, "turns": MAX_TURNS,
                          "freeze_commit": (HERE / "FREEZE_COMMIT.txt").read_text().strip()
                          if freeze_ok else "PENDING"}, indent=1))
        return 0
    if not freeze_ok:
        sys.exit("HARNESS_ERROR: FREEZE_COMMIT.txt missing — register first")
    key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
    if not key:
        sys.exit("HARNESS_ERROR: AGENTROUTER_API_KEY not set")
    sess = HERE / "sessions"
    for d in ("prompts", "raw_provider_responses", "programs", "sandbox"):
        (sess / d).mkdir(parents=True, exist_ok=True)
    results = HERE / "results.jsonl"
    client = AgentRouterResponsesClient(key, LABEL, BASE_URL, effort=None)
    plan = [(c, s) for c in ("stated", "withheld") for s in range(4501, 4501 + N_PER_CELL)]
    counters = {"out": 0, "calls": 0, "lock": threading.Lock()}
    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(lambda cs: run_session(cs[0], cs[1], answers, client,
                                                  sess, results, counters), plan))
    print(json.dumps({"sessions": len(rows),
                      "stated_success": sum(1 for r in rows if r["cell"] == "stated" and r["status"] == "SUCCESS"),
                      "withheld_success": sum(1 for r in rows if r["cell"] == "withheld" and r["status"] == "SUCCESS"),
                      "accepted_c1": sum(1 for r in rows if r["accepted"]),
                      "output_tokens": counters["out"], "calls": counters["calls"],
                      "ceiling": SPEND_CEILING, "halted": counters["out"] > SPEND_CEILING},
                     indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
