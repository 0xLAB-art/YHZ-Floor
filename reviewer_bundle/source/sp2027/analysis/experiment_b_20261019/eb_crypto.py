#!/usr/bin/env python3
"""Experiment B — independent cryptographic primitives.

Self-contained ECDSA (secp256k1, nonce reuse) and ChaCha20 (keystream reuse)
implementations written from the public specifications for the Experiment B
evaluation. Stdlib only. No imports from the frozen HEB-1 or stage01 code.

Truth semantics used throughout:
  * cryptographic correctness is recomputed from the private target state by the
    experiment's reference adjudicator; it is never taken from a validator or a
    declared field;
  * a candidate is "cryptographically correct" iff it recovers the target's
    private material used by the corresponding predicate.

Candidate formats (JSON, deterministic):
  * ECDSA:   {"recovered_private_key": "<64 hex chars>"}
  * ChaCha20:{"recovered_plaintext":  "<hex of the unknown plaintext>"}
"""
from __future__ import annotations

import hashlib
import json

# ---------------------------------------------------------------------------
# secp256k1 domain parameters
# ---------------------------------------------------------------------------
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (GX, GY)


def _inv(a: int, m: int) -> int:
    return pow(a, m - 2, m)


def point_add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p == q:
        lam = (3 * x1 * x1) * _inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * _inv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return (x3, (lam * (x1 - x3) - y1) % P)


def point_mul(k: int, p):
    r = None
    while k:
        if k & 1:
            r = point_add(r, p)
        p = point_add(p, p)
        k >>= 1
    return r


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _stream(seed: bytes, tag: str, n: int) -> bytes:
    out = b""
    ctr = 0
    while len(out) < n:
        out += sha256(b"eb-crypto|" + seed + b"|" + tag.encode() + b"|" + str(ctr).encode())
        ctr += 1
    return out[:n]


def _as_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


# ---------------------------------------------------------------------------
# ECDSA nonce reuse
# ---------------------------------------------------------------------------
def ecdsa_make(seed: bytes) -> dict:
    """Deterministic instance: same nonce k used for two distinct messages."""
    d = (_as_int(_stream(seed, "d", 32)) % (N - 1)) + 1
    k = (_as_int(_stream(seed, "k", 32)) % (N - 1)) + 1
    e1 = _as_int(_stream(seed, "e1", 32)) % N
    e2 = _as_int(_stream(seed, "e2", 32)) % N
    if e1 == e2:
        e2 = (e2 + 1) % N
    Q = point_mul(d, G)
    x = point_mul(k, G)[0] % N
    r = x
    s1 = (_inv(k, N) * (e1 + r * d)) % N
    s2 = (_inv(k, N) * (e2 + r * d)) % N
    return {
        "primitive": "ecdsa-nonce-reuse",
        "private_d": d,
        "k": k,
        "Q": {"x": Q[0], "y": Q[1]},
        "r": r,
        "s1": s1,
        "s2": s2,
        "e1": e1,
        "e2": e2,
    }


def ecdsa_public_target(inst: dict) -> dict:
    return {
        "primitive": inst["primitive"],
        "curve": "secp256k1",
        "public_key": {"x": "%064x" % inst["Q"]["x"], "y": "%064x" % inst["Q"]["y"]},
        "signature1": {"r": "%064x" % inst["r"], "s": "%064x" % inst["s1"], "e": "%064x" % inst["e1"]},
        "signature2": {"r": "%064x" % inst["r"], "s": "%064x" % inst["s2"], "e": "%064x" % inst["e2"]},
        "note": "two signatures sharing the same nonce r",
    }


def ecdsa_expected_instance_d(inst: dict) -> int:
    """Truth recomputation (private side): recovered d from the two signatures.

    Pure nonce-reuse algebra, checked against the stored private d.
    """
    r, s1, s2, e1, e2 = inst["r"], inst["s1"], inst["s2"], inst["e1"], inst["e2"]
    k = ((e1 - e2) * _inv((s1 - s2) % N, N)) % N
    d = ((s1 * k - e1) * _inv(r, N)) % N
    if k != inst["k"] or d != inst["private_d"]:
        raise AssertionError("instance algebra inconsistent")
    return d


def ecdsa_predicate(inst: dict, candidate: object) -> tuple[bool, dict]:
    """Independent recomputation: does candidate recover the private key?"""
    details = {"kind": "ecdsa-nonce-reuse", "expected_matches": False, "candidate_valid": False}
    if not isinstance(candidate, dict):
        return False, details
    hexd = candidate.get("recovered_private_key")
    if not isinstance(hexd, str) or len(hexd) != 64:
        return False, details
    try:
        cand = int(hexd, 16)
    except ValueError:
        return False, details
    expected = ecdsa_expected_instance_d(inst)
    details["candidate_valid"] = (point_mul(cand, G) is not None) and 1 <= cand < N
    details["expected_matches"] = (cand == expected)
    details["public_key_matches"] = (point_mul(cand, G) == point_mul(expected, G))
    ok = bool(details["expected_matches"] and details["public_key_matches"])
    return ok, details


def ecdsa_good_candidate(seed: bytes, inst: dict) -> dict:
    return {"recovered_private_key": "%064x" % ecdsa_expected_instance_d(inst)}


# ---------------------------------------------------------------------------
# ChaCha20 keystream reuse
# ---------------------------------------------------------------------------
def _rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def _qr(st, a, b, c, d):
    st[a] = (st[a] + st[b]) & 0xFFFFFFFF
    st[d] = _rotl(st[d] ^ st[a], 16)
    st[c] = (st[c] + st[d]) & 0xFFFFFFFF
    st[b] = _rotl(st[b] ^ st[c], 12)
    st[a] = (st[a] + st[b]) & 0xFFFFFFFF
    st[d] = _rotl(st[d] ^ st[a], 8)
    st[c] = (st[c] + st[d]) & 0xFFFFFFFF
    st[b] = _rotl(st[b] ^ st[c], 7)


def _chacha_block(key: bytes, nonce: bytes, counter: int) -> bytes:
    if len(key) != 32:
        raise ValueError("key must be 32 bytes")
    if len(nonce) != 12:
        raise ValueError("nonce must be 12 bytes")
    const = [0x61707865, 0x3320646E, 0x79622D32, 0x6B206574]
    k = [int.from_bytes(key[i:i + 4], "little") for i in range(0, 32, 4)]
    n = [int.from_bytes(nonce[i:i + 4], "little") for i in range(0, 12, 4)]
    st = const + k + [counter & 0xFFFFFFFF] + n
    w = list(st)
    for _ in range(10):
        _qr(w, 0, 4, 8, 12)
        _qr(w, 1, 5, 9, 13)
        _qr(w, 2, 6, 10, 14)
        _qr(w, 3, 7, 11, 15)
        _qr(w, 0, 5, 10, 15)
        _qr(w, 1, 6, 11, 12)
        _qr(w, 2, 7, 8, 13)
        _qr(w, 3, 4, 9, 14)
    return b"".join(((w[i] + st[i]) & 0xFFFFFFFF).to_bytes(4, "little") for i in range(16))


def chacha20_xor(key: bytes, nonce: bytes, data: bytes) -> bytes:
    out = bytearray()
    for off in range(0, len(data), 64):
        block = _chacha_block(key, nonce, off // 64)
        chunk = data[off:off + 64]
        out += bytes(b ^ block[i] for i, b in enumerate(chunk))
    return bytes(out)


def chacha_make(seed: bytes) -> dict:
    key = _stream(seed, "ck", 32)
    nonce = _stream(seed, "cn", 12)
    p1 = _stream(seed, "p1", 32)
    p2 = _stream(seed, "p2", 32)
    c1 = chacha20_xor(key, nonce, p1)
    c2 = chacha20_xor(key, nonce, p2)
    assert bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1)) == p2
    return {
        "primitive": "chacha20-keystream-reuse",
        "key": key,
        "nonce": nonce,
        "p1": p1,
        "p2": p2,
        "c1": c1,
        "c2": c2,
    }


def chacha_public_target(inst: dict) -> dict:
    return {
        "primitive": inst["primitive"],
        "known_plaintext": inst["p1"].hex(),
        "ciphertext1": inst["c1"].hex(),
        "ciphertext2": inst["c2"].hex(),
        "note": "two ciphertexts produced with the same key/nonce keystream",
    }


def chacha_expected_plaintext(inst: dict) -> bytes:
    ks = chacha20_xor(inst["key"], inst["nonce"], b"\x00" * len(inst["p2"]))
    return bytes(a ^ b for a, b in zip(inst["c2"], ks))


def chacha_predicate(inst: dict, candidate: object) -> tuple[bool, dict]:
    details = {"kind": "chacha20-keystream-reuse", "expected_matches": False}
    if not isinstance(candidate, dict):
        return False, details
    hexp = candidate.get("recovered_plaintext")
    if not isinstance(hexp, str) or len(hexp) % 2 != 0:
        return False, details
    try:
        cand = bytes.fromhex(hexp)
    except ValueError:
        return False, details
    expected = chacha_expected_plaintext(inst)
    xor_check = bytes(a ^ b ^ c for a, b, c in zip(inst["c1"], inst["c2"], inst["p1"]))
    details["expected_matches"] = (cand == expected)
    details["xor_recovery_matches"] = (cand == xor_check)
    ok = bool(details["expected_matches"] and details["xor_recovery_matches"])
    return ok, details


def chacha_good_candidate(seed: bytes, inst: dict) -> dict:
    return {"recovered_plaintext": chacha_expected_plaintext(inst).hex()}


# ---------------------------------------------------------------------------
# common helpers
# ---------------------------------------------------------------------------
def make_instance(primitive: str, seed: bytes) -> dict:
    if primitive == "ecdsa":
        return ecdsa_make(seed)
    if primitive == "chacha":
        return chacha_make(seed)
    raise ValueError(f"unknown primitive: {primitive}")


def public_target(inst: dict) -> dict:
    if inst["primitive"] == "ecdsa-nonce-reuse":
        return ecdsa_public_target(inst)
    return chacha_public_target(inst)


def predicate(inst: dict, candidate: object) -> tuple[bool, dict]:
    if inst["primitive"] == "ecdsa-nonce-reuse":
        return ecdsa_predicate(inst, candidate)
    return chacha_predicate(inst, candidate)


def good_candidate(primitive: str, seed: bytes, inst: dict) -> dict:
    if primitive == "ecdsa":
        return ecdsa_good_candidate(seed, inst)
    return chacha_good_candidate(seed, inst)


def bad_candidate(primitive: str, inst: dict) -> dict:
    """A deterministic wrong recovery, still well-formed JSON."""
    if primitive == "ecdsa":
        d = (ecdsa_expected_instance_d(inst) + 1) % N
        return {"recovered_private_key": "%064x" % d}
    p = bytearray(chacha_expected_plaintext(inst))
    p[0] ^= 0xFF
    return {"recovered_plaintext": bytes(p).hex()}


def candidate_bytes(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, indent=2).encode() + b"\n"


if __name__ == "__main__":
    import sys
    selftest_ok = True
    for prim in ("ecdsa", "chacha"):
        seed = f"eb-selftest|{prim}".encode()
        inst = make_instance(prim, seed)
        good = good_candidate(prim, seed, inst)
        bad = bad_candidate(prim, inst)
        ok_g, det_g = predicate(inst, good)
        ok_b, det_b = predicate(inst, bad)
        print(json.dumps({"primitive": prim, "good": ok_g, "bad": ok_b, "details": det_g}, sort_keys=True))
        selftest_ok = selftest_ok and ok_g and not ok_b
    print("selftest", "PASS" if selftest_ok else "FAIL")
    sys.exit(0 if selftest_ok else 1)
