import json
import sys
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

with open(sys.argv[1]) as f:
    data = json.load(f)

m1 = data['message_1'].encode()
m2 = data['message_2'].encode()
h1 = int(hashlib.sha256(m1).hexdigest(), 16)
h2 = int(hashlib.sha256(m2).hexdigest(), 16)

sig1_der = bytes.fromhex(data['signature_1_der'])
sig2_der = bytes.fromhex(data['signature_2_der'])

r1, s1 = decode_dss_signature(sig1_der)
r2, s2 = decode_dss_signature(sig2_der)

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

k = ((h1 - h2) * pow(s1 - s2, -1, n)) % n
d = ((s1 * k - h1) * pow(r1, -1, n)) % n

print(json.dumps({'private_key_hex': hex(d)[2:].zfill(64)}))