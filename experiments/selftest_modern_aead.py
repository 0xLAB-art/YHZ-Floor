#!/usr/bin/env python3
"""Offline self-test for the modern-AEAD fixtures. No model calls, no network.

For ChaCha20-Poly1305 the fixture must be *solvable* by the P014 reference
attack; for AES-GCM-SIV it must be *unsolvable* by that attack. Both directions
are asserted here, through the same sandbox the harness uses, before any
provider call is made.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fixtures_aead_modern as fx  # noqa: E402

SEEDS = list(range(1, 9))

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


def sandbox(code, public):
    with tempfile.TemporaryDirectory(prefix="acts_selftest_modern_") as td:
        p = Path(td) / "public.json"
        p.write_text(json.dumps(public, sort_keys=True))
        c = Path(td) / "agent.py"
        c.write_text(code)
        proc = subprocess.run([sys.executable, "-I", str(c), str(p)], cwd=td,
                              env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""},
                              capture_output=True, text=True, timeout=20)
        out = proc.stdout.strip()
        try:
            cand = json.loads(out.splitlines()[-1]) if out else None
        except (ValueError, IndexError):
            cand = None
        return proc.returncode, cand


def main():
    failures = []
    report = {}

    # 1. determinism, both families
    det = all(fx.instance(fam, s)[0] == fx.instance(fam, s)[0]
              for fam in fx.FAMILIES for s in SEEDS)
    if not det:
        failures.append("determinism")
    report["deterministic"] = det

    # 2. keystream structure: true for chacha, false for siv
    for fam in ("chacha20poly1305", "aesgcmsiv"):
        hits = 0
        for s in SEEDS:
            public, secret = fx.instance(fam, s)
            c1 = bytes.fromhex(public["c1_hex"])[:64]
            c2 = bytes.fromhex(public["c2_hex"])[:64]
            if bytes(a ^ b for a, b in zip(c1, c2)) == bytes(a ^ b for a, b in zip(secret, fx.RECORD)):
                hits += 1
        expected = fx.FAMILIES[fam]["keystream_exposed"]
        got = hits == len(SEEDS)
        report[f"{fam}_keystream_reuse"] = f"{hits}/{len(SEEDS)}"
        if got != expected:
            failures.append(f"{fam} keystream expectation")

    # 3. reference attack: must succeed on chacha, must fail on siv
    for fam, want in (("chacha20poly1305", True), ("aesgcmsiv", False)):
        ok = 0
        for s in SEEDS:
            public, secret = fx.instance(fam, s)
            rc, cand = sandbox(REFERENCE, public)
            if rc == 0 and fx.oracle(cand, secret):
                ok += 1
        report[f"{fam}_reference_accepted"] = f"{ok}/{len(SEEDS)}"
        if (ok == len(SEEDS)) != want:
            failures.append(f"{fam} reference attack expectation")

    # 4. SIV determinism under reuse: same plaintext must give the same ciphertext
    key = __import__("hashlib").sha256(b"acts-aesgcmsiv-1-key").digest()
    nonce = __import__("hashlib").sha256(b"acts-aesgcmsiv-1-nonce").digest()[:12]
    from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
    a = AESGCMSIV(key)
    report["siv_same_plaintext_same_ciphertext"] = (
        a.encrypt(nonce, fx.RECORD, None) == a.encrypt(nonce, fx.RECORD, None))

    # 5. oracle rejects garbage
    public0, secret0 = fx.instance("chacha20poly1305", SEEDS[0])
    bad = [None, {}, {"plaintext1_hex": "00" * 64},
           {"plaintext1_hex": secret0.hex()[:32]}, {"plaintext1_hex": "zz"}]
    rej = sum(1 for b in bad if not fx.oracle(b, secret0))
    report["oracle_rejects"] = f"{rej}/{len(bad)}"
    if rej != len(bad):
        failures.append("oracle rejection")

    # 6. no public leak
    leaks = 0
    for fam in fx.FAMILIES:
        for s in SEEDS:
            public, secret = fx.instance(fam, s)
            blob = json.dumps(public, sort_keys=True)
            if secret.hex() in blob or fx.RECORD.decode() in blob:
                leaks += 1
    report["public_leaks"] = leaks
    if leaks:
        failures.append("public leak")

    # 7. slot discipline: A names (or withholds) the family, B states (or withholds) the premise
    for fam, meta in fx.FAMILIES.items():
        slots = fx.slot_text(fam)
        c1a, c1b = slots["C1"]
        c2a, c2b = slots["C2"]
        c3a, c3b = slots["C3"]
        c4a, c4b = slots["C4"]
        ok = (meta["name"] in c1a and "START_OF_RECORD:" in c1b
              and meta["name"] not in c2a and "START_OF_RECORD:" not in c2b
              and meta["name"] not in c3a and "START_OF_RECORD:" in c3b
              and meta["name"] in c4a and "START_OF_RECORD:" not in c4b)
        report[f"{fam}_slot_discipline"] = ok
        if not ok:
            failures.append(f"{fam} slot discipline")

    report["fixtures_sha256"] = __import__("hashlib").sha256(
        (HERE / "fixtures_aead_modern.py").read_bytes()).hexdigest()
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
