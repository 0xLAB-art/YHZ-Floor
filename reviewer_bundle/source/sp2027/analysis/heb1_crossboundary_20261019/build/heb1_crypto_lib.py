#!/usr/bin/env python3
"""HEB-1 build-time key-material helpers (used ONLY by the fixtures generator).

Deterministic, offline. NOT imported by any validator or the adjudicator.
Produces, for one case tag, a target state plus a correct and a faulty
candidate (ECDSA nonce reuse and ChaCha20 keystream reuse).
"""
from __future__ import annotations
import random

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (55066263022277343669578718895168534326250603453777594175500187360389116729240,
     32670510020758816978083085130507043184471273380659243275938904335757337482424)


def inv(x: int, m: int) -> int:
    return pow(x % m, -1, m)


def point_add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    x1, y1 = a
    x2, y2 = b
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if a == b:
        lam = (3 * x1 * x1) * inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * inv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return x3, (lam * (x1 - x3) - y1) % P


def scalar_mul(k: int, point=G):
    out = None
    cur = point
    k %= N
    while k:
        if k & 1:
            out = point_add(out, cur)
        cur = point_add(cur, cur)
        k >>= 1
    return out


def _rng(cid: str, tag: str) -> random.Random:
    return random.Random(f"heb1|{cid}|{tag}")


def ecdsa_material(cid: str, tag: str):
    """Two signatures sharing nonce k; returns (target, good, bad)."""
    rng = _rng(cid, tag)
    while True:
        d = rng.randrange(2, N)
        k = rng.randrange(2, N)
        rp = scalar_mul(k)
        if rp is None:
            continue
        r = rp[0] % N
        if r == 0:
            continue
        z1 = rng.randrange(2, N)
        z2 = rng.randrange(2, N)
        s1 = inv(k, N) * (z1 + r * d) % N
        s2 = inv(k, N) * (z2 + r * d) % N
        if s1 == 0 or s2 == 0 or s1 == s2:
            continue
        break
    q = scalar_mul(d)
    target = {
        "curve": "secp256k1",
        "public_key": [hex(q[0]), hex(q[1])],
        "signature_1": {"r": hex(r), "s": hex(s1), "z": hex(z1)},
        "signature_2": {"r": hex(r), "s": hex(s2), "z": hex(z2)},
    }
    good = {"d": hex(d), "k": hex(k)}
    bad = {"d": hex(d ^ 1), "k": hex(k)}
    return target, good, bad


def chacha_material(cid: str, tag: str):
    """One key/nonce reused for two messages; returns (target, good, bad)."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
    rng = _rng(cid, tag)
    key = bytes(rng.randrange(256) for _ in range(32))
    nonce = bytes(rng.randrange(256) for _ in range(16))
    p1 = bytes(rng.randrange(256) for _ in range(48))
    p2 = bytes(rng.randrange(256) for _ in range(48))

    def stream(pt: bytes) -> bytes:
        enc = Cipher(algorithms.ChaCha20(key, nonce), mode=None).encryptor()
        return enc.update(pt)

    c1, c2 = stream(p1), stream(p2)
    target = {
        "cipher": "chacha20-keystream-reuse",
        "ciphertext_1": c1.hex(),
        "ciphertext_2": c2.hex(),
        "known_plaintext_1": p1.hex(),
    }
    good = {"plaintext_2": p2.hex()}
    bad = {"plaintext_2": (bytes([p2[0] ^ 1]) + p2[1:]).hex()}
    return target, good, bad


def keymaterial(cid: str, prim: str, tag: str):
    if prim == "ecdsa":
        return ecdsa_material(cid, tag)
    if prim == "chacha":
        return chacha_material(cid, tag)
    raise ValueError(f"unknown primitive {prim!r}")
