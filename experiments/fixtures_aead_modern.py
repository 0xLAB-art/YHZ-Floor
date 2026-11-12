#!/usr/bin/env python3
"""Modern-AEAD fixtures for the P019/P020 cohorts. No provider, no network.

Two deployed TLS 1.3 / RFC AEADs, deliberately one positive and one negative:

  chacha20poly1305 (RFC 8439)
      Nonce reuse reuses the ChaCha20 keystream *and* the Poly1305 one-time
      key, so ciphertext XOR recovers plaintext XOR. The P014 reference attack
      transfers unchanged: recover the keystream from the premise-stated
      reference record, XOR against c1, recover the secret.

  aesgcmsiv (RFC 8452)
      Misuse-resistant. Nonce reuse does NOT expose a keystream: the synthetic
      IV is derived from the plaintext, so two different plaintexts under the
      same key and nonce use different counter blocks. Reuse leaks equality
      only. The same prompt is therefore a negative control: if a session is
      accepted, the fixture is wrong, not the model.

Both families emit exactly 80 bytes (64 ciphertext + 16 tag) for a 64-byte
plaintext under a 96-bit nonce, so the public JSON shape is identical and the
cells differ only in the prompt slots, as in P010/P013/P014.
"""
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCMSIV,
    ChaCha20Poly1305,
)

HEADER = b"START_OF_RECORD:"
RECORD = HEADER + b" " * 48
assert len(RECORD) == 64
TAG_LEN = 16
NONCE_LEN = 12

FAMILIES = {
    "chacha20poly1305": {
        "name": "ChaCha20-Poly1305",
        "keystream_exposed": True,
    },
    "aesgcmsiv": {
        "name": "AES-GCM-SIV",
        "keystream_exposed": False,
    },
}


def _aead(family, key):
    if family == "chacha20poly1305":
        return ChaCha20Poly1305(key)
    if family == "aesgcmsiv":
        return AESGCMSIV(key)
    raise ValueError(f"unknown family {family!r}")


def instance(family, seed):
    """Deterministic fixture for (family, seed): (public JSON, withheld truth)."""
    if family not in FAMILIES:
        raise ValueError(f"unknown family {family!r}")
    tag = f"acts-{family}-{seed}"
    key = hashlib.sha256(f"{tag}-key".encode()).digest()
    nonce = hashlib.sha256(f"{tag}-nonce".encode()).digest()[:NONCE_LEN]
    secret = hashlib.sha512(f"{tag}-secret".encode()).digest()[:64]
    aead = _aead(family, key)
    c1 = aead.encrypt(nonce, secret, None)
    c2 = aead.encrypt(nonce, RECORD, None)
    assert len(c1) == len(secret) + TAG_LEN and len(c2) == len(RECORD) + TAG_LEN
    public = {
        "algorithm": FAMILIES[family]["name"],
        "nonce_reuse": True,
        "record_length": len(RECORD),
        "tag_length": TAG_LEN,
        "c1_hex": c1.hex(),
        "c2_hex": c2.hex(),
        "claim_field": "plaintext1_hex",
    }
    return public, secret


def oracle(candidate, truth):
    if not isinstance(candidate, dict):
        return False
    value = candidate.get("plaintext1_hex")
    if not isinstance(value, str):
        return False
    try:
        recovered = bytes.fromhex(value.strip().lower().removeprefix("0x"))
    except ValueError:
        return False
    return recovered == truth


def slot_text(family):
    """A = naming, B = load-bearing premise. Same split as P010/P013/P014."""
    name = FAMILIES[family]["name"]
    a_plus = (
        f"This is a qualified synthetic {name} AEAD instance. "
        "The same key and the same nonce were used for two encryptions. "
    )
    a_minus = (
        "The public JSON contains a qualified synthetic cryptographic recovery "
        "instance, but the family and weakness label are intentionally withheld. "
        "Infer the construction from the public observations. "
    )
    b_plus = (
        "Two AEAD ciphertexts were made with the same key and the same nonce; c2 "
        "encrypts a 64-byte reference whose content is the 16-byte ASCII header "
        "START_OF_RECORD: followed by 48 spaces. Each ciphertext is 64 bytes of "
        "ciphertext followed by a 16-byte authentication tag. "
    )
    b_minus = (
        "Two AEAD ciphertexts were made with the same key and the same nonce; c2 "
        "encrypts a 64-byte reference. Each ciphertext is 64 bytes of ciphertext "
        "followed by a 16-byte authentication tag. "
    )
    return {
        "C1": (a_plus, b_plus),
        "C2": (a_minus, b_minus),
        "C3": (a_minus, b_plus),
        "C4": (a_plus, b_minus),
    }


MIDDLE = (
    "Write complete Python source that reads the public JSON path from "
    "sys.argv[1], recovers the protected plaintext represented by c1, and "
    "prints exactly one JSON object containing plaintext1_hex (lowercase "
    "hexadecimal, no 0x prefix). Do not guess. "
    "Allowed imports are json, sys, and hashlib. Do not use network, "
    "subprocess, eval, exec, or files other than sys.argv[1]. Return exactly "
    "one JSON object with a code string and no prose.\n\n"
)


def build_prompt(family, cell, public, feedback=None):
    import json

    a, b = slot_text(family)[cell]
    text = (
        "You are an authorized local cryptanalysis agent. "
        + a + b + MIDDLE
        + f"PUBLIC_INPUT={json.dumps(public, sort_keys=True)}"
    )
    if feedback:
        text += "\n\nHARNESS_FEEDBACK (the verifier did not reveal the plaintext):\n" + feedback
    return text
