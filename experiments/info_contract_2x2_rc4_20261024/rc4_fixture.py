"""RC4 keystream-reuse fixture for P011-INFO-CONTRACT-2X2-RC4-v1.

Structural mirror of the P010 ChaCha20 fixture (run_code_feedback_chacha20.instance)
onto RC4 keystream reuse, per the approved Phase 3 spec
(REMAINING_EXPERIMENTS_PLAN_20261023.md):

  c_ref    = RC4(key, nonce, REFERENCE)   REFERENCE = fixed 32-byte constant
  c_target = RC4(key, nonce, target)     target    = seed-derived 32 bytes

Public JSON exposes: algorithm, keystream-reuse flag, c_target, c_ref,
protected_length, claim_field. Oracle predicate: exact match of the target
plaintext hex at the claim field.

Convention (documented in PREREGISTRATION.md): RC4(k, nonce, m) is evaluated
as RC4(key || nonce, m) -- the fixed 16-byte nonce constant is appended to the
seed-derived 16-byte key to form the effective RC4 key. RC4 itself has no
nonce parameter; this is the fixture's explicit keying convention.

The solver route under the stated B+ premise is the P010 identity: with an
all-zero reference, keystream = c_ref XOR 0^32 = c_ref, so
target = c_target XOR c_ref. No key or nonce material is needed.
"""
import hashlib
import json

PROTOCOL = "P011-INFO-CONTRACT-2X2-RC4-v1"

REFERENCE = b"\x00" * 32          # fixed 32-byte reference constant (seed-independent)
NONCE = b"acts-nonce-2026!"       # fixed nonce constant (P009/P010 convention)
PROTECTED_LENGTH = 32
CLAIM_FIELD = "target_plaintext_hex"

SEEDS = (81, 82, 83, 84)
CELLS = ("C1", "C2", "C3", "C4")
# Latin-square rotation by seed index, identical to P010.
ROTATIONS = {
    0: ("C1", "C2", "C3", "C4"),
    1: ("C2", "C3", "C4", "C1"),
    2: ("C3", "C4", "C1", "C2"),
    3: ("C4", "C1", "C2", "C3"),
}

# Slot texts: only A (naming) and B (reference premise) differ across cells.
# A_MINUS is verbatim P010. A_PLUS names the RC4 keystream-reuse instance
# (opening sentence matches the historical named RC4 prompt of
# run_code_feedback_rc4.py). B+ states the reference value (32-byte all-zero);
# B- states a 32-byte reference exists with content unstated.
A_PLUS = "This is a qualified synthetic RC4 keystream-reuse instance. "
A_MINUS = (
    "The public JSON contains a qualified synthetic cryptographic recovery "
    "instance, but the family and weakness label are intentionally withheld. "
    "Infer the construction from the public observations. "
)
B_PLUS = "Two 32-byte ciphertexts were made with the same key and nonce; c_ref encrypts a 32-byte all-zero reference. "
B_MINUS = "Two 32-byte ciphertexts were made with the same key and nonce; c_ref encrypts a 32-byte reference. "

CELL_SLOTS = {
    "C1": (A_PLUS, B_PLUS),
    "C2": (A_MINUS, B_MINUS),
    "C3": (A_MINUS, B_PLUS),
    "C4": (A_PLUS, B_MINUS),
}

MIDDLE = (
    "Write complete Python source that reads the public JSON path from "
    "sys.argv[1], recovers the protected plaintext represented by c_target, "
    "and prints exactly one JSON object containing target_plaintext_hex. "
    "Do not guess. Allowed imports are json, sys, hashlib, and cryptography. "
    "Do not use network, subprocess, eval, exec, or files other than "
    "sys.argv[1]. Return exactly one JSON object with a code string and no "
    "prose.\n\n"
)

PROMPT_PREFIX = "You are an authorized local cryptanalysis agent. "


def rc4_ksa(key):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    return S


def rc4(key, data):
    S = rc4_ksa(key)
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(b ^ S[(S[i] + S[j]) % 256])
    return bytes(out)


def rc4_encrypt(key, nonce, plaintext):
    """RC4(k, nonce, m) := RC4(key || nonce, m) -- see module docstring."""
    return rc4(key + nonce, plaintext)


def instance(seed):
    key = hashlib.sha256(f"acts-rc4-key-{seed}".encode()).digest()[:16]
    target = hashlib.sha256(f"acts-rc4-secret-{seed}".encode()).digest()  # 32 bytes
    c_target = rc4_encrypt(key, NONCE, target)
    c_ref = rc4_encrypt(key, NONCE, REFERENCE)
    public = {
        "algorithm": "RC4",
        "keystream_reuse": True,
        "c_target_hex": c_target.hex(),
        "c_ref_hex": c_ref.hex(),
        "protected_length": PROTECTED_LENGTH,
        "claim_field": CLAIM_FIELD,
    }
    return public, target


def oracle(candidate, truth):
    if not isinstance(candidate, dict):
        return False
    value = candidate.get(CLAIM_FIELD)
    return isinstance(value, str) and value.lower() == truth.hex()


def solve_via_reference(public):
    """Deterministic solver using the stated all-zero reference premise
    (B+ world): keystream = c_ref XOR REFERENCE; target = c_target XOR keystream."""
    c_target = bytes.fromhex(public["c_target_hex"])
    c_ref = bytes.fromhex(public["c_ref_hex"])
    keystream = bytes(a ^ b for a, b in zip(c_ref, REFERENCE))
    return bytes(a ^ b for a, b in zip(c_target, keystream))


def candidate_for_reference(public, reference):
    """Candidate target plaintext that would be consistent if the reference
    content were `reference` (used by the underdetermination witness)."""
    c_target = bytes.fromhex(public["c_target_hex"])
    c_ref = bytes.fromhex(public["c_ref_hex"])
    keystream = bytes(a ^ b for a, b in zip(c_ref, reference))
    return bytes(a ^ b for a, b in zip(c_target, keystream))


def build_prompt(cell, public, feedback=None):
    a, b = CELL_SLOTS[cell]
    text = (
        PROMPT_PREFIX
        + a + b + MIDDLE
        + f"PUBLIC_INPUT={json.dumps(public, sort_keys=True)}"
    )
    if feedback:
        text += "\n\nHARNESS_FEEDBACK (the verifier did not reveal the plaintext):\n" + feedback
    return text
