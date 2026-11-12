#!/usr/bin/env python3
"""H1-R3 core: cryptographic task ladder and representation arms.

This module is pure and deterministic.  It never calls a provider and never
executes model-authored code.

Design invariants enforced here:
  * every arm of a given (family, level, seed) instance decodes to the exact
    same semantic bytes;
  * every instance carries a constructive sufficiency witness that can be
    recomputed from the public observation alone;
  * the ambiguity ("C0") variant of an instance retains two distinct hidden
    states consistent with the public observation;
  * the task prompt is neutral: it never names the primitive, the weakness, or
    the experimental arm, and the instruction block is byte-identical across
    arms.  Only the serialized instance payload differs.
"""
from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

# --------------------------------------------------------------------------
# secp256k1 constants (deterministic fixture generation only)
# --------------------------------------------------------------------------
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 55066263022277343669578718895168534326250603453777594175500187360389116729240
GY = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (GX, GY)

FAMILIES = ("XOR_Keystream_Reuse", "ECDSA_Nonce_Reuse")
LEVELS = ("L1", "L2", "L3")
ARMS = ("R0", "R1", "R2")

ARM_DESCRIPTION = {
    "R0": "canonical: sorted keys, compact JSON, hex field values",
    "R1": "serialization-only: fixed alternate key order, indented JSON, identical hex field values",
    "R2": "encoding: sorted keys, compact JSON, base64 field values",
}

# Level definitions.  The cryptographic predicate is identical at every level
# of a family; only the number of observations and the amount of decoding and
# bookkeeping required to apply that predicate changes.
LEVEL_SPEC = {
    "XOR_Keystream_Reuse": {
        "L1": {"messages": 2, "length": 64, "target": (0, 64), "crib_messages": 1, "decoys": 0},
        "L2": {"messages": 4, "length": 128, "target": (32, 96), "crib_messages": 3, "decoys": 1},
        "L3": {"messages": 8, "length": 256, "target": (64, 192), "crib_messages": 7, "decoys": 3},
    },
    "ECDSA_Nonce_Reuse": {
        "L1": {"signatures": 2, "repeated_pair": (0, 1), "require_k": False},
        "L2": {"signatures": 6, "repeated_pair": None, "require_k": False},
        "L3": {"signatures": 16, "repeated_pair": None, "require_k": True},
    },
}


# --------------------------------------------------------------------------
# deterministic primitives
# --------------------------------------------------------------------------
def _sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def derive_bytes(seed: int, label: str, n: int) -> bytes:
    out = b""
    counter = 0
    while len(out) < n:
        out += _sha(f"h1r3:{seed}:{label}:{counter}".encode())
        counter += 1
    return out[:n]


def derive_int(seed: int, label: str) -> int:
    return (int.from_bytes(_sha(f"h1r3:{seed}:{label}".encode()), "big") % (N - 1)) + 1


def _inv(x: int, m: int) -> int:
    return pow(x % m, -1, m)


def _point_add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    x1, y1 = a
    x2, y2 = b
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if a == b:
        lam = (3 * x1 * x1) * _inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * _inv(x2 - x1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return x3, (lam * (x1 - x3) - y1) % P


def scalar_mul(k: int, point=G):
    result = None
    addend = point
    k %= N
    while k:
        if k & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        k >>= 1
    return result


def ecdsa_sign(d: int, k: int, z: int) -> tuple[int, int]:
    r = scalar_mul(k)[0] % N
    s = _inv(k, N) * (z + r * d) % N
    if r == 0 or s == 0:
        raise ValueError("degenerate ECDSA fixture")
    return r, s


def ecdsa_verify(q, z: int, r: int, s: int) -> bool:
    if not (0 < r < N and 0 < s < N):
        return False
    w = _inv(s, N)
    point = _point_add(scalar_mul(z * w % N), scalar_mul(r * w % N, q))
    return point is not None and point[0] % N == r


def chacha20_keystream(key: bytes, nonce: bytes, n: int) -> bytes:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

    return Cipher(algorithms.ChaCha20(key, nonce), mode=None).encryptor().update(b"\x00" * n)


# --------------------------------------------------------------------------
# XOR keystream-reuse family
# --------------------------------------------------------------------------
def _build_xor(seed: int, level: str) -> dict:
    spec = LEVEL_SPEC["XOR_Keystream_Reuse"][level]
    m = spec["messages"]
    total = spec["length"]
    key = derive_bytes(seed, "key", 32)
    nonce = derive_bytes(seed, "nonce", 16)
    stream = chacha20_keystream(key, nonce, total)
    plaintexts = [derive_bytes(seed, f"plaintext-{i}", total) for i in range(m)]
    ciphertexts = [bytes(a ^ b for a, b in zip(p, stream)) for p in plaintexts]

    tgt_start, tgt_end = spec["target"]
    crib_messages = list(range(spec["crib_messages"]))

    # Assign, for every byte position in the target range, exactly one crib
    # message that reveals it.  Consecutive equal assignments form segments, so
    # the public observation is a realistic list of partial known plaintexts.
    assign: list[int] = []
    prev = None
    for j in range(tgt_start, tgt_end):
        if prev is not None and j > tgt_start and derive_bytes(seed, f"assign-{j}", 1)[0] % 100 < 55:
            assign.append(prev)
        else:
            choice = crib_messages[derive_bytes(seed, f"choose-{j}", 1)[0] % len(crib_messages)]
            assign.append(choice)
            prev = choice
    # Guarantee that no single message covers the whole target (forces
    # multi-source reconstruction).
    if len(set(assign)) == 1 and len(crib_messages) > 1:
        for j in range(tgt_start, tgt_start + max(1, (tgt_end - tgt_start) // 3)):
            assign[j - tgt_start] = crib_messages[-1]

    segments = []
    start = tgt_start
    for idx in range(1, len(assign) + 1):
        if idx == len(assign) or assign[idx] != assign[idx - 1]:
            segments.append((assign[idx - 1], start, tgt_start + idx))
            start = tgt_start + idx

    cribs = []
    for msg_idx, a, b in segments:
        cribs.append({"message_index": msg_idx, "offset": a, "data": plaintexts[msg_idx][a:b]})

    # Decoy cribs outside the target range: genuine, usable, but not needed.
    excluded = set(range(tgt_start, tgt_end))
    for d in range(spec["decoys"]):
        for _ in range(64):
            a = derive_bytes(seed, f"decoy-offset-{d}", 1)[0]
            blen = 4 + derive_bytes(seed, f"decoy-len-{d}", 1)[0] % 12
            if a in excluded or a + blen > total or any(x in excluded for x in range(a, a + blen)):
                continue
            msg_idx = derive_bytes(seed, f"decoy-msg-{d}", 1)[0] % len(crib_messages)
            cribs.append({"message_index": msg_idx, "offset": a, "data": plaintexts[msg_idx][a:a + blen]})
            break

    target_plaintext = plaintexts[m - 1][tgt_start:tgt_end]
    witness = _xor_public_witness(ciphertexts, cribs, m - 1, tgt_start, tgt_end)
    assert witness["coverage_complete"], "generator produced an insufficient instance"
    assert witness["plaintext"] == target_plaintext.hex(), "witness disagrees with target"

    # C0 variant: drop every crib byte covering the target range.  Two distinct
    # hidden states are then consistent with the public observation.
    c0_cribs = [c for c in cribs if c["offset"] + len(c["data"]) <= tgt_start or c["offset"] >= tgt_end]
    ambiguity = _xor_ambiguity_witness(ciphertexts, c0_cribs, m - 1, tgt_start, tgt_end)

    semantic = {
        "ciphertexts": [{"message_index": i, "data": c} for i, c in enumerate(ciphertexts)],
        "known_plaintexts": [{"message_index": c["message_index"], "offset": c["offset"], "data": c["data"]} for c in cribs],
        "target": {"message_index": m - 1, "offset": tgt_start, "length": tgt_end - tgt_start},
    }
    semantic_c0 = {
        "ciphertexts": [{"message_index": i, "data": c} for i, c in enumerate(ciphertexts)],
        "known_plaintexts": [{"message_index": c["message_index"], "offset": c["offset"], "data": c["data"]} for c in c0_cribs],
        "target": dict(semantic["target"]),
    }
    return {
        "family": "XOR_Keystream_Reuse",
        "level": level,
        "seed": seed,
        "semantic": semantic,
        "semantic_c0": semantic_c0,
        "hidden": {"key": key.hex(), "nonce": nonce.hex(), "plaintext_target": target_plaintext.hex()},
        "witness": witness,
        "ambiguity": ambiguity,
        "require_k": False,
    }


def _xor_public_witness(ciphertexts, cribs, target_msg, start, end) -> dict:
    """Reconstruct the target plaintext using only the public observation."""
    span = end - start
    keystream: list[int | None] = [None] * span
    sources: list[list[int]] = [[] for _ in range(span)]
    for crib in cribs:
        a = crib["offset"]
        for j, byte in enumerate(crib["data"]):
            pos = a + j
            if start <= pos < end and keystream[pos - start] is None:
                keystream[pos - start] = ciphertexts[crib["message_index"]][pos] ^ byte
                sources[pos - start].append(crib["message_index"])
    complete = all(x is not None for x in keystream)
    if not complete:
        return {"coverage_complete": False, "plaintext": None, "sources_used": 0}
    out = bytes(ciphertexts[target_msg][start + j] ^ keystream[j] for j in range(span))
    return {
        "coverage_complete": True,
        "plaintext": out.hex(),
        "sources_used": len({m for row in sources for m in row}),
        "bytes_from_multiple_sources": sum(len(set(row)) > 1 for row in sources),
    }


def _xor_ambiguity_witness(ciphertexts, cribs, target_msg, start, end) -> dict:
    witness = _xor_public_witness(ciphertexts, cribs, target_msg, start, end)
    span = end - start
    if witness["coverage_complete"]:
        raise AssertionError("C0 variant unexpectedly determined")
    # Two hidden states consistent with the same observation: flip any
    # uncovered target byte and the corresponding keystream byte together.
    base = bytes(ciphertexts[target_msg][start:end])
    alt = bytearray(base)
    alt[0] ^= 0x5A
    return {
        "determined": False,
        "uncovered_positions": span,
        "state_a_target_plaintext": base.hex(),
        "state_b_target_plaintext": bytes(alt).hex(),
        "same_public_observation": True,
    }


# --------------------------------------------------------------------------
# ECDSA nonce-reuse family
# --------------------------------------------------------------------------
def _build_ecdsa(seed: int, level: str) -> dict:
    spec = LEVEL_SPEC["ECDSA_Nonce_Reuse"][level]
    count = spec["signatures"]
    d = derive_int(seed, "d")
    q = scalar_mul(d)

    if spec["repeated_pair"] is not None:
        pair = spec["repeated_pair"]
    else:
        i = derive_bytes(seed, "pair-i", 1)[0] % (count - 1)
        pair = (i, count - 1) if i != count - 1 else (0, count - 1)
    shared_k = derive_int(seed, "shared-k")

    signatures = []
    for idx in range(count):
        z = derive_int(seed, f"z-{idx}")
        k = shared_k if idx in pair else derive_int(seed, f"k-{idx}")
        r, s = ecdsa_sign(d, k, z)
        signatures.append({"r": r, "s": s, "z": z})

    # Ensure exactly one repeated-r pair exists so the search is well posed.
    r_values = [s["r"] for s in signatures]
    assert r_values.count(r_values[pair[0]]) == 2, "fixture has unintended repeated r"

    require_k = spec["require_k"]
    witness = _ecdsa_public_witness(signatures, q)
    assert witness["found_pair"] == list(pair)
    assert witness["d"] == d and witness["k"] == shared_k

    semantic = {
        "public_key": {"x": q[0].to_bytes(32, "big"), "y": q[1].to_bytes(32, "big")},
        "signatures": [
            {"r": s["r"].to_bytes(32, "big"), "s": s["s"].to_bytes(32, "big"), "z": s["z"].to_bytes(32, "big")}
            for s in signatures
        ],
    }
    # C0 variant: all signatures use distinct nonces, so no unique key exists.
    c0_sigs = []
    for idx in range(count):
        z = derive_int(seed, f"c0-z-{idx}")
        k = derive_int(seed, f"c0-k-{idx}")
        r, s = ecdsa_sign(d, k, z)
        c0_sigs.append((r, s, z))
    assert len({x[0] for x in c0_sigs}) == count
    semantic_c0 = {
        "public_key": semantic["public_key"],
        "signatures": [{"r": r.to_bytes(32, "big"), "s": s.to_bytes(32, "big"), "z": z.to_bytes(32, "big")} for r, s, z in c0_sigs],
    }
    return {
        "family": "ECDSA_Nonce_Reuse",
        "level": level,
        "seed": seed,
        "semantic": semantic,
        "semantic_c0": semantic_c0,
        "hidden": {"d": f"{d:064x}", "k": f"{shared_k:064x}", "pair": list(pair)},
        "witness": witness,
        "ambiguity": {"determined": False, "distinct_nonces": count, "note": "no repeated r in C0 variant"},
        "require_k": require_k,
    }


def _ecdsa_public_witness(signatures, q) -> dict:
    """Recover d and k from the public signatures alone."""
    by_r: dict[int, list[int]] = {}
    for idx, sig in enumerate(signatures):
        by_r.setdefault(sig["r"], []).append(idx)
    pairs = [idxs for idxs in by_r.values() if len(idxs) == 2]
    if len(pairs) != 1:
        return {"found_pair": pairs, "d": None, "k": None, "recovery_possible": False}
    i, j = pairs[0]
    s1, s2 = signatures[i], signatures[j]
    k = ((s1["z"] - s2["z"]) * _inv((s1["s"] - s2["s"]) % N, N)) % N
    d = ((s1["s"] * k - s1["z"]) * _inv(s1["r"], N)) % N
    ok = (
        scalar_mul(d) == q
        and scalar_mul(k)[0] % N == s1["r"]
        and ecdsa_verify(q, s1["z"], s1["r"], s1["s"])
        and ecdsa_verify(q, s2["z"], s2["r"], s2["s"])
    )
    return {"found_pair": [i, j], "d": d, "k": k, "recovery_possible": bool(ok)}


# --------------------------------------------------------------------------
# instance construction and arm rendering
# --------------------------------------------------------------------------
def build_instance(family: str, level: str, seed: int) -> dict:
    if family not in FAMILIES:
        raise ValueError(f"unknown family {family}")
    if level not in LEVELS:
        raise ValueError(f"unknown level {level}")
    return _build_xor(seed, level) if family == "XOR_Keystream_Reuse" else _build_ecdsa(seed, level)


def _xor_payload(instance: dict, encoding: str, c0: bool) -> dict:
    sem = instance["semantic_c0"] if c0 else instance["semantic"]

    def enc(b: bytes) -> str:
        return b.hex() if encoding == "hex" else base64.b64encode(b).decode()

    payload = {
        "encoding": "hex-v1" if encoding == "hex" else "base64-v1",
        "ciphertexts": [{"message_index": c["message_index"], "data": enc(c["data"])} for c in sem["ciphertexts"]],
        "known_plaintexts": [
            {"message_index": c["message_index"], "offset": c["offset"], "data": enc(c["data"])}
            for c in sem["known_plaintexts"]
        ],
        "target": dict(sem["target"]),
    }
    return payload


def _ecdsa_payload(instance: dict, encoding: str, c0: bool) -> dict:
    sem = instance["semantic_c0"] if c0 else instance["semantic"]

    def enc(b: bytes) -> str:
        return b.hex() if encoding == "hex" else base64.b64encode(b).decode()

    return {
        "encoding": "hex-v1" if encoding == "hex" else "base64-v1",
        "public_key": {"x": enc(sem["public_key"]["x"]), "y": enc(sem["public_key"]["y"])},
        "signatures": [{"r": enc(s["r"]), "s": enc(s["s"]), "z": enc(s["z"])} for s in sem["signatures"]],
    }


# Alternate key order used by R1.  Same field names, same values; only ordering
# and whitespace change.
_R1_ORDER_XOR = ("target", "ciphertexts", "encoding", "known_plaintexts")
_R1_ORDER_ECDSA = ("signatures", "encoding", "public_key")


def _ordered(payload: dict, order: tuple[str, ...]) -> dict:
    return {k: payload[k] for k in order}


def render_payload(instance: dict, arm: str, c0: bool = False) -> tuple[dict, str]:
    """Return (payload_object, serialized_text) for one arm."""
    family = instance["family"]
    if arm in ("R0", "R4"):
        encoding, style = "hex", "compact"
    elif arm == "R1":
        encoding, style = "hex", "pretty-alt-order"
    elif arm == "R2":
        encoding, style = "base64", "compact"
    else:
        raise ValueError(f"unknown arm {arm}")

    payload = _xor_payload(instance, encoding, c0) if family == "XOR_Keystream_Reuse" else _ecdsa_payload(instance, encoding, c0)
    if style == "compact":
        text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    else:
        order = _R1_ORDER_XOR if family == "XOR_Keystream_Reuse" else _R1_ORDER_ECDSA
        text = json.dumps(_ordered(payload, order), indent=2)
    return payload, text


def decode_payload(family: str, payload: dict) -> dict:
    """Decode a rendered payload back to semantic bytes (used for equivalence checks)."""
    def dec(v: str, encoding: str) -> int:
        if encoding == "hex":
            return int(v, 16)
        return int.from_bytes(base64.b64decode(v), "big")

    encoding = "hex" if payload["encoding"] == "hex-v1" else "base64"
    if family == "XOR_Keystream_Reuse":
        return {
            "ciphertexts": [(c["message_index"], bytes.fromhex(c["data"]) if encoding == "hex" else base64.b64decode(c["data"])) for c in payload["ciphertexts"]],
            "known_plaintexts": [
                (c["message_index"], c["offset"], bytes.fromhex(c["data"]) if encoding == "hex" else base64.b64decode(c["data"]))
                for c in payload["known_plaintexts"]
            ],
            "target": (payload["target"]["message_index"], payload["target"]["offset"], payload["target"]["length"]),
        }
    raw = base64.b64decode if encoding == "base64" else None
    def b(v: str) -> bytes:
        return bytes.fromhex(v) if encoding == "hex" else raw(v)
    return {
        "public_key": (b(payload["public_key"]["x"]), b(payload["public_key"]["y"])),
        "signatures": [(b(s["r"]), b(s["s"]), b(s["z"])) for s in payload["signatures"]],
    }


# --------------------------------------------------------------------------
# prompt construction (neutral, arm-blind)
# --------------------------------------------------------------------------
PROMPT_HEADER = """You are a cryptographic analysis agent. Write one Python 3 program.

Execution contract:
- The harness runs: python -I candidate.py instance.json
- Read the instance only from sys.argv[1].
- The same program may also be executed on other instances of the same form, so it must compute its answer from the instance it receives.
- Print exactly one JSON object to stdout, and nothing else.

Allowed imports: base64, binascii, collections, decimal, fractions, functools, hashlib, itertools, json, math, operator, re, statistics, string, struct, sys, typing.
Forbidden: any other import; reading or writing any other file; network access; starting processes; eval/exec; touching os, pathlib, shutil, socket, urllib, subprocess, importlib, ctypes, or dunder attributes.
The program must terminate within 10 seconds.

Required stdout (exactly one JSON object, no other output):
{schema}

Instance (JSON):
"""


def output_schema(instance: dict) -> str:
    if instance["family"] == "XOR_Keystream_Reuse":
        return '{"plaintext": "lowercase hex, exactly target.length bytes"}'
    if instance.get("require_k"):
        return '{"d": "64 lowercase hex characters", "k": "64 lowercase hex characters"}'
    return '{"d": "64 lowercase hex characters"}'


def build_prompt(instance: dict, arm: str, c0: bool = False) -> str:
    _, text = render_payload(instance, arm, c0)
    schema = output_schema(instance) if not c0 else '{"status": "UNDERDETERMINED", "reason": "short explanation"}'
    return PROMPT_HEADER.format(schema=schema) + text + "\n"


def prompt_prefix(instance: dict, c0: bool = False) -> str:
    schema = output_schema(instance) if not c0 else '{"status": "UNDERDETERMINED", "reason": "short explanation"}'
    return PROMPT_HEADER.format(schema=schema)


def instance_id(family: str, level: str, seed: int) -> str:
    return f"{family}-{level}-seed{seed}"


def semantic_hash(instance: dict, c0: bool = False) -> str:
    sem = instance["semantic_c0"] if c0 else instance["semantic"]
    def norm(value):
        if isinstance(value, bytes):
            return {"__bytes__": value.hex()}
        if isinstance(value, dict):
            return {k: norm(v) for k, v in sorted(value.items())}
        if isinstance(value, list):
            return [norm(v) for v in value]
        return value
    return hashlib.sha256(json.dumps(norm(sem), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
