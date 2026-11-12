"""Build PROMPT_HASHES.json + FREEZE.json for P011-INFO-CONTRACT-2X2-RC4-v1.

Run AFTER PREREGISTRATION.md is written and BEFORE the first experimental
provider call. FREEZE.json carries the SHA-256 of every prompt/fixture/policy
file (preregistration, all phase code, per-cell prompt templates with the
PUBLIC_INPUT placeholder, per-(seed,cell) turn-1 prompts, policy constants).
Turn-2 prompts depend on observed feedback and are hashed at session time in
events.jsonl (prespecified in PREREGISTRATION.md section 9).
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rc4_fixture import (  # noqa: E402
    CELLS, CLAIM_FIELD, NONCE, PROTOCOL, REFERENCE, ROTATIONS, SEEDS,
    build_prompt, instance,
)

FROZEN_CODE_FILES = [
    "PREREGISTRATION.md",
    "provider_client.py",
    "rc4_fixture.py",
    "auth_smoke.py",
    "preflight_rc4_2x2.py",
    "run_info_contract_2x2_rc4.py",
    "analysis_info_contract_2x2_rc4.py",
    "leakscan_info_contract_2x2_rc4.py",
    "PROMPT_HASHES.json",
]

POLICY = {
    "allowed_imports": ["json", "sys", "hashlib", "cryptography"],
    "forbidden_calls": ["eval", "exec", "__import__"],
    "forbidden_behaviors": ["network", "subprocess", "files other than sys.argv[1]"],
    "execution_command": "python -I agent.py public.json (bare temp dir)",
    "execution_timeout_s": 20,
    "provider_call_timeout_s": 300,
    "max_tokens": 1400,
    "temperature": "provider default (not set)",
    "turn_cap": 2,
}


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    # per-cell templates (PUBLIC_INPUT placeholder) and per-(seed,cell) turn-1 prompts
    dummy = {"dummy": 1}
    template_hashes = {}
    for cell in CELLS:
        text = build_prompt(cell, dummy)
        template = text.replace(f"PUBLIC_INPUT={json.dumps(dummy, sort_keys=True)}", "PUBLIC_INPUT={PUBLIC}")
        template_hashes[cell] = hashlib.sha256(template.encode()).hexdigest()

    turn1_prompt_hashes = {}
    for idx, seed in enumerate(SEEDS):
        public, _truth = instance(seed)
        for cell in ROTATIONS[idx]:
            prompt = build_prompt(cell, public)
            turn1_prompt_hashes[f"seed_{seed}__{cell}"] = hashlib.sha256(prompt.encode()).hexdigest()

    prompt_hashes = {
        "protocol": PROTOCOL,
        "note": "SHA-256 over the full prompt text as sent (template + concrete PUBLIC_INPUT). "
                "Turn-2 prompts include observed feedback and are hashed at session time in events.jsonl.",
        "template_sha256": template_hashes,
        "turn1_prompt_sha256": turn1_prompt_hashes,
        "prompt_prefix_sha256": hashlib.sha256(b"You are an authorized local cryptanalysis agent. ").hexdigest(),
    }
    (HERE / "PROMPT_HASHES.json").write_text(json.dumps(prompt_hashes, indent=2, sort_keys=True) + "\n")

    code_hashes = {}
    missing = []
    for name in FROZEN_CODE_FILES:
        p = HERE / name
        if p.is_file():
            code_hashes[name] = sha_file(p)
        else:
            missing.append(name)
    if missing:
        print("MISSING FROZEN FILES:", missing)
        return 1

    freeze = {
        "protocol": PROTOCOL,
        "freeze_type": "PREREGISTRATION_FREEZE",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rule": "Committed before the first experimental provider call of this protocol. "
                "The AUTH_SMOKE health probe (preflight/auth_smoke_*.json) predates this commit "
                "and is non-evidence by classification.",
        "code_and_policy_files_sha256": code_hashes,
        "prompt_templates_sha256": template_hashes,
        "prompt_hashes_file": {"path": "PROMPT_HASHES.json", "sha256": code_hashes["PROMPT_HASHES.json"]},
        "policy": POLICY,
        "fixture_constants": {
            "algorithm": "RC4",
            "reference_const_hex": REFERENCE.hex(),
            "reference_const_note": "fixed 32-byte reference constant, identical for every seed",
            "nonce_const": NONCE.decode(),
            "nonce_const_note": "P009/P010 fixed nonce constant; RC4(k, nonce, m) := RC4(k || nonce, m)",
            "protected_length": 32,
            "claim_field": CLAIM_FIELD,
            "key_derivation": "key = SHA-256('acts-rc4-key-{seed}')[:16]; target = SHA-256('acts-rc4-secret-{seed}')",
        },
        "seeds": list(SEEDS),
        "cells": list(CELLS),
        "rotations": {str(k): list(v) for k, v in ROTATIONS.items()},
        "sessions_planned": 16,
        "max_provider_calls_experiment": 32,
        "provider": {
            "endpoint": "https://api.apmix.ai/v1/messages",
            "model_label": "claude-sonnet-4-6-free",
            "identity": "provider-attested route label only; no hosted-weight identity claimed",
            "key_handling": "APMIX_API_KEY read from repo-root .env at runtime; never printed, never written to any sp2027/ artifact",
        },
        "budget": {
            "phase_ceiling_usd": 5.0,
            "projected_worst_case_usd": 0.75,
            "projection_basis": "32 experiment calls x (~750 input + 1400 output tokens) at USD 3/M in + 15/M out",
            "project_guardrails": {"alert_usd": 50, "hard_stop_usd": 200},
        },
        "terminal_state_enum": ["SUCCESS", "ORACLE_FAIL", "TIMEOUT", "AGENT_GIVEUP", "MODEL_REFUSAL",
                                "TOOL_FAILURE", "PROVIDER_UNAVAILABLE", "HARNESS_ERROR"],
        "halt_rule": "3 consecutive PROVIDER_UNAVAILABLE sessions halt the phase; all records retained; no retries",
        "self_exclusion_note": "build_freeze.py and FREEZE.json do not hash themselves; "
                               "FINAL_FREEZE.json at completion names the post-run manifest hash",
    }
    (HERE / "FREEZE.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"written": ["PROMPT_HASHES.json", "FREEZE.json"],
                      "code_files_hashed": len(code_hashes)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
