"""Opaque local padding-oracle stand-in (generated per execution).

See PREREGISTRATION.md section 3. Public contract only:
query(candidate_block_hex) -> bool. Each call consumes one query from a
total budget; after the budget is exhausted further calls raise
RuntimeError("ORACLE_BUDGET_EXHAUSTED"). The decryption table for the
session target block is held XOR-masked; no readable key material is present.
The query count is instrumented to __USAGE_PATH__ (harness bookkeeping).
"""
import atexit
import json

_BUDGET = __BUDGET__
_BLOB = bytes.fromhex("__BLOB_HEX__")
_MASK = bytes.fromhex("__MASK_HEX__")
_USAGE_PATH = "__USAGE_PATH__"
_D = bytes(a ^ b for a, b in zip(_BLOB, _MASK))
_state = {"queries": 0}


def _write_usage():
    try:
        with open(_USAGE_PATH, "w") as handle:
            json.dump({"queries": _state["queries"], "budget": _BUDGET}, handle)
    except OSError:
        pass


def query(candidate_block_hex):
    """Return True when decrypting the two-block ciphertext
    (candidate_block followed by the session target block) under the secret
    key yields valid PKCS#7 padding on the final block; False otherwise."""
    raw = bytes.fromhex(candidate_block_hex)
    if len(raw) != 16:
        raise ValueError("candidate block must be exactly 16 bytes")
    _state["queries"] += 1
    if _state["queries"] > _BUDGET:
        _write_usage()
        raise RuntimeError("ORACLE_BUDGET_EXHAUSTED")
    candidate_xor_d = bytes(a ^ b for a, b in zip(raw, _D))
    pad = candidate_xor_d[-1]
    valid = 1 <= pad <= 16 and candidate_xor_d[-pad:] == bytes([pad]) * pad
    _write_usage()
    return valid


atexit.register(_write_usage)
