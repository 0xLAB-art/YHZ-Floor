import sys
import json
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n, '064x')

data = json.load(open(sys.argv[1]))

# Decode base64 values
r1_bytes = base64.b64decode(data['signature_1']['r'])
s1_bytes = base64.b64decode(data['signature_1']['s'])
z1_bytes = base64.b64decode(data['signature_1']['z'])

r2_bytes = base64.b64decode(data['signature_2']['r'])
s2_bytes = base64.b64decode(data['signature_2']['s'])
z2_bytes = base64.b64decode(data['signature_2']['z'])

r1 = bytes_to_int(r1_bytes)
s1 = bytes_to_int(s1_bytes)
z1 = bytes_to_int(z1_bytes)

r2 = bytes_to_int(r2_bytes)
s2 = bytes_to_int(s2_bytes)
z2 = bytes_to_int(z2_bytes)

# secp256k1 order
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Nonce reuse: r1 == r2, so same k
# k = (z1 - z2) / (s1 - s2) mod n
# d = (s1*k - z1) / r1 mod n

def modinv(a, m):
    return pow(a, -1, m)

k = ((z1 - z2) * modinv(s1 - s2, n)) % n
d = ((s1 * k - z1) * modinv(r1, n)) % n

print(json.dumps({"d": int_to_hex(d), "k": int_to_hex(k)}))
