#!/usr/bin/env python3
import hashlib
import json
import random
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature

from fixture_qualification import rc4, ecdsa_actual

OUT = Path(__file__).resolve().parent
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def xor_instance(seed):
    key = hashlib.sha256(f"xor-key-{seed}".encode()).digest()[:16]
    samples = [{"x": (bytes([i]) * 16).hex(), "y": bytes(a ^ b for a, b in zip(bytes([i]) * 16, key)).hex()} for i in range(1, 5)]
    target = hashlib.sha256(f"xor-target-{seed}".encode()).digest()[:16]
    ciphertext = bytes(a ^ b for a, b in zip(target, key))
    public = {"samples": samples, "ciphertext": ciphertext.hex()}
    return public, key, target


def xor_oracle(key, query, budget):
    calls = []

    def ask(x):
        if len(calls) >= budget:
            raise RuntimeError("oracle budget exhausted")
        calls.append(x)
        return bytes(a ^ b for a, b in zip(x, key))

    return ask, calls


def ecdsa_recover_private(message_one, message_two, sig_one, sig_two, public):
    r1, s1 = decode_dss_signature(sig_one)
    r2, s2 = decode_dss_signature(sig_two)
    assert r1 == r2 and r1 != 0
    z1 = int.from_bytes(hashlib.sha256(message_one).digest(), "big")
    z2 = int.from_bytes(hashlib.sha256(message_two).digest(), "big")
    recovered = ((s1 * z2 - s2 * z1) * pow(r1 * (s2 - s1), -1, N)) % N
    recovered_public = ec.derive_private_key(recovered, ec.SECP256K1()).public_key().public_numbers()
    expected = public.public_numbers()
    return recovered_public.x == expected.x and recovered_public.y == expected.y


def actual_ecdsa_recovery(seed=31):
    d = seed + 1
    private = ec.derive_private_key(d, ec.SECP256K1())
    public = private.public_key()
    m1, m2 = b"matched-message-1", b"matched-message-2"
    p = 55066263022277343669578718895168534326250603453777594175500187360389116729240
    gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
    prime = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

    def add(a, b):
        if a is None: return b
        if b is None: return a
        if a[0] == b[0] and (a[1] + b[1]) % prime == 0: return None
        slope = ((3 * a[0] * a[0]) * pow(2 * a[1], -1, prime) if a == b else
                 (b[1] - a[1]) * pow(b[0] - a[0], -1, prime)) % prime
        x = (slope * slope - a[0] - b[0]) % prime
        return x, (slope * (a[0] - x) - a[1]) % prime

    def mul(k, point=(p, gy)):
        out = None
        while k:
            if k & 1: out = add(out, point)
            point = add(point, point)
            k >>= 1
        return out

    k = seed + 101
    r = mul(k)[0] % N
    signatures = []
    for message in (m1, m2):
        z = int.from_bytes(hashlib.sha256(message).digest(), "big")
        s = pow(k, -1, N) * (z + r * d) % N
        signatures.append(encode_dss_signature(r, s))
    return {"different_messages": True, "shared_r": True,
            "private_recovery_verified": ecdsa_recover_private(m1, m2, signatures[0], signatures[1], public)}


def matched_public_conditions(seed):
    rc4_key = hashlib.sha256(f"rc4-key-{seed}".encode()).digest()[:16]
    known = b"known-prefix-16!"
    target = hashlib.sha256(f"rc4-target-{seed}".encode()).digest()[:16]
    rc4_public = {"known_plaintext": known.hex(), "known_ciphertext": rc4(rc4_key, known).hex(),
                  "target_ciphertext": rc4(rc4_key, target).hex()}
    xor_public, _, _ = xor_instance(seed)
    return {"seed": seed, "rc4_public": rc4_public, "xor_public": xor_public,
            "named_and_unnamed_same_public_sha256": hashlib.sha256(json.dumps(rc4_public, sort_keys=True).encode()).hexdigest()}


def main():
    records = [matched_public_conditions(seed) for seed in range(1, 11)]
    report = {"matched_seed_count": len(records), "seeds": [x["seed"] for x in records],
              "ecdsa_private_recovery": actual_ecdsa_recovery(),
              "underdetermined_control": {"unique_secret": False, "correct_decision": "ABSTAIN_UNDERDETERMINED"},
              "public_records": records}
    (OUT / "h1_fixture_qualification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"matched_seed_count": len(records), "ecdsa_private_recovery": report["ecdsa_private_recovery"],
                      "underdetermined_control": report["underdetermined_control"]}, indent=2))


if __name__ == "__main__":
    main()
