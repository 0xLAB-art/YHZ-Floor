#!/usr/bin/env python3
import sys
import json
import base64

def decode_b64(s):
    return int.from_bytes(base64.b64decode(s), 'big')

data = json.load(open(sys.argv[1]))

r = decode_b64(data['signature_1']['r'])
s1 = decode_b64(data['signature_1']['s'])
z1 = decode_b64(data['signature_1']['z'])
s2 = decode_b64(data['signature_2']['s'])
z2 = decode_b64(data['signature_2']['z'])

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

s1_inv = pow(s1, -1, n)
k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
d = ((s1 * k - z1) * s1_inv) % n

print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))