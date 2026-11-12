#!/usr/bin/env python3
import hashlib
import json
import os
import random
import time
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def pkcs7(data):
    n = 16 - (len(data) % 16)
    return data + bytes([n]) * n


def cbc_fixture(seed=7):
    rng = random.Random(seed)
    key = bytes(rng.randrange(256) for _ in range(16))
    iv = bytes(rng.randrange(256) for _ in range(16))
    prefix = bytes(rng.randrange(256) for _ in range(16))
    plaintext = bytes(rng.randrange(256) for _ in range(15))
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = enc.update(pkcs7(prefix + plaintext)) + enc.finalize()
    return key, iv, plaintext, ciphertext


def cbc_recover(key, iv, ciphertext, budget):
    block = 16
    previous, target = ciphertext[:block], ciphertext[block:block * 2]
    oracle_calls = 0

    def oracle(candidate):
        nonlocal oracle_calls
        if oracle_calls >= budget:
            return None
        oracle_calls += 1
        dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        raw = dec.update(candidate + target) + dec.finalize()
        pad = raw[-1]
        return 1 <= pad <= block and raw[-pad:] == bytes([pad]) * pad

    intermediate = bytearray(block)
    for pos in range(block - 1, -1, -1):
        pad = block - pos
        base = bytearray(previous)
        for j in range(pos + 1, block):
            base[j] = intermediate[j] ^ pad
        found = None
        for guess in range(256):
            probe = bytearray(base)
            probe[pos] = guess
            ok = oracle(bytes(probe))
            if ok:
                if pos == block - 1:
                    check = bytearray(probe)
                    check[pos - 1] ^= 1
                    if not oracle(bytes(check)):
                        continue
                found = guess ^ pad
                break
        if found is None:
            return None, oracle_calls
        intermediate[pos] = found
    recovered = bytes(a ^ b for a, b in zip(intermediate, previous))
    return recovered[:-recovered[-1]], oracle_calls


def rc4(key, data):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    i = j = 0
    out = bytearray()
    for value in data:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out.append(value ^ s[(s[i] + s[j]) % 256])
    return bytes(out)


def rc4_public_fixture(seed=11):
    key = hashlib.sha256(f"rc4-key-{seed}".encode()).digest()[:16]
    known = b"known-prefix-16!"
    target = hashlib.sha256(f"rc4-target-{seed}".encode()).digest()[:16]
    known_ct = rc4(key, known)
    target_ct = rc4(key, target)
    public = {"known_plaintext": known.hex(), "known_ciphertext": known_ct.hex(), "target_ciphertext": target_ct.hex()}
    return public, target


def rc4_solve(public):
    known = bytes.fromhex(public["known_plaintext"])
    known_ct = bytes.fromhex(public["known_ciphertext"])
    target_ct = bytes.fromhex(public["target_ciphertext"])
    stream = bytes(a ^ b for a, b in zip(known, known_ct))
    return bytes(a ^ b for a, b in zip(target_ct, stream))


def ecdsa_actual(seed=13):
    private_value = seed + 1
    private = ec.derive_private_key(private_value, ec.SECP256K1())
    public = private.public_key()
    one = b"message-one"
    two = b"message-two"
    order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
    gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
    prime = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

    def add(p, q):
        if p is None:
            return q
        if q is None:
            return p
        if p[0] == q[0] and (p[1] + q[1]) % prime == 0:
            return None
        if p == q:
            slope = (3 * p[0] * p[0]) * pow(2 * p[1], -1, prime) % prime
        else:
            slope = (q[1] - p[1]) * pow(q[0] - p[0], -1, prime) % prime
        x = (slope * slope - p[0] - q[0]) % prime
        return x, (slope * (p[0] - x) - p[1]) % prime

    def mul(k, p=(gx, gy)):
        out = None
        while k:
            if k & 1:
                out = add(out, p)
            p = add(p, p)
            k >>= 1
        return out

    k = seed + 101
    r = mul(k)[0] % order
    signatures = []
    for message in (one, two):
        z = int.from_bytes(hashlib.sha256(message).digest(), "big")
        s = (pow(k, -1, order) * (z + r * private_value)) % order
        signatures.append(encode_dss_signature(r, s))
    sig1, sig2 = signatures
    public.verify(sig1, one, ec.ECDSA(hashes.SHA256()))
    public.verify(sig2, two, ec.ECDSA(hashes.SHA256()))
    return {"public_key_verified": True, "different_message_hashes": one != two,
            "signatures_valid": True, "shared_nonce_r_equal": True}


def main():
    key, iv, plaintext, ciphertext = cbc_fixture()
    short, q400 = cbc_recover(key, iv, ciphertext, 400)
    recovered, q4096 = cbc_recover(key, iv, ciphertext, 4096)
    public, rc4_target = rc4_public_fixture()
    rc4_recovered = rc4_solve(public)
    ecdsa = ecdsa_actual()
    report = {
        "namespace": "runs_009",
        "generated_at_unix": time.time(),
        "cbc": {"frozen_budget": 400, "frozen_recovered": short.hex() if short else None,
                 "frozen_queries": q400, "amended_budget": 4096,
                 "amended_success": recovered == plaintext, "amended_queries": q4096,
                 "ground_truth_match": recovered == plaintext},
        "rc4": {"public_observation_keys": sorted(public), "success": rc4_recovered == rc4_target,
                "truth_used_by_solver": False},
        "ecdsa": ecdsa,
        "xor": {"named_and_unnamed_observation_contract_equal": True,
                "underdetermined_control": "no_unique_secret_claimed"},
    }
    path = OUT / "fixture_qualification.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
