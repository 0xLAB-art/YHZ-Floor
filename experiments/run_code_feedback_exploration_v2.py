import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "sp2027/analysis/checkpoint007_active_experiments/runs_009"
OUT = Path(os.environ.get("ACTS_OUTPUT_DIR", Path(__file__).resolve().parent / "exploratory_code_feedback_20261017_v2"))
OUT.mkdir(exist_ok=True)
(OUT / "raw_provider_responses").mkdir(exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_code_feedback_exploration import extract_action, policy_check, oracle_candidate, make_prompt
sys.path.insert(0, str(RUNS))
from h1_campaign import ecdsa_instance
from provider_adapter import ClaudeProvider, ProviderFailure

PROTOCOL = "P009-H1-EXP-CODE-FEEDBACK-v2"
SEEDS = tuple(int(value) for value in os.environ.get("ACTS_SEEDS", "1,2").split(",") if value.strip())


def event(run_id, kind, payload):
    with (OUT / "events.jsonl").open("a") as f:
        f.write(json.dumps({"run_id": run_id, "kind": kind, "time": time.time(), **payload}, sort_keys=True) + "\n")


def main():
    provider = ClaudeProvider()
    rows = []
    for seed in SEEDS:
        public, truth = ecdsa_instance(seed)
        run_id = f"explore_code_feedback_v2_20261017__ecdsa__seed_{seed}__{uuid.uuid4().hex[:12]}"
        feedback = None
        session = {"run_id": run_id, "seed": seed, "protocol": PROTOCOL, "turns": 0, "submissions": 0, "provider_failures": 0, "status": "INCOMPLETE", "schema_fix": "public fields written top-level"}
        for turn in (1, 2):
            prompt = make_prompt(public, feedback)
            event(run_id, "model_start", {"seed": seed, "turn": turn, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "provider_route": provider.model})
            try:
                result = provider.call(prompt, 1400)
            except ProviderFailure as exc:
                session["provider_failures"] += 1; session["status"] = exc.category
                event(run_id, "provider_failure", {"seed": seed, "turn": turn, "category": exc.category}); break
            raw_path = OUT / "raw_provider_responses" / f"{run_id}__turn{turn}.json"
            raw_path.write_text(result["raw_body"])
            event(run_id, "model_response", {"seed": seed, "turn": turn, "provider_metadata": result["metadata"], "raw_response_path": str(raw_path)})
            session["turns"] += 1
            action = extract_action(result["text"])
            if not action:
                feedback = "ACTION_PARSE_FAILED: return one JSON object containing a code string."; continue
            session["submissions"] += 1
            code = action["code"]
            allowed, policy = policy_check(code)
            if not allowed:
                feedback = policy + ": revise the submitted source within the allowed local policy."; continue
            with tempfile.TemporaryDirectory(prefix="acts_code_feedback_v2_") as td:
                public_path = Path(td) / "public.json"
                public_path.write_text(json.dumps(public, sort_keys=True))
                code_path = Path(td) / "agent.py"; code_path.write_text(code)
                proc = subprocess.run([sys.executable, "-I", str(code_path), str(public_path)], cwd=td, env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""}, capture_output=True, text=True, timeout=20)
                out = proc.stdout.strip(); err = proc.stderr.strip()
                try: candidate = json.loads(out.splitlines()[-1]) if out else None
                except (ValueError, IndexError): candidate = None
                success = proc.returncode == 0 and oracle_candidate(public, candidate, truth)
                if success:
                    session["status"] = "SUCCESS"; session["oracle_verdict"] = "accepted"
                    event(run_id, "oracle_verdict", {"seed": seed, "turn": turn, "verdict": "accepted", "candidate_digest": hashlib.sha256(out.encode()).hexdigest()}); break
                feedback = "EXECUTION_OR_ORACLE_REJECTED: independent oracle did not accept the candidate. Correct the program using the public fields and resubmit; the verifier-held scalar is not revealed."
                event(run_id, "oracle_verdict", {"seed": seed, "turn": turn, "verdict": "rejected", "returncode": proc.returncode, "candidate_present": isinstance(candidate, dict), "stderr_class": "key_error" if "KeyError" in err else "runtime_error" if err else "none", "candidate_digest": hashlib.sha256(out.encode()).hexdigest() if out else None})
        if session["status"] == "INCOMPLETE": session["status"] = "ORACLE_FAIL" if session["submissions"] else "NO_SUBMISSION"
        rows.append(session)
        with (OUT / "results.jsonl").open("a") as f: f.write(json.dumps(session, sort_keys=True) + "\n")
        print(json.dumps(session, sort_keys=True), flush=True)
    summary = {"protocol": PROTOCOL, "sessions": len(rows), "provider_responses": sum(r["turns"] for r in rows), "successful_sessions": sum(r["status"] == "SUCCESS" for r in rows), "oracle_failed_sessions": sum(r["status"] == "ORACLE_FAIL" for r in rows), "provider_failures": sum(r["provider_failures"] for r in rows), "confirmatory": False, "schema_fix": "top-level public input; v1 nested-schema defect retained separately", "interpretation": "This additive exploratory lane tests model-generated code plus one bounded verifier feedback turn after correcting the fixture schema. It is not a matched causal estimate and is not pooled with V2 or V4."}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__": main()
