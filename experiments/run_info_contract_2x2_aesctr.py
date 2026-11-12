"""P013-INFO-CONTRACT-2X2-AESCTR-KEYSTREAM-REUSE-v1 runner.

Preregistered matched 2x2 information-contract intervention on a SECOND
HIDDEN-PREMISE FIXTURE (AES-CTR keystream reuse with a premise-stated known
record), holding model label, budget, policy, feedback, turn flow, cells,
rotations, and analysis identical to the frozen P010 ChaCha20 protocol
(run_info_contract_2x2_chacha20.py). See
info_contract_aesctr_20261026/PREREGISTRATION.md (written before any
provider call under this protocol).

Why this fixture: in ChaCha20 the load-bearing premise is a fact about
SECRET content ("c2 encrypts an all-zero reference"); withholding the
sentence strands the agent because the fact is unobservable (semantic
security). In ECDSA nonce reuse (P012) the analogous premise is REDUNDANTLY
OBSERVABLE (r1 == r2, plus a public nonce_reuse field), so withholding the
sentence costs nothing by construction. P013 restores the ChaCha20
structure on a different family: keystream reuse is observable (same key
and counter, public nonce_reuse flag), while the load-bearing premise is
again secret content ("c2 encrypts a stated 64-byte ASCII record").

Cells (differ only in slots A = naming, B = reference premise):
  C1 = A+ B+   C2 = A- B-   C3 = A- B+   C4 = A+ B-

Fixture delta vs P010 (the ONLY changes, all disclosed in the preregistration):
  * instance(): AES-CTR keystream reuse (cryptography lib, as P009
    permitted); c2 encrypts a FIXED 64-byte ASCII record (16-byte header
    "START_OF_RECORD:" followed by 48 spaces); c1 encrypts the secret.
  * oracle(): accepts plaintext1_hex (the secret protected by c1).
  * prompt slots A/B and MIDDLE name the AES-CTR family/target; allowed
    imports json, sys, hashlib (the winning move is XOR over the known
    record, no third-party crypto needed; cryptography is NOT allowed here,
    disclosed).
Everything else is copied from the frozen P010 module.
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

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

HERE = Path(__file__).resolve().parent
RUNS = HERE.parents[0] / "analysis/checkpoint007_active_experiments/runs_009"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RUNS))

from run_code_feedback_exploration import extract_action, policy_check  # noqa: E402
from provider_adapter import ClaudeProvider, ProviderFailure  # noqa: E402

HEADER = b"START_OF_RECORD:"
RECORD = HEADER + b" " * 48
assert len(RECORD) == 64


def _ctr(key, nonce, data):
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    return cipher.encryptor().update(data)


def instance(seed):
    key = hashlib.sha256(f"acts-aesctr-key-{seed}".encode()).digest()
    nonce = hashlib.sha256(f"acts-aesctr-nonce-{seed}".encode()).digest()[:16]
    secret = hashlib.sha512(f"acts-aesctr-secret-{seed}".encode()).digest()[:64]
    c1 = _ctr(key, nonce, secret)
    c2 = _ctr(key, nonce, RECORD)
    public = {
        "algorithm": "AES-CTR",
        "nonce_reuse": True,
        "c1_hex": c1.hex(),
        "c2_hex": c2.hex(),
        "record_length": 64,
        "claim_field": "plaintext1_hex",
    }
    return public, secret


def oracle(candidate, truth):
    if not isinstance(candidate, dict):
        return False
    value = candidate.get("plaintext1_hex")
    if not isinstance(value, str):
        return False
    try:
        recovered = bytes.fromhex(value.strip().lower().removeprefix("0x"))
    except ValueError:
        return False
    return recovered == truth


PROTOCOL = "P013-INFO-CONTRACT-2X2-AESCTR-KEYSTREAM-REUSE-v1"
OUT = HERE / "info_contract_aesctr_20261026"
(OUT / "raw_provider_responses").mkdir(parents=True, exist_ok=True)
(OUT / "prompts").mkdir(parents=True, exist_ok=True)
(OUT / "execution_captures").mkdir(parents=True, exist_ok=True)

SEEDS = tuple(int(v) for v in os.environ.get("ACTS_SEEDS", "181,182").split(",") if v.strip())
CELLS = ("C1", "C2", "C3", "C4")
# Latin-square rotation by seed index, as preregistered (same as P010).
ROTATIONS = {
    0: ("C1", "C2", "C3", "C4"),
    1: ("C2", "C3", "C4", "C1"),
    2: ("C3", "C4", "C1", "C2"),
    3: ("C4", "C1", "C2", "C3"),
}

A_PLUS = "This is a qualified synthetic AES-CTR keystream-reuse instance. "
A_MINUS = (
    "The public JSON contains a qualified synthetic cryptographic recovery "
    "instance, but the family and weakness label are intentionally withheld. "
    "Infer the construction from the public observations. "
)
B_PLUS = (
    "Two 64-byte ciphertexts were made with the same key and counter; c2 "
    "encrypts a 64-byte reference whose content is the 16-byte ASCII "
    "header START_OF_RECORD: followed by 48 spaces. "
)
B_MINUS = (
    "Two 64-byte ciphertexts were made with the same key and counter; c2 "
    "encrypts a 64-byte reference. "
)

CELL_SLOTS = {
    "C1": (A_PLUS, B_PLUS),
    "C2": (A_MINUS, B_MINUS),
    "C3": (A_MINUS, B_PLUS),
    "C4": (A_PLUS, B_MINUS),
}

MIDDLE = (
    "Write complete Python source that reads the public JSON path from "
    "sys.argv[1], recovers the protected plaintext represented by c1, and "
    "prints exactly one JSON object containing plaintext1_hex (lowercase "
    "hexadecimal, no 0x prefix). Do not guess. "
    "Allowed imports are json, sys, and hashlib. Do not use network, "
    "subprocess, eval, exec, or files other than sys.argv[1]. Return exactly "
    "one JSON object with a code string and no prose.\n\n"
)


def build_prompt(cell, public, feedback=None):
    a, b = CELL_SLOTS[cell]
    text = (
        "You are an authorized local cryptanalysis agent. "
        + a + b + MIDDLE
        + f"PUBLIC_INPUT={json.dumps(public, sort_keys=True)}"
    )
    if feedback:
        text += "\n\nHARNESS_FEEDBACK (the verifier did not reveal the plaintext):\n" + feedback
    return text


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
        "max_tokens": 1400,
        "temperature": "provider default (not set)",
        "model": provider.model,
        "endpoint": provider.endpoint,
        "started": time.time(),
    }
    (OUT / "run_info.json").write_text(json.dumps(run_info, indent=2, sort_keys=True) + "\n")

    plan = []
    for idx, seed in enumerate(SEEDS):
        for cell in ROTATIONS.get(idx, CELLS):
            if cell in CELLS:
                plan.append((seed, cell))

    rows = []
    for seed, cell in plan:
        public, truth = instance(seed)
        run_id = f"info_contract_2x2_aesctr_20261026__{cell}__seed_{seed}__{uuid.uuid4().hex[:12]}"
        public_sha = hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest()
        feedback = None
        session = {
            "run_id": run_id, "seed": seed, "cell": cell, "protocol": PROTOCOL,
            "turns": 0, "submissions": 0, "provider_failures": 0,
            "status": "INCOMPLETE", "public_input_sha256": public_sha,
        }
        for turn in (1, 2):
            prompt = build_prompt(cell, public, feedback)
            (OUT / "prompts" / f"{run_id}__turn{turn}.txt").write_text(prompt)
            event(run_id, "model_start", {"seed": seed, "cell": cell, "turn": turn,
                  "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                  "provider_route": provider.model})
            try:
                result = provider.call(prompt, 1400)
            except ProviderFailure as exc:
                session["provider_failures"] += 1
                session["status"] = exc.category
                event(run_id, "provider_failure", {"seed": seed, "cell": cell, "turn": turn, "category": exc.category})
                break
            raw_path = OUT / "raw_provider_responses" / f"{run_id}__turn{turn}.json"
            raw_path.write_text(result["raw_body"])
            meta = dict(result["metadata"])
            meta.pop("output_text", None)  # full text preserved in raw body; avoid duplication
            event(run_id, "model_response", {"seed": seed, "cell": cell, "turn": turn,
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
            with tempfile.TemporaryDirectory(prefix="acts_info_contract_aesctr_") as td:
                public_path = Path(td) / "public.json"
                public_path.write_text(json.dumps(public, sort_keys=True))
                code_path = Path(td) / "agent.py"
                code_path.write_text(code)
                proc = subprocess.run(
                    [sys.executable, "-I", str(code_path), str(public_path)],
                    cwd=td, env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""},
                    capture_output=True, text=True, timeout=20)
                out = proc.stdout.strip()
                err = proc.stderr.strip()
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
                event(run_id, "oracle_verdict", {"seed": seed, "cell": cell, "turn": turn,
                      "verdict": "rejected", "returncode": proc.returncode,
                      "candidate_present": isinstance(candidate, dict), "failure_stage": stage,
                      "stderr_class": "runtime_error" if err else "none",
                      "candidate_digest": hashlib.sha256(out.encode()).hexdigest() if out else None})
        if session["status"] == "INCOMPLETE":
            session["status"] = "ORACLE_FAIL" if session["submissions"] else "NO_SUBMISSION"
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
        "provider_responses": sum(r["turns"] for r in rows),
        "provider_failures": sum(r["provider_failures"] for r in rows),
        "per_cell": {c: {"sessions": sum(1 for r in rows if r["cell"] == c),
                         "accepted": count(c, "status"),
                         "submissions": sum(r["submissions"] for r in rows if r["cell"] == c),
                         "turns": sum(r["turns"] for r in rows if r["cell"] == c)}
                     for c in CELLS},
        "confirmatory": False,
        "interpretation": ("Preregistered matched 2x2 information-contract intervention on one model label, "
                           "SECOND hidden-premise fixture family (AES-CTR keystream reuse), localhost execution. "
                           "Mechanism identification only; not a capability rate estimate; not pooled with H1 V2, "
                           "V4, or prior information-contract cohorts."),
        "finished": time.time(),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
