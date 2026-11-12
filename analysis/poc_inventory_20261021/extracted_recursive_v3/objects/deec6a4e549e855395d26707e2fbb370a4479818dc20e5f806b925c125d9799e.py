import json
import sys
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

def decode_der_signature(der_hex):
    der = bytes.fromhex(der_hex)
    idx = 2
    r_len = der[idx + 1]
    r = int.from_bytes(der[idx + 2:idx + 2 + r_len], 'big')
    idx += 2 + r_len
    s_len = der[idx + 1]
    s = int.from_bytes(der[idx + 2:idx + 2 + s_len], 'big')
    return r, s

with open(sys.argv[1]) as f:
    data = json.load(f)

r1, s1 = decode_der_signature(data['signature_one_der'])
r2, s2 = decode_der_signature(data['signature_two_der'])

h1 = int.from_bytes(hashlib.sha256(data['message_one'].encode()).digest(), 'big')
h2 = int.from_bytes(hashlib.sha256(data['message_two'].encode()).digest(), 'big')

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

k = ((h1 - h2) * pow(s1 - s2, -1, n)) % n
d = ((s1 * k - h1) * pow(r1, -1, n)) % n

print(json.dumps({"private_key_hex": format(d, '064x')}))