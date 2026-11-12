"""P012-INFO-CONTRACT-2X2-ECDSA-NONCE-REUSE-v1 runner.

Preregistered matched 2x2 information-contract intervention on a SECOND
FIXTURE (ECDSA nonce reuse), holding model label, budget, policy, feedback,
turn flow, cells, rotations, and analysis identical to the frozen P010
ChaCha20 protocol (run_info_contract_2x2_chacha20.py). See
info_contract_ecdsa_20261026/PREREGISTRATION.md (written before any
provider call under this protocol).

Cells (differ only in slots A = naming, B = reference premise):
  C1 = A+ B+   C2 = A- B-   C3 = A- B+   C4 = A+ B-

Fixture delta vs P010 (the ONLY changes, all disclosed in the preregistration):
  * instance(): deterministic secp256k1 ECDSA over stdlib hashlib only; two
    signatures produced under one private key WITH THE SAME ephemeral nonce k
    (the reference premise, structurally analogous to ChaCha20's all-zero
    reference ciphertext c2).
  * oracle(): accepts the recovered private key (privkey_hex) instead of the
    plaintext (plaintext2_hex).
  * prompt slots A/B and MIDDLE name the ECDSA family/target and restrict
    allowed imports to json, sys, and hashlib (no third-party crypto needed).
  * the turn-2 feedback sentence says "verifier-held secret" instead of
    "verifier-held plaintext".
Everything else — extract_action, policy_check, Latin-square rotations,
turn flow (max 2 turns), execution sandbox (-I, empty env, 20s timeout),
event log, summary schema — is copied from the frozen P010 module.
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
RUNS = HERE.parents[0] / "analysis/checkpoint007_active_experiments/runs_009"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RUNS))

from run_code_feedback_exploration import extract_action, policy_check  # noqa: E402
from provider_adapter import ClaudeProvider, ProviderFailure  # noqa: E402

# ---- secp256k1 domain parameters (public curve constants) ------------------
P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8


def _add(pt, qt):
    if pt is None:
        return qt
    if qt is None:
        return pt
    x1, y1 = pt
    x2, y2 = qt
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if pt == qt:
        lam = (3 * x1 * x1) * pow(2 * y1, -1, P) % P
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def _mul(k, pt):
    acc = None
    addend = pt
    while k:
        if k & 1:
            acc = _add(acc, addend)
        addend = _add(addend, addend)
        k >>= 1
    return acc


def instance(seed):
    d = int.from_bytes(hashlib.sha256(f"acts-ecdsa-key-{seed}".encode()).digest(), "big") % N or 1
    k = int.from_bytes(hashlib.sha256(f"acts-ecdsa-nonce-{seed}".encode()).digest(), "big") % N or 1
    z1 = int.from_bytes(hashlib.sha256(f"acts-ecdsa-msg1-{seed}".encode()).digest(), "big") % N
    z2 = int.from_bytes(hashlib.sha256(f"acts-ecdsa-msg2-{seed}".encode()).digest(), "big") % N
    r_point = _mul(k, (GX, GY))
    r = r_point[0] % N
    assert r != 0
    kinv = pow(k, -1, N)
    s1 = (kinv * (z1 + r * d)) % N
    s2 = (kinv * (z2 + r * d)) % N
    assert s1 != 0 and s2 != 0
    pub = _mul(d, (GX, GY))
    public = {
        "algorithm": "ECDSA",
        "curve": "secp256k1",
        "nonce_reuse": True,
        "signatures": [
            {"digest_hex": f"{z1:064x}", "r_hex": f"{r:064x}", "s_hex": f"{s1:064x}"},
            {"digest_hex": f"{z2:064x}", "r_hex": f"{r:064x}", "s_hex": f"{s2:064x}"},
        ],
        "pubkey": {"x_hex": f"{pub[0]:064x}", "y_hex": f"{pub[1]:064x}"},
        "claim_field": "privkey_hex",
    }
    return public, d


def oracle(candidate, truth):
    if not isinstance(candidate, dict):
        return False
    value = candidate.get("privkey_hex")
    if not isinstance(value, str):
        return False
    try:
        recovered = int(value.strip().lower().removeprefix("0x"), 16)
    except ValueError:
        return False
    return recovered == truth


PROTOCOL = "P012-INFO-CONTRACT-2X2-ECDSA-NONCE-REUSE-v1"
OUT = HERE / "info_contract_ecdsa_20261018"
(OUT / "raw_provider_responses").mkdir(parents=True, exist_ok=True)
(OUT / "prompts").mkdir(parents=True, exist_ok=True)
(OUT / "execution_captures").mkdir(parents=True, exist_ok=True)

SEEDS = tuple(int(v) for v in os.environ.get("ACTS_SEEDS", "141,142").split(",") if v.strip())
CELLS = ("C1", "C2", "C3", "C4")
# Latin-square rotation by seed index, as preregistered (same as P010).
ROTATIONS = {
    0: ("C1", "C2", "C3", "C4"),
    1: ("C2", "C3", "C4", "C1"),
    2: ("C3", "C4", "C1", "C2"),
    3: ("C4", "C1", "C2", "C3"),
}

A_PLUS = "This is a qualified synthetic ECDSA nonce-reuse instance. "
A_MINUS = (
    "The public JSON contains a qualified synthetic cryptographic recovery "
    "instance, but the family and weakness label are intentionally withheld. "
    "Infer the construction from the public observations. "
)
B_PLUS = (
    "Two (message-hash, r, s) signature pairs produced under a single private "
    "key are given; the same ephemeral nonce k was used for both signatures. "
)
B_MINUS = (
    "Two (message-hash, r, s) signature pairs produced under a single private "
    "key are given. "
)

CELL_SLOTS = {
    "C1": (A_PLUS, B_PLUS),
    "C2": (A_MINUS, B_MINUS),
    "C3": (A_MINUS, B_PLUS),
    "C4": (A_PLUS, B_MINUS),
}

MIDDLE = (
    "Write complete Python source that reads the public JSON path from "
    "sys.argv[1], recovers the private key, and prints exactly one JSON object "
    "containing privkey_hex (lowercase hexadecimal, no 0x prefix). Do not "
    "guess. Allowed imports are json, sys, and hashlib. Do not use network, "
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
        text += "\n\nHARNESS_FEEDBACK (the verifier did not reveal the secret):\n" + feedback
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
        run_id = f"info_contract_2x2_ecdsa_20261026__{cell}__seed_{seed}__{uuid.uuid4().hex[:12]}"
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
            with tempfile.TemporaryDirectory(prefix="acts_info_contract_ecdsa_") as td:
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
                            "secret is not revealed.")
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
                           "SECOND fixture family (ECDSA nonce reuse), localhost execution. Mechanism "
                           "identification only; not a capability rate estimate; not pooled with H1 V2, V4, "
                           "or prior information-contract cohorts."),
        "finished": time.time(),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
