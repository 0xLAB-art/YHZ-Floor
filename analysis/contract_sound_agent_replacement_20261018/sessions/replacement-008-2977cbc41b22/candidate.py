import sys
import json
import base64

def decode_b64(s):
    return int.from_bytes(base64.b64decode(s), 'big')

def modinv(a, m):
    return pow(a, -1, m)

data = json.load(open(sys.argv[1]))

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

r = decode_b64(data['signature_1']['r'])
s1 = decode_b64(data['signature_1']['s'])
z1 = decode_b64(data['signature_1']['z'])
s2 = decode_b64(data['signature_2']['s'])
z2 = decode_b64(data['signature_2']['z'])

k = ((z1 - z2) * modinv(s1 - s2, n)) % n
d = ((s1 * k - z1) * modinv(r, n)) % n

print(json.dumps({"d": f"{d:064x}", "k": f"{k:064x}"}))
