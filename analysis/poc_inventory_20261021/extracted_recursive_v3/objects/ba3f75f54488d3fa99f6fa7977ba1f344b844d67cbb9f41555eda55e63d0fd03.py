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
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

import base64

# secp256k1 order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse public key
Qx = bytes_to_int(base64.b64decode(data['public_key'][0]))
Qy = bytes_to_int(base64.b64decode(data['public_key'][1]))

# Parse signature 1
r1 = bytes_to_int(base64.b64decode(data['signature_1']['r']))
s1 = bytes_to_int(base64.b64decode(data['signature_1']['s']))
z1 = bytes_to_int(base64.b64decode(data['signature_1']['z']))

# Parse signature 2
r2 = bytes_to_int(base64.b64decode(data['signature_2']['r']))
s2 = bytes_to_int(base64.b64decode(data['signature_2']['s']))
z2 = bytes_to_int(base64.b64decode(data['signature_2']['z']))

# Nonce reuse: r1 == r2
# k = (z1 - z2) / (s1 - s2) mod n
# d = (s*k - z) / r mod n

k = (((z1 - z2) % n) * modinv((s1 - s2) % n, n)) % n
d = (((s1 * k - z1) % n) * modinv(r1, n)) % n

print(json.dumps({"d": int_to_hex(d), "k": int_to_hex(k)}))