#!/usr/bin/env python3
"""Harness for the modern-AEAD cohorts (P019 ChaCha20-Poly1305, P020 AES-GCM-SIV).

Usage: python3 run_modern_aead_cohort.py <cohort-dir>

One cohort per process, one registration per cohort. Everything that can leak
into a cell denominator is pinned before the first provider call:

  * this harness's own SHA-256 (self-hash, asserted at launch);
  * `fixtures_aead_modern.py` SHA-256 (the fixture code is under test, so it is
    pinned separately from the harness);
  * the transport adapter SHA-256 and its token floor;
  * the protocol string, label and seed list from `_REGISTRATION.json`.

The sandbox, event schema, status taxonomy, oracle pattern and resume rule are
the same as `run_info_contract_2x2_aesgcm.py` (P014/P016/P017), so a row from
this harness is directly comparable to a row from that one. The only intended
differences are the fixture family and the registered seeds.

Provider failures are terminal per session: never retried, never imputed.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "analysis/checkpoint007_active_experiments/runs_009"))

from run_code_feedback_exploration import extract_action, policy_check  # noqa: E402

CELLS = ("C1", "C2", "C3", "C4")
ROTATIONS = {
    0: ("C1", "C2", "C3", "C4"),
    1: ("C2", "C3", "C4", "C1"),
    2: ("C3", "C4", "C1", "C2"),
    3: ("C4", "C1", "C2", "C3"),
}
RUNNER_MAX_TOKENS = 1400
SANDBOX_TIMEOUT = 20


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_provider(reg):
    adapter = HERE / reg["adapter"]
    got = sha(adapter)
    if got != reg["adapter_sha256"]:
        raise SystemExit(f"ADAPTER HASH MISMATCH: {got} != {reg['adapter_sha256']}")
    spec = importlib.util.spec_from_file_location("provider_adapter", adapter)
    injected = importlib.util.module_from_spec(spec)
    sys.modules["provider_adapter"] = injected
    spec.loader.exec_module(injected)
    if not hasattr(injected, "ClaudeProvider") or not hasattr(injected, "ProviderFailure"):
        raise SystemExit("injected adapter missing ClaudeProvider/ProviderFailure")
    if int(getattr(injected, "P017_TOKEN_FLOOR", 0)) != reg["token_floor"]:
        raise SystemExit("adapter floor does not match the registered floor")
    return injected


def event(out, run_id, kind, payload):
    with (out / "events.jsonl").open("a") as f:
        f.write(json.dumps({"run_id": run_id, "kind": kind, "time": time.time(), **payload},
                           sort_keys=True) + "\n")


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: run_modern_aead_cohort.py <cohort-dir>")
    out = Path(argv[1]).resolve()
    reg = json.loads((out / "_REGISTRATION.json").read_text())

    # Self-hash: the harness is registered too, so a silent edit cannot run.
    got = sha(HERE / "run_modern_aead_cohort.py")
    if got != reg["runner_sha256"]:
        raise SystemExit(f"RUNNER SELF-HASH MISMATCH: {got} != {reg['runner_sha256']}")
    fixtures = HERE / "fixtures_aead_modern.py"
    fx_sha = sha(fixtures)
    if fx_sha != reg["fixtures_sha256"]:
        raise SystemExit(f"FIXTURE HASH MISMATCH: {fx_sha} != {reg['fixtures_sha256']}")

    spec = importlib.util.spec_from_file_location("fixtures_aead_modern", fixtures)
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)

    family = reg["fixture"]
    if family not in fx.FAMILIES:
        raise SystemExit(f"unregistered fixture {family!r}")
    label = reg["label"]
    os.environ["AGENTROUTER_LABEL_MODEL"] = label

    injected = load_provider(reg)
    Framed = injected
    provider = Framed.ClaudeProvider()
    if not hasattr(fx, "instance") or not hasattr(fx, "oracle"):
        raise SystemExit("fixture module missing instance/oracle")

    for sub in ("raw_provider_responses", "prompts", "execution_captures"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    seeds = tuple(int(v) for v in reg["seeds"])
    launch = {
        "protocol": reg["protocol"],
        "namespace": str(out.relative_to(HERE)),
        "model_label": provider.model,
        "route": "agentrouter",
        "endpoint_host": provider.endpoint.split("//")[-1].split("/")[0],
        "fixture": family,
        "fixture_name": fx.FAMILIES[family]["name"],
        "keystream_exposed": fx.FAMILIES[family]["keystream_exposed"],
        "runner_sha256": got,
        "fixtures_sha256": fx_sha,
        "adapter_sha256": reg["adapter_sha256"],
        "token_floor": int(injected.P017_TOKEN_FLOOR),
        "seeds": list(seeds),
        "seed_receipt": reg.get("seed_receipt"),
        "seeds_registered_sha256": reg.get("seeds_sha256"),
        "sessions_registered": 4 * len(seeds),
        "started": time.time(),
    }
    (out / "_LAUNCH.json").write_text(json.dumps(launch, indent=2, sort_keys=True) + "\n")
    print(json.dumps(launch, indent=2, sort_keys=True), flush=True)

    # Resume rule: a seed is complete only when all four cells have a row.
    if (out / "results.jsonl").exists():
        recorded = {}
        for line in (out / "results.jsonl").read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                recorded.setdefault(rec["seed"], set()).add(rec["cell"])
        complete = {s for s, cells in recorded.items() if cells >= set(CELLS)}
        if complete:
            seeds = tuple(s for s in seeds if s not in complete)
            (out / "resume_note.json").write_text(json.dumps(
                {"skipped_complete_seeds": sorted(complete), "seeds_to_run": list(seeds)},
                indent=1, sort_keys=True) + "\n")

    plan = []
    for idx, seed in enumerate(seeds):
        for cell in ROTATIONS.get(idx, CELLS):
            plan.append((seed, cell))

    rows = []
    for seed, cell in plan:
        public, truth = fx.instance(family, seed)
        run_id = f"{reg['protocol'].split('-v')[0].lower()}__{cell}__seed_{seed}__{uuid.uuid4().hex[:12]}"
        public_sha = hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest()
        feedback = None
        session = {
            "run_id": run_id, "seed": seed, "cell": cell, "protocol": reg["protocol"],
            "fixture": family, "turns": 0, "submissions": 0, "provider_failures": 0,
            "status": "INCOMPLETE", "public_input_sha256": public_sha,
        }
        for turn in (1, 2):
            prompt = fx.build_prompt(family, cell, public, feedback)
            (out / "prompts" / f"{run_id}__turn{turn}.txt").write_text(prompt)
            event(out, run_id, "model_start", {
                "seed": seed, "cell": cell, "turn": turn,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "provider_route": provider.model})
            try:
                result = provider.call(prompt, RUNNER_MAX_TOKENS)
            except Framed.ProviderFailure as exc:
                session["provider_failures"] += 1
                session["status"] = exc.category
                event(out, run_id, "provider_failure",
                      {"seed": seed, "cell": cell, "turn": turn, "category": exc.category})
                break
            raw_path = out / "raw_provider_responses" / f"{run_id}__turn{turn}.json"
            raw_path.write_text(result["raw_body"])
            meta = dict(result["metadata"])
            meta.pop("output_text", None)
            event(out, run_id, "model_response", {
                "seed": seed, "cell": cell, "turn": turn,
                "provider_metadata": meta, "raw_response_path": str(raw_path)})
            session["turns"] += 1
            action = extract_action(result["text"])
            if not action:
                feedback = "ACTION_PARSE_FAILED: return one JSON object containing a code string."
                continue
            session["submissions"] += 1
            code = action["code"]
            allowed, policy = policy_check(code)
            if not allowed:
                feedback = policy + ": revise the submitted source within the allowed local policy."
                continue
            with tempfile.TemporaryDirectory(prefix="acts_modern_aead_") as td:
                public_path = Path(td) / "public.json"
                public_path.write_text(json.dumps(public, sort_keys=True))
                code_path = Path(td) / "agent.py"
                code_path.write_text(code)
                proc = subprocess.run(
                    [sys.executable, "-I", str(code_path), str(public_path)],
                    cwd=td, env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""},
                    capture_output=True, text=True, timeout=SANDBOX_TIMEOUT)
                stdout, stderr = proc.stdout.strip(), proc.stderr.strip()
                cap = out / "execution_captures" / f"{run_id}__turn{turn}"
                cap.with_suffix(".stdout.txt").write_text(stdout + "\n")
                Path(str(cap) + ".stderr.txt").write_text(stderr + "\n")
                Path(str(cap) + ".returncode.txt").write_text(str(proc.returncode) + "\n")
                Path(str(cap) + ".agent.py").write_text(code)
                try:
                    candidate = json.loads(stdout.splitlines()[-1]) if stdout else None
                except (ValueError, IndexError):
                    candidate = None
                if proc.returncode == 0 and fx.oracle(candidate, truth):
                    session["status"] = "SUCCESS"
                    session["oracle_verdict"] = "accepted"
                    event(out, run_id, "oracle_verdict", {
                        "seed": seed, "cell": cell, "turn": turn, "verdict": "accepted",
                        "candidate_digest": hashlib.sha256(stdout.encode()).hexdigest()})
                    break
                feedback = ("EXECUTION_OR_ORACLE_REJECTED: the independent oracle did not accept "
                            "the candidate. Correct the program using only the public fields and "
                            "resubmit; the verifier-held plaintext is not revealed.")
                stage = ("parse" if candidate is None else
                         "execution" if proc.returncode != 0 else "oracle")
                event(out, run_id, "oracle_verdict", {
                    "seed": seed, "cell": cell, "turn": turn, "verdict": "rejected",
                    "returncode": proc.returncode,
                    "candidate_present": isinstance(candidate, dict), "failure_stage": stage,
                    "stderr_class": "runtime_error" if stderr else "none",
                    "candidate_digest": hashlib.sha256(stdout.encode()).hexdigest() if stdout else None})
        if session["status"] == "INCOMPLETE":
            session["status"] = "ORACLE_FAIL" if session["submissions"] else "NO_SUBMISSION"
        rows.append(session)
        with (out / "results.jsonl").open("a") as f:
            f.write(json.dumps(session, sort_keys=True) + "\n")
        print(json.dumps(session, sort_keys=True), flush=True)

    def count(cell):
        return sum(1 for r in rows if r["cell"] == cell and r["status"] == "SUCCESS")

    summary = {
        "protocol": reg["protocol"],
        "preregistered": True,
        "fixture": family,
        "keystream_exposed": fx.FAMILIES[family]["keystream_exposed"],
        "sessions": len(rows),
        "provider_responses": sum(r["turns"] for r in rows),
        "provider_failures": sum(r["provider_failures"] for r in rows),
        "per_cell": {c: {"sessions": sum(1 for r in rows if r["cell"] == c),
                         "accepted": count(c),
                         "submissions": sum(r["submissions"] for r in rows if r["cell"] == c),
                         "turns": sum(r["turns"] for r in rows if r["cell"] == c)}
                     for c in CELLS},
        "confirmatory": False,
        "finished": time.time(),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
