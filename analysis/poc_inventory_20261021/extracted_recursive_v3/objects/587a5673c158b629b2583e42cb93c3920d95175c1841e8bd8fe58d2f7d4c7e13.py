import json
import sys
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

def sha256_int(msg):
    return int.from_bytes(hashlib.sha256(msg.encode()).digest(), 'big')

with open(sys.argv[1]) as f:
    data = json.load(f)

r1_bytes = bytes.fromhex(data['signature_one_der'])
r2_bytes = bytes.fromhex(data['signature_two_der'])

r1, s1 = decode_dss_signature(r1_bytes)
r2, s2 = decode_dss_signature(r2_bytes)

z1 = sha256_int(data['message_one'])
z2 = sha256_int(data['message_two'])

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
d = ((s1 * k - z1) * pow(r1, -1, n)) % n

print(json.dumps({"private_key_hex": hex(d)[2:].zfill(64)}))