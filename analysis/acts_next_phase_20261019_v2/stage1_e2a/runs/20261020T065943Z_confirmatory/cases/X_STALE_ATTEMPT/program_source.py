"""
ACTS-Attack E2A scripted producer program.
"""

import json
import sys

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def inv(x, m):
    return pow(x % m, -1, m)


def main():
    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        instance = json.load(handle)
    sig1 = instance["signature_1"]
    sig2 = instance["signature_2"]
    r1 = int(sig1["r"], 16)
    z1 = int(sig1["z"], 16)
    z2 = int(sig2["z"], 16)
    s1 = int(sig1["s"], 16)
    s2 = int(sig2["s"], 16)
    k = ((z1 - z2) * inv((s1 - s2) % N, N)) % N
    d = ((s1 * k - z1) * inv(r1, N)) % N

    print(json.dumps({"d": "%064x" % d, "k": "%064x" % k}, sort_keys=True))


main()
