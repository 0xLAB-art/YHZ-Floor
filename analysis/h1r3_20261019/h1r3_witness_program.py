#!/usr/bin/env python3
"""Mechanical solution programs for the H1-R3 task ladder.

These exist so the deterministic gate can demonstrate, without any model call,
that every (family, level, arm) task is solvable inside the declared contract
(imports, argv-only input, sandbox, output schema) and that the reference
verifier accepts the resulting bytes.  They are not given to the model.
"""
from __future__ import annotations

XOR_SOLVER = '''import base64
import json
import sys

data = json.load(open(sys.argv[1], "r"))
enc = data.get("encoding")

def dec(value):
    if enc == "hex-v1":
        return bytes.fromhex(value)
    return base64.b64decode(value)

ciphertexts = {c["message_index"]: dec(c["data"]) for c in data["ciphertexts"]}
target = data["target"]
start = target["offset"]
length = target["length"]
message = target["message_index"]

keystream = [None] * length
for crib in data["known_plaintexts"]:
    blob = dec(crib["data"])
    offset = crib["offset"]
    for j, byte in enumerate(blob):
        pos = offset + j
        if start <= pos < start + length and keystream[pos - start] is None:
            keystream[pos - start] = ciphertexts[crib["message_index"]][pos] ^ byte

if any(x is None for x in keystream):
    print(json.dumps({"status": "UNDERDETERMINED", "reason": "incomplete coverage"}))
else:
    out = bytes(ciphertexts[message][start + j] ^ keystream[j] for j in range(length))
    print(json.dumps({"plaintext": out.hex()}))
'''

ECDSA_SOLVER = '''import base64
import json
import sys

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
data = json.load(open(sys.argv[1], "r"))
enc = data.get("encoding")

def dec(value):
    if enc == "hex-v1":
        return int(value, 16)
    return int.from_bytes(base64.b64decode(value), "big")

sigs = [(dec(s["r"]), dec(s["s"]), dec(s["z"])) for s in data["signatures"]]
groups = {}
for idx, (r, _s, _z) in enumerate(sigs):
    groups.setdefault(r, []).append(idx)
pairs = [g for g in groups.values() if len(g) == 2]
if len(pairs) != 1:
    print(json.dumps({"status": "UNDERDETERMINED", "reason": "no unique repeated r"}))
else:
    i, j = pairs[0]
    r1, s1, z1 = sigs[i]
    r2, s2, z2 = sigs[j]
    k = ((z1 - z2) * pow((s1 - s2) % N, -1, N)) % N
    d = ((s1 * k - z1) * pow(r1, -1, N)) % N
    if "k" in data.get("required_output", []) or REQUIRED_K:
        print(json.dumps({"d": format(d, "064x"), "k": format(k, "064x")}))
    else:
        print(json.dumps({"d": format(d, "064x")}))
'''


def solution_source(family: str, require_k: bool) -> str:
    if family == "XOR_Keystream_Reuse":
        return XOR_SOLVER
    return ECDSA_SOLVER.replace("REQUIRED_K", "True" if require_k else "False")


ABSTAIN = '''import json
print(json.dumps({"status": "UNDERDETERMINED", "reason": "public observation does not determine a unique target"}))
'''

WRONG_XOR = '''import json
import sys
data = json.load(open(sys.argv[1], "r"))
print(json.dumps({"plaintext": "00" * data["target"]["length"]}))
'''

WRONG_ECDSA = '''import json
print(json.dumps({"d": "00" * 32}))
'''
