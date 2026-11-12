import sys
import json
import base64

def b64_to_int(s):
    return int.from_bytes(base64.b64decode(s), 'big')

def modinv(a, m):
    return pow(a, -1, m)

data = json.load(open(sys.argv[1]))

r = b64_to_int(data['signature_1']['r'])
s1 = b64_to_int(data['signature_1']['s'])
z1 = b64_to_int(data['signature_1']['z'])
s2 = b64_to_int(data['signature_2']['s'])
z2 = b64_to_int(data['signature_2']['z'])

n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

k = ((z1 - z2) * modinv(s1 - s2, n)) % n
d = ((s1 * k - z1) * modinv(r, n)) % n

print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))
