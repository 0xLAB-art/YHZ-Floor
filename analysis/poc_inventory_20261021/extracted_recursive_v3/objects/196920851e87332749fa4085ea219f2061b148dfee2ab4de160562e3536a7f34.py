import json
import sys
from hashlib import sha256

def modinv(a, m):
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    gcd, x, _ = egcd(a % m, m)
    if gcd != 1:
        raise ValueError("No inverse")
    return (x % m + m) % m

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

import base64

px = bytes_to_int(base64.b64decode(data['public_key'][0]))
py = bytes_to_int(base64.b64decode(data['public_key'][1]))

r1 = bytes_to_int(base64.b64decode(data['signature_1']['r']))
s1 = bytes_to_int(base64.b64decode(data['signature_1']['s']))
z1 = bytes_to_int(base64.b64decode(data['signature_1']['z']))

r2 = bytes_to_int(base64.b64decode(data['signature_2']['r']))
s2 = bytes_to_int(base64.b64decode(data['signature_2']['s']))
z2 = bytes_to_int(base64.b64decode(data['signature_2']['z']))

p = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551

k = ((z1 - z2) * modinv(s1 - s2, p)) % p
d = ((s1 * k - z1) * modinv(r1, p)) % p

print(json.dumps({"d": int_to_hex(d), "k": int_to_hex(k)}))