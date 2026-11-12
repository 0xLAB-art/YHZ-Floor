import sys
import json
import base64

def b64_to_int(s):
    return int.from_bytes(base64.b64decode(s), 'big')

def modinv(a, m):
    return pow(a, -1, m)

data = json.load(open(sys.argv[1]))

# secp256k1 parameters
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Parse signatures
r = b64_to_int(data['signature_1']['r'])
s1 = b64_to_int(data['signature_1']['s'])
z1 = b64_to_int(data['signature_1']['z'])
s2 = b64_to_int(data['signature_2']['s'])
z2 = b64_to_int(data['signature_2']['z'])

# Recover k from nonce reuse: k = (z1 - z2) / (s1 - s2) mod n
k = ((z1 - z2) % n * modinv((s1 - s2) % n, n)) % n

# Recover d from k: d = (s*k - z) / r mod n
d = ((s1 * k - z1) % n * modinv(r, n)) % n

print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))
