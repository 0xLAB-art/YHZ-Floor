#!/usr/bin/env python3
r"""Amendment-4 session runner: 3 registered frontier labels x 7 tasks x
{R0, RT} x seeds {421,422,423,424} = 168 sessions, <=2 turns, under
PHASE2-EXTERNAL-ADMISSION-AMEND4-FRONTIER-v1.

Labels (agentrouter gateway, Anthropic-messages /v1/messages transport):
  gpt-5.6-sol, gpt-6-astra, gpt-6.1-sol   — the paper's registered GPT-family
  labels; provider-attested at call time, never digest-pinned.

Changes versus the frozen Amendment-3 runner (all registered up front in
PREREGISTRATION_AMEND4_FRONTIER.md; everything else verbatim):
  1. labels/seeds/max_tokens: frontier labels, seeds 421-424, token floor
     4200 (the P017-registered floor for this label family; uniform across
     arms and turns);
  2. DUAL-CODED ORACLE registered before the first call: C1 (registered
     primary, unchanged) = entire stripped stdout equals the pinned answer;
     C2 (second admissible normalization, P024b both-codings discipline) =
     the first flag-shaped token (regex flag\{[ -~]*?\}) in stdout equals
     the pinned answer, rc==0.  Both computed and recorded per turn;
     acceptance (SUCCESS) is C1; C2 reported side by side;
  3. CRASH status class added: final submitted program exits non-zero;
  4. cost ceiling enforced on output tokens (2.5M, soft checkpoint 2.0M);
     USD reconciled at settlement (token counts are the measurement-
     relevant quantity per Section 11).

Frozen inputs (hash-asserted at runtime against FREEZE.json /
PROMPT_HASHES.json): the 14 prompt files, the 10 declared artifacts,
oracle/answers.json (truth material, never prompt content),
census_nyu/criterion5_outcomes.json, seed_sweep_SEED_SWEEP.json.

The namespace-restricted freeze commit is the registration act.  Live mode
REFUSES to run until FREEZE_COMMIT.txt exists; `--dry-run` is offline and
performs the full frozen-input/grid verification without any provider
import or call.

Terminal states: SUCCESS, CRASH, ORACLE_FAIL, TIMEOUT, AGENT_GIVEUP,
MODEL_REFUSAL, TOOL_FAILURE, PROVIDER_UNAVAILABLE, HARNESS_ERROR.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORACLE = HERE / "oracle" / "answers.json"
FREEZE = HERE / "FREEZE.json"
FREEZE_COMMIT = HERE / "FREEZE_COMMIT.txt"

PROTOCOL = "PHASE2-EXTERNAL-ADMISSION-AMEND4-FRONTIER-v1"
BASE_URL = "https://agentrouter.org"
LABELS = ["gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-sol"]
SUBSTITUTE_ORDER = ["gpt-6.1-sol", "gpt-5.6-sol", "gpt-6-astra"]
SEEDS = [421, 422, 423, 424]
TASKS = [
    "2015q-cry-eps",
    "2015q-cry-eps_part2",
    "2017q-cry-almost_xor",
    "2017q-cry-another_xor",
    "2018q-cry-babycrypto",
    "2018q-cry-lowe",
    "2021q-cry-crack_me",
]
REPS = ["R0", "RT"]
MAX_TOKENS = 4200
TEMPERATURE = 0.2
# Pre-first-call amendments 1-2 of the preregistration: the route rejects an
# explicit 0.2 for gpt-6.1-sol AND (intermittently, per backend shard)
# gpt-6-astra — the frontier labels on this transport support only their
# default temperature. Registered resolution: the temperature field is
# OMITTED for every label (route default, 1.0), UNIFORM across all labels,
# tasks, representations, and turns — no differential treatment, no confound.
TEMP_BY_LABEL = {label: None for label in LABELS}
MAX_TURNS = 2
EXEC_TIMEOUT_S = 30
OUTPUT_TOKEN_CEILING = 2_500_000
OUTPUT_TOKEN_CHECKPOINT = 2_000_000
CONSECUTIVE_PROVIDER_FAIL_HALT = 3
MAX_PROVIDER_REATTEMPTS = 2

FLAG_RE = re.compile(r"flag\{[ -~]*?\}")

FB_REJECT = ("EXECUTION_OR_ORACLE_REJECTED: your previous submission did not "
             "run to completion or the oracle did not accept its output. "
             "Revise the program using only the provided artifacts and "
             "resubmit. Return exactly one JSON object with a single \"code\" "
             "string and no prose.")

REFUSAL_MARKERS = ("cannot assist", "won't", "will not", "refuse",
                   "unable to comply", "i can't help")

SESS = HERE / "sessions"


def sha_text(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fail(message: str) -> None:
    sys.exit(f"HARNESS_ERROR: {message}")


def label_slug(label: str) -> str:
    return label.split("/")[-1]


def verify_frozen_inputs() -> tuple[dict, dict, dict, dict]:
    if not FREEZE.is_file():
        fail("FREEZE.json missing")
    freeze = json.loads(FREEZE.read_text())
    if not str(freeze.get("status", "")).startswith("FROZEN"):
        fail("FREEZE.json is not in FROZEN status")
    if freeze.get("design", {}).get("labels") != LABELS:
        fail("registered label panel mismatch")
    if freeze.get("design", {}).get("seeds") != SEEDS:
        fail("registered seed range mismatch")
    if freeze.get("design", {}).get("max_tokens") != MAX_TOKENS:
        fail("registered token floor mismatch")
    for key, entry in freeze["files"].items():
        path = (HERE.parent / entry["path"]) if "path" in entry else (HERE / key)
        if sha_file(path) != entry["sha256"]:
            fail(f"frozen-input hash mismatch: {path}")

    manifest = json.loads((HERE / "PROMPT_HASHES.json").read_text())
    prompts = {(e["task_id"], e["representation"]): e
               for e in manifest["instantiated_prompts"]}
    for task in TASKS:
        for rep in REPS:
            entry = prompts[(task, rep)]
            if sha_file(HERE / entry["path"]) != entry["sha256"]:
                fail(f"prompt hash mismatch: {entry['path']}")
        for artifact in manifest["artifacts"][task]:
            path = HERE / "fixtures" / "tasks" / task / artifact["name"]
            if sha_file(path) != artifact["sha256"]:
                fail(f"artifact hash mismatch: {path}")

    oracle = json.loads(ORACLE.read_text())
    answers = oracle["answers"]
    if sorted(answers) != sorted(TASKS):
        fail("oracle task set mismatch")

    outcomes = json.loads(
        (HERE / "census_nyu" / "criterion5_outcomes.json").read_text())
    if sorted(outcomes["grid_membership"]) != sorted(TASKS):
        fail("grid membership mismatch")
    if outcomes["quorum"]["status"] != "MET":
        fail("criterion-5 quorum not met")

    sweep = json.loads((HERE / "seed_sweep_SEED_SWEEP.json").read_text())
    if sweep["candidate_range"] != SEEDS or not sweep["candidate_range_free"]:
        fail("seed-range sweep mismatch")
    return freeze, manifest, answers, outcomes


def extract_action(text):
    """Verbatim P009-family parser (JSON object with string 'code')."""
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


def run_program(program_path: Path, workdir: Path) -> dict:
    facts = {"stage": "exec", "proc_rc": None, "out": "", "err": "",
             "timed_out": False, "exec_error": None}
    argv = [sys.executable, "-I", str(program_path)]
    try:
        proc = subprocess.run(argv, shell=False, cwd=workdir,
                              capture_output=True, timeout=EXEC_TIMEOUT_S)
        facts["proc_rc"] = proc.returncode
        facts["out"] = proc.stdout.decode("utf-8", "replace")
        facts["err"] = proc.stderr.decode("utf-8", "replace")
        facts["stage"] = "output"
    except subprocess.TimeoutExpired:
        facts["timed_out"] = True
    except Exception as exc:
        facts["exec_error"] = f"{type(exc).__name__}: {exc}"
        facts["stage"] = "tool_failure"
    return facts


def oracle_codings(facts: dict, pin: str) -> tuple[bool, bool]:
    """C1 (registered primary): whole stripped stdout == pin.
    C2 (second admissible normalization): first flag-shaped token == pin."""
    if facts["stage"] != "output" or facts["proc_rc"] != 0:
        return False, False
    out = facts["out"]
    c1 = out.strip() == pin
    m = FLAG_RE.search(out)
    c2 = bool(m and m.group(0) == pin)
    return c1, c2


def terminal_state(session: dict, last_text: str | None) -> str:
    if session.get("_provider_category"):
        return session["_provider_category"]
    if session.get("_harness_error"):
        return "HARNESS_ERROR"
    if session.get("_tool_failure"):
        return "TOOL_FAILURE"
    if session["accepted"]:
        return "SUCCESS"
    if session["final_timed_out"]:
        return "TIMEOUT"
    if session["submissions"] >= 1:
        # CRASH class (registered): the FINAL submitted program exited
        # non-zero; ORACLE_FAIL is a clean run that failed both codings.
        subs = [t for t in session["turn_records"]
                if t.get("submitted") and t.get("returncode") is not None]
        if subs and subs[-1]["returncode"] != 0:
            return "CRASH"
        return "ORACLE_FAIL"
    low = (last_text or "").lower()
    if any(marker in low for marker in REFUSAL_MARKERS):
        return "MODEL_REFUSAL"
    return "AGENT_GIVEUP"


def ledger_append(line: dict) -> None:
    ledger = Path("/mnt/nvme5/ACTS-Attack/sp2027/research_execution/BUDGET_LEDGER.jsonl")
    with ledger.open("a") as f:
        f.write(json.dumps(line, sort_keys=True) + "\n")


def build_plan(labels=None) -> list[tuple[str, str, str, int]]:
    labels = labels or LABELS
    return [(label, task, rep, seed)
            for label in labels for task in TASKS for rep in REPS for seed in SEEDS]


def main() -> int:
    dry_run = "--dry-run" in sys.argv[1:]
    substitute_for = None
    substitute_with = None
    args = sys.argv[1:]
    if "--substitute-for" in args:
        i = args.index("--substitute-for")
        substitute_for = args[i + 1]
        args = args[:i] + args[i + 2:]
    if "--substitute-with" in args:
        i = args.index("--substitute-with")
        substitute_with = args[i + 1]
        args = args[:i] + args[i + 2:]
    freeze, manifest, answers, _ = verify_frozen_inputs()

    plan_labels = list(LABELS)
    if substitute_for:
        if substitute_for not in LABELS:
            fail(f"substitute-for label not registered: {substitute_for}")
        if substitute_with not in SUBSTITUTE_ORDER or substitute_with == substitute_for:
            fail(f"substitute-with not in the registered substitution order "
                 f"or identical: {substitute_with}")
        plan_labels = [substitute_with if l == substitute_for else l
                       for l in LABELS]

    if dry_run:
        plan = build_plan(plan_labels)
        prefixes = {f"extadm_amend4__{label_slug(l)}__{t}__{r}__seed_{s}__"
                    for l, t, r, s in plan}
        if len(plan) != 168 or len(prefixes) != 168:
            fail(f"grid is not 168 unique slots: {len(plan)} / {len(prefixes)}")
        if not FREEZE_COMMIT.exists():
            commit_state = "PENDING (live mode will refuse until FREEZE_COMMIT.txt exists)"
        else:
            commit_state = FREEZE_COMMIT.read_text().strip()
        print(json.dumps({
            "dry_run": True,
            "status": "OK — no model call, no session created",
            "protocol": PROTOCOL,
            "labels": plan_labels,
            "substituted_for": substitute_for,
            "tasks": TASKS,
            "representations": REPS,
            "seeds": SEEDS,
            "sessions": len(plan),
            "max_tokens": MAX_TOKENS,
            "frozen_files_verified": len(freeze["files"]),
            "prompts_verified": len(manifest["instantiated_prompts"]),
            "oracle_tasks": len(answers),
            "oracle_codings": ["C1 whole-stdout == pin (primary)",
                               "C2 first flag-shaped token == pin"],
            "freeze_commit": commit_state,
        }, indent=2, sort_keys=True))
        return 0

    if not FREEZE_COMMIT.exists():
        fail("freeze commit marker FREEZE_COMMIT.txt missing — run the "
             "namespace-restricted freeze commit first")
    key = os.environ.get("AGENTROUTER_API_KEY", "").strip()
    if not key:
        fail("AGENTROUTER_API_KEY is not set in the process environment")

    sys.path.insert(0, str(HERE))
    from agentrouter_client import AgentRouterClient, ProviderFailure  # noqa: E402
    clients = {label: AgentRouterClient(key, label, BASE_URL,
                                        TEMP_BY_LABEL.get(label, TEMPERATURE))
               for label in plan_labels}

    for d in ("prompts", "raw_provider_responses", "events", "programs", "sandbox"):
        (SESS / d).mkdir(parents=True, exist_ok=True)

    results_path = HERE / "results.jsonl"
    done_prefixes = set()
    if results_path.exists():
        for line in results_path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                done_prefixes.add(
                    f"extadm_amend4__{label_slug(row['label'])}__{row['task_id']}__"
                    f"{row['representation']}__seed_{row['seed']}__")

    event_log = SESS / "events" / "events_amend4.jsonl"

    def event(run_id, kind, payload):
        with event_log.open("a") as f:
            f.write(json.dumps({"ts": time.time(), "run_id": run_id,
                                "kind": kind, **payload}, sort_keys=True) + "\n")

    cumulative_out_tokens = 0
    cumulative_in_tokens = 0
    consecutive_provider_fail = 0
    halted = False
    call_index = 0

    for label, task, rep, seed in build_plan(plan_labels):
        if halted:
            break
        slug = label_slug(label)
        prefix = f"extadm_amend4__{slug}__{task}__{rep}__seed_{seed}__"
        if prefix in done_prefixes:
            print(json.dumps({"skipped_already_recorded": [label, task, rep, seed]}),
                  flush=True)
            continue
        run_id = prefix + uuid.uuid4().hex[:12]

        prompt_template = (HERE / "fixtures" / "rt_transform" / task /
                           f"prompt_{rep}.txt").read_text()
        prompt_sha = sha_text(prompt_template)
        session = {
            "run_id": run_id, "protocol": PROTOCOL, "label": label,
            "model": label, "route": BASE_URL,
            "temperature": TEMP_BY_LABEL.get(label, TEMPERATURE),
            "task_id": task, "representation": rep, "seed": seed,
            "status": "INCOMPLETE", "turns": 0, "submissions": 0,
            "accepted": False, "accepted_c2": False, "final_timed_out": False,
            "prompt_sha256": prompt_sha,
            "oracle_answer_sha256": sha_text(answers[task]),
            "produced_model_content": False, "provider_attempts": 0,
            "programs": [], "turn_records": [],
        }

        workdir = SESS / "sandbox" / run_id
        workdir.mkdir(parents=True)
        for artifact in manifest["artifacts"][task]:
            name = artifact["name"]
            shutil.copyfile(HERE / "fixtures" / "tasks" / task / name, workdir / name)

        feedback = None
        last_text = None
        for turn in range(1, MAX_TURNS + 1):
            prompt = prompt_template if feedback is None else prompt_template + "\n\n" + feedback
            (SESS / "prompts" / f"{run_id}__turn{turn}.txt").write_text(prompt)
            event(run_id, "model_start", {
                "label": label, "task": task, "rep": rep, "seed": seed,
                "turn": turn, "prompt_sha256": sha_text(prompt),
                "base_prompt_sha256": prompt_sha, "provider_route": label})
            result = None
            for attempt in range(1, MAX_PROVIDER_REATTEMPTS + 2):
                session["provider_attempts"] += 1
                try:
                    result = clients[label].call(prompt, MAX_TOKENS)
                    break
                except ProviderFailure as exc:
                    if exc.category == "HARNESS_ERROR":
                        session["_harness_error"] = str(exc)[:300]
                        event(run_id, "harness_error", {
                            "turn": turn, "attempt": attempt,
                            "detail": str(exc)[:300]})
                        ledger_append({
                            "timestamp": time.strftime("%Y-%m-%d"),
                            "namespace": "external_admission_amend4_frontier_20261106",
                            "classification": "harness_error",
                            "protocol": PROTOCOL, "run_id": run_id,
                            "label": label, "task_id": task,
                            "representation": rep, "seed": seed, "turn": turn,
                            "attempt": attempt, "call_index": call_index + 1,
                            "model": label, "input_tokens": 0,
                            "output_tokens": 0,
                            "detail": str(exc)[:300],
                        })
                        break
                    classification = ("provider_failure_no_model_content"
                                      if not session["produced_model_content"]
                                      else "provider_failure_after_model_content")
                    event(run_id, "provider_failure", {
                        "label": label, "turn": turn, "attempt": attempt,
                        "category": exc.category,
                        "detail": str(exc)[:300],
                        "classification": classification})
                    ledger_append({
                        "timestamp": time.strftime("%Y-%m-%d"),
                        "namespace": "external_admission_amend4_frontier_20261106",
                        "classification": classification,
                        "protocol": PROTOCOL, "run_id": run_id,
                        "label": label, "task_id": task,
                        "representation": rep, "seed": seed, "turn": turn,
                        "attempt": attempt, "call_index": call_index + 1,
                        "model": label, "input_tokens": 0,
                        "output_tokens": 0,
                        "provider_failure_category": exc.category,
                    })
                    if attempt <= MAX_PROVIDER_REATTEMPTS:
                        continue
                    if not session["produced_model_content"]:
                        session["_provider_category"] = (
                            "TIMEOUT" if exc.category == "TIMEOUT"
                            else "PROVIDER_UNAVAILABLE")
                        session["provider_failure_detail"] = str(exc)[:300]
                    else:
                        session["provider_failure_after_content"] = str(exc)[:300]
                    break
            if result is None:
                break

            raw_path = SESS / "raw_provider_responses" / f"{run_id}__turn{turn}.json"
            raw_path.write_text(result["raw_body"])
            session["produced_model_content"] = True
            meta = dict(result["metadata"])
            meta.pop("output_text", None)
            event(run_id, "model_response", {
                "label": label, "turn": turn, "provider_metadata": meta,
                "raw_response_path": str(raw_path)})
            usage = result["metadata"].get("usage") or {}
            in_tok = int(usage.get("input_tokens", 0))
            out_tok = int(usage.get("output_tokens", 0))
            cumulative_in_tokens += in_tok
            cumulative_out_tokens += out_tok
            call_index += 1
            ledger_append({
                "timestamp": time.strftime("%Y-%m-%d"),
                "namespace": "external_admission_amend4_frontier_20261106",
                "classification": "experiment call",
                "protocol": PROTOCOL, "run_id": run_id,
                "label": label, "task_id": task,
                "representation": rep, "seed": seed, "turn": turn,
                "call_index": call_index, "model": label,
                "input_tokens": in_tok, "output_tokens": out_tok,
                "invoice_status": "token counts recorded; USD reconciled at settlement",
            })
            if cumulative_out_tokens > OUTPUT_TOKEN_CEILING:
                fail(f"phase output-token ceiling exceeded: {cumulative_out_tokens}")

            session["turns"] += 1
            last_text = result["text"]
            action = extract_action(result["text"])
            if not action:
                session["turn_records"].append(
                    {"turn": turn, "stage": "parse", "submitted": False,
                     "finish_reason": result["metadata"].get("finish_reason")})
                event(run_id, "action_parse_failed", {"turn": turn})
                feedback = FB_REJECT
                continue
            session["submissions"] += 1
            code = action["code"]
            prog_path = workdir / "prog.py"
            prog_path.write_text(code)
            prog_sha = sha_text(code)
            retained = SESS / "programs" / f"{run_id}__turn{turn}.py"
            shutil.copyfile(prog_path, retained)
            facts = run_program(prog_path, workdir)
            if facts["stage"] == "tool_failure":
                session["_tool_failure"] = True
                session["turn_records"].append(
                    {"turn": turn, "stage": "tool_failure",
                     "exec_error": facts["exec_error"], "submitted": True,
                     "accepted": False})
                event(run_id, "tool_failure", {"turn": turn,
                                               "detail": facts["exec_error"]})
                break
            c1, c2 = oracle_codings(facts, answers[task])
            record = {
                "turn": turn, "stage": facts["stage"],
                "returncode": facts["proc_rc"],
                "stdout_tail": facts["out"][-200:],
                "stderr_tail": facts["err"][-200:] if facts["err"] else "",
                "oracle_match": c1, "oracle_match_c2": c2,
                "timed_out": facts["timed_out"],
                "program_sha256": prog_sha,
                "retained_program_path": str(retained.relative_to(HERE)),
                "submitted": True, "accepted": c1,
                "finish_reason": result["metadata"].get("finish_reason"),
            }
            session["turn_records"].append(record)
            session["programs"].append({"turn": turn, "sha256": prog_sha,
                                        "path": str(retained.relative_to(HERE))})
            event(run_id, "execution_verdict", {
                "turn": turn, "verdict": "accepted" if c1 else "rejected",
                "verdict_c2": "accepted" if c2 else "rejected",
                "stage": facts["stage"], "timed_out": facts["timed_out"],
                "program_sha256": prog_sha})
            if c1:
                session["accepted"] = True
                session["accepted_turn"] = turn
                session["accepted_program_sha256"] = prog_sha
                session["oracle_verdict"] = "accepted_c1"
                break
            if c2:
                session["accepted_c2"] = True
                session["accepted_c2_turn"] = turn
                session["accepted_c2_program_sha256"] = prog_sha
            feedback = FB_REJECT
            session["final_timed_out"] = bool(facts["timed_out"])

        session["status"] = terminal_state(session, last_text)
        session["cumulative_output_tokens"] = cumulative_out_tokens
        session.pop("_provider_category", None)
        session.pop("_harness_error", None)
        session.pop("_tool_failure", None)
        with results_path.open("a") as f:
            f.write(json.dumps(session, sort_keys=True) + "\n")
        print(json.dumps({k: session.get(k) for k in
                          ("run_id", "label", "task_id", "representation", "seed",
                           "status", "turns", "submissions", "accepted",
                           "accepted_c2", "accepted_turn",
                           "produced_model_content")},
                         sort_keys=True), flush=True)

        if (session["status"] in ("PROVIDER_UNAVAILABLE", "TIMEOUT")
                and not session["produced_model_content"]):
            consecutive_provider_fail += 1
        else:
            consecutive_provider_fail = 0
        if session["status"] == "HARNESS_ERROR":
            halted = True
            print(json.dumps({"halted": True,
                              "reason": "harness/auth error"}), flush=True)
        if cumulative_out_tokens >= OUTPUT_TOKEN_CHECKPOINT and call_index % 50 == 0:
            print(json.dumps({"checkpoint_output_tokens": cumulative_out_tokens}),
                  flush=True)
        if consecutive_provider_fail >= CONSECUTIVE_PROVIDER_FAIL_HALT:
            halted = True
            print(json.dumps({"halted": True,
                              "reason": ">=3 consecutive provider-side pre-output failures"}),
                  flush=True)

    print(json.dumps({"cumulative_input_tokens": cumulative_in_tokens,
                      "cumulative_output_tokens": cumulative_out_tokens,
                      "experiment_calls": call_index, "halted": halted}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
