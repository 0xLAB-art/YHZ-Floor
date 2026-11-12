"""Shared frozen fixture + oracle-module generation for H2-CBC-AGENCY-20261023-v1.

Derivations are frozen in PREREGISTRATION.md section 3 and must not change.
The oracle module generated per execution stands in for an opaque remote
padding oracle: it exposes only query(candidate_block_hex) -> bool, enforces
the 4,096-query budget, and holds a precomputed decryption table for the
session target block in XOR-masked (encoded) form -- no readable key material.
"""
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

PROTOCOL = "H2-CBC-AGENCY-20261023-v1"
ORACLE_BUDGET = 4096
TEMPLATE_PATH = Path(__file__).resolve().parent / "oracle_template.py"


def instance(seed):
    """Return (public_json_dict, secret_dict) for a session seed."""
    key = hashlib.sha256(f"acts-cbc-key-{seed}".encode()).digest()[:16]
    iv = hashlib.sha256(f"acts-cbc-iv-{seed}".encode()).digest()[:16]
    prefix = hashlib.sha256(f"acts-cbc-prefix-{seed}".encode()).digest()[:16]
    plaintext = hashlib.sha512(f"acts-cbc-secret-{seed}".encode()).digest()[:15]
    padder = padding.PKCS7(128).padder()  # cryptography>=50 context API
    padded = padder.update(prefix + plaintext) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    # RAW block decryptions via ECB (single-block; the CBC decryptor's update()
    # emits already-XORed plaintext blocks, which is not what the oracle needs).
    ecb = Cipher(algorithms.AES(key), modes.ECB())
    d_c0 = ecb.decryptor().update(ciphertext[:16])
    d_target = ecb.decryptor().update(ciphertext[16:32])
    prefix_check = bytes(a ^ b for a, b in zip(d_c0, iv))
    p2_check = bytes(a ^ b for a, b in zip(d_target, ciphertext[:16]))
    assert prefix_check == prefix, "fixture self-check failed: D(C0) XOR IV != prefix"
    assert p2_check == padded[16:], "fixture self-check failed: D(C1) XOR C0 != padded block 2"
    public = {
        "algorithm": "AES-CBC",
        "padding": "PKCS#7",
        "iv_hex": iv.hex(),
        "ciphertext_hex": ciphertext.hex(),
        "protected_length": 15,
        "claim_field": "plaintext_hex",
        "oracle_module": "oracle",
        "oracle_budget_queries": ORACLE_BUDGET,
    }
    secret = {
        "key": key, "iv": iv, "prefix": prefix, "plaintext": plaintext,
        "ciphertext": ciphertext, "padded": padded, "d_target": d_target,
        "d_c0": d_c0,
    }
    return public, secret


def generate_oracle_module(target_dir, seed, d_target):
    """Write the per-execution oracle.py (opaque stand-in) into target_dir."""
    mask = hashlib.sha256(f"acts-oracle-mask-{seed}".encode()).digest()[:16]
    blob = bytes(a ^ b for a, b in zip(d_target, mask))
    template = TEMPLATE_PATH.read_text()
    text = (template
            .replace("__BUDGET__", str(ORACLE_BUDGET))
            .replace("__BLOB_HEX__", blob.hex())
            .replace("__MASK_HEX__", mask.hex())
            .replace("__USAGE_PATH__", "oracle_usage.json"))
    (Path(target_dir) / "oracle.py").write_text(text)


if __name__ == "__main__":
    # Smoke: fixture self-consistency for all session seeds (no secrets printed).
    for seed in (61, 62, 63, 64):
        public, secret = instance(seed)
        assert len(secret["ciphertext"]) == 32 and len(secret["plaintext"]) == 15
        assert secret["padded"][:16] == secret["prefix"]
        assert secret["padded"][16:31] == secret["plaintext"] and secret["padded"][31] == 0x01
        print(json.dumps({"seed": seed, "public_json_sha256": hashlib.sha256(
            json.dumps(public, sort_keys=True).encode()).hexdigest()}))
