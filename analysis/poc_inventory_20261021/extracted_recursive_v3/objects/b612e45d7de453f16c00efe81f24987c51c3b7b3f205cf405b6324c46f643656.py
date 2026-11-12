import json
import sys
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

def sha256_hash(message):
    return int.from_bytes(hashlib.sha256(message.encode()).digest(), 'big')

def modinv(a, m):
    return pow(a, -1, m)

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

m1 = sha256_hash(data['message_one'])
m2 = sha256_hash(data['message_two'])

sig1_der = bytes.fromhex(data['signature_one_der'])
sig2_der = bytes.fromhex(data['signature_two_der'])

r1, s1 = decode_dss_signature(sig1_der)
r2, s2 = decode_dss_signature(sig2_der)

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

k = ((m1 - m2) * modinv(s1 - s2, n)) % n
d = ((s1 * k - m1) * modinv(r1, n)) % n

print(json.dumps({"private_key_hex": hex(d)[2:].zfill(64)}))