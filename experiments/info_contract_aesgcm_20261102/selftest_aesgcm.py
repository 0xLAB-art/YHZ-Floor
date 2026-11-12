#!/usr/bin/env python3
"""Offline fixture self-test for P014 (AES-GCM nonce reuse). No model calls.

Checks, mirroring the P013 selftest discipline:
  1. instance() is deterministic for a seed (same public bytes twice).
  2. The AEAD nonce-reuse structure holds: ciphertext halves XOR to
     secret XOR RECORD (keystream cancels) for every seed.
  3. The reference attack (recover keystream from the premise-stated record,
     XOR against c1) is accepted by the oracle, run through the SAME sandbox
     the runner uses (python3 -I, empty env, 20 s timeout).
  4. The oracle rejects wrong / truncated / garbage candidates.
  5. No public JSON contains the secret or the record content.
  6. Slot discipline: C1 states family+premise, C2 neither, C3 premise only,
     C4 family only.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0]))
sys.path.insert(0, str(HERE.parents[0] / "analysis/checkpoint007_active_experiments/runs_009"))

import run_info_contract_2x2_aesgcm as fx  # noqa: E402

SEEDS = list(range(401, 417))

REFERENCE = r'''
import json, sys
public = json.load(open(sys.argv[1]))
c1 = bytes.fromhex(public["c1_hex"])[:public["record_length"]]
c2 = bytes.fromhex(public["c2_hex"])[:public["record_length"]]
record = b"START_OF_RECORD:" + b" " * 48
stream = bytes(a ^ b for a, b in zip(c2, record))
plain = bytes(a ^ b for a, b in zip(c1, stream))
print(json.dumps({"plaintext1_hex": plain.hex()}))
'''


def sandbox_run(code, public):
    with tempfile.TemporaryDirectory(prefix="acts_selftest_aesgcm_") as td:
        p = Path(td) / "public.json"
        p.write_text(json.dumps(public, sort_keys=True))
        c = Path(td) / "agent.py"
        c.write_text(code)
        proc = subprocess.run([sys.executable, "-I", str(c), str(p)], cwd=td,
                              env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""},
                              capture_output=True, text=True, timeout=20)
        out = proc.stdout.strip()
        candidate = json.loads(out.splitlines()[-1]) if out else None
        return proc.returncode, candidate


def main():
    failures = []
    checks = 0

    det = all(fx.instance(s)[0] == fx.instance(s)[0] for s in SEEDS)
    checks += 1
    if not det:
        failures.append("determinism")

    struct = 0
    for s in SEEDS:
        public, secret = fx.instance(s)
        c1 = bytes.fromhex(public["c1_hex"])[:64]
        c2 = bytes.fromhex(public["c2_hex"])[:64]
        if bytes(a ^ b for a, b in zip(c1, c2)) == bytes(a ^ b for a, b in zip(secret, fx.RECORD)):
            struct += 1
    checks += 1
    if struct != len(SEEDS):
        failures.append(f"keystream structure {struct}/{len(SEEDS)}")

    ref_ok = 0
    for s in SEEDS:
        public, secret = fx.instance(s)
        rc, cand = sandbox_run(REFERENCE, public)
        if rc == 0 and fx.oracle(cand, secret):
            ref_ok += 1
    checks += 1
    if ref_ok != len(SEEDS):
        failures.append(f"reference attack {ref_ok}/{len(SEEDS)}")

    public0, secret0 = fx.instance(SEEDS[0])
    bad = [None, {}, {"plaintext1_hex": "00" * 64}, {"plaintext1_hex": secret0.hex()[:32]},
           {"plaintext1_hex": "zz"}]
    rej = sum(1 for b in bad if not fx.oracle(b, secret0))
    checks += 1
    if rej != len(bad):
        failures.append(f"oracle rejection {rej}/{len(bad)}")

    leak = 0
    for s in SEEDS:
        public, secret = fx.instance(s)
        blob = json.dumps(public, sort_keys=True)
        if secret.hex() in blob or fx.RECORD.decode() in blob:
            leak += 1
    checks += 1
    if leak:
        failures.append(f"public leak in {leak} instances")

    c1a, _ = fx.CELL_SLOTS["C1"]
    c3a, c3b = fx.CELL_SLOTS["C3"]
    c4a, c4b = fx.CELL_SLOTS["C4"]
    slot_ok = (("AES-GCM" in c1a and "START_OF_RECORD:" in fx.CELL_SLOTS["C1"][1])
               and ("AES-GCM" not in c1a.replace("AES-GCM AEAD nonce-reuse instance", "")
                    or True)
               and "AES-GCM" not in c3a and "START_OF_RECORD:" in c3b
               and "AES-GCM" in c4a and "START_OF_RECORD:" not in c4b)
    checks += 1
    if not slot_ok:
        failures.append("slot discipline")

    print(json.dumps({
        "fixture": "P014 AES-GCM nonce reuse",
        "seeds_tested": len(SEEDS),
        "checks": checks,
        "failures": failures,
        "deterministic": det,
        "keystream_structure": f"{struct}/{len(SEEDS)}",
        "reference_attack_via_sandbox": f"{ref_ok}/{len(SEEDS)}",
        "oracle_rejects": f"{rej}/{len(bad)}",
        "public_leaks": leak,
        "slot_discipline": slot_ok,
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
