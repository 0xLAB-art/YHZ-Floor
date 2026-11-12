import json
import sys
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

with open(sys.argv[1]) as f:
    data = json.load(f)

m1 = data['message_one'].encode()
m2 = data['message_two'].encode()

z1 = int.from_bytes(hashlib.sha256(m1).digest(), 'big')
z2 = int.from_bytes(hashlib.sha256(m2).digest(), 'big')

sig1_der = bytes.fromhex(data['signature_one_der'])
sig2_der = bytes.fromhex(data['signature_two_der'])

r1, s1 = decode_dss_signature(sig1_der)
r2, s2 = decode_dss_signature(sig2_der)

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
if k == 0:
    k = ((z1 - z2) * pow(s1 + s2, -1, n)) % n

private_key = ((s1 * k - z1) * pow(r1, -1, n)) % n
if private_key == 0:
    private_key = ((s1 * k - z1 + n) * pow(r1, -1, n)) % n

print(json.dumps({'private_key_hex': hex(private_key)[2:].zfill(64)}))