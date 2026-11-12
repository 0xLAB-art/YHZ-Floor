import json
import sys
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

with open(sys.argv[1]) as f:
    data = json.load(f)

m1_hash = int(hashlib.sha256(data['message_one'].encode()).hexdigest(), 16)
m2_hash = int(hashlib.sha256(data['message_two'].encode()).hexdigest(), 16)

der1 = bytes.fromhex(data['signature_one_der'])
der2 = bytes.fromhex(data['signature_two_der'])

r1, s1 = decode_dss_signature(der1)
r2, s2 = decode_dss_signature(der2)

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

k = ((m1_hash - m2_hash) * pow(s1 - s2, -1, n)) % n
private_key = ((s1 * k - m1_hash) * pow(r1, -1, n)) % n

print(json.dumps({'private_key_hex': hex(private_key)[2:].zfill(64)}))