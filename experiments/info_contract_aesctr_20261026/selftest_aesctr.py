#!/usr/bin/env python3
"""P013 preflight self-test — NO provider calls.

Verifies, on seeds 181-196 (16/16), BEFORE any provider call under
P013-INFO-CONTRACT-2X2-AESCTR-KEYSTREAM-REUSE-v1:

  1. determinism: instance(seed) is identical on repeated calls;
  2. keystream-reuse structure: c1 XOR c2 == secret XOR RECORD;
  3. reference attack (recover keystream from the premise-stated reference,
     XOR against c1) is accepted by the oracle (16/16), executed through the
     SAME sandbox the runner uses (python3 -I, empty env, 20 s timeout);
  4. oracle rejects wrong/truncated/garbage candidates (16/16);
  5. extract_action + policy_check accept a reference-style program;
  6. slot discipline: C1 prompt contains the premise content and the family
     name; C2 contains neither; C3 contains the premise content but not the
     family name; C4 contains the family name but not the premise content.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[0]
sys.path.insert(0, str(ROOT))

import run_info_contract_2x2_aesctr as mod  # noqa: E402

SEEDS = list(range(181, 197))

REFERENCE_CODE = """import json, sys
pub = json.load(open(sys.argv[1]))
c1 = bytes.fromhex(pub["c1_hex"])
c2 = bytes.fromhex(pub["c2_hex"])
record = b"START_OF_RECORD:" + b" " * 48
keystream = bytes(a ^ b for a, b in zip(c2, record))
p1 = bytes(a ^ b for a, b in zip(c1, keystream))
print(json.dumps({"plaintext1_hex": p1.hex()}))
"""


def main():
    counts = {"determinism": 0, "structure": 0, "reference_attack": 0,
              "oracle_rejects": 0, "action_policy": 0, "slots": 0}
    for seed in SEEDS:
        public, secret = mod.instance(seed)
        public2, secret2 = mod.instance(seed)
        if public == public2 and secret == secret2:
            counts["determinism"] += 1
        c1 = bytes.fromhex(public["c1_hex"])
        c2 = bytes.fromhex(public["c2_hex"])
        if bytes(a ^ b for a, b in zip(c1, c2)) == bytes(a ^ b for a, b in zip(secret, mod.RECORD)):
            counts["structure"] += 1
        # Reference attack through the SAME sandbox semantics as the runner.
        keystream = bytes(a ^ b for a, b in zip(c2, mod.RECORD))
        p1 = bytes(a ^ b for a, b in zip(c1, keystream))
        assert p1 == secret
        with tempfile.TemporaryDirectory(prefix="acts_p013_selftest_") as td:
            pub_path = Path(td) / "public.json"
            pub_path.write_text(json.dumps(public, sort_keys=True))
            code_path = Path(td) / "agent.py"
            code_path.write_text(REFERENCE_CODE)
            proc = subprocess.run(
                [sys.executable, "-I", str(code_path), str(pub_path)],
                cwd=td, env={"PATH": "", "PYTHONPATH": ""},
                capture_output=True, text=True, timeout=20)
            candidate = None
            if proc.returncode == 0 and proc.stdout.strip():
                try:
                    candidate = json.loads(proc.stdout.strip().splitlines()[-1])
                except (ValueError, IndexError):
                    candidate = None
            if proc.returncode == 0 and mod.oracle(candidate, secret):
                counts["reference_attack"] += 1
        # Oracle rejections: wrong bytes, truncated, invalid hex, wrong type.
        rejects = [
            {"plaintext1_hex": (secret[:-1] + bytes([secret[-1] ^ 1])).hex()},
            {"plaintext1_hex": secret[:32].hex()},
            {"plaintext1_hex": "zz"},
            {"plaintext1_hex": 12345},
            {"other_field": secret.hex()},
            "not-a-dict",
        ]
        if all(mod.oracle(cand, secret) is False for cand in rejects):
            counts["oracle_rejects"] += 1
    # extract_action + policy_check accept the reference-style program.
    fake_response = '```json\n{"code": ' + json.dumps(REFERENCE_CODE) + "\n}\n```"
    action = mod.extract_action(fake_response)
    if action:
        allowed, _policy = mod.policy_check(action["code"])
        if allowed:
            counts["action_policy"] += 1
    # Slot discipline on all four cells.
    slots_ok = True
    for seed in SEEDS[:1]:
        public, seed_secret = mod.instance(seed)
        secret_hex = seed_secret.hex()
        prompts = {c: mod.build_prompt(c, public) for c in ("C1", "C2", "C3", "C4")}
        fam = lambda t: "AES-CTR keystream-reuse instance" in t  # noqa: E731
        prem = lambda t: "START_OF_RECORD:" in t  # noqa: E731
        slots_ok &= fam(prompts["C1"]) and prem(prompts["C1"])
        slots_ok &= (not fam(prompts["C2"])) and (not prem(prompts["C2"]))
        slots_ok &= (not fam(prompts["C3"])) and prem(prompts["C3"])
        slots_ok &= fam(prompts["C4"]) and (not prem(prompts["C4"]))
        # Public JSON never leaks the secret or the record content.
        blob = json.dumps(public, sort_keys=True)
        slots_ok &= secret_hex not in blob and "START_OF_RECORD" not in blob
    if slots_ok:
        counts["slots"] += 1

    n = len(SEEDS)
    verdict = "PASS" if all(v == (n if k in ("determinism", "structure",
                                             "reference_attack", "oracle_rejects") else 1)
                            for k, v in counts.items()) else "FAIL"
    print(json.dumps({"verdict": verdict, "seeds": n, "counts": counts}, indent=1, sort_keys=True))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
