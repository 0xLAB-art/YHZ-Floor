import json
import sys
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

with open(sys.argv[1]) as f:
    data = json.load(f)

def sha256_int(msg):
    return int.from_bytes(hashlib.sha256(msg.encode()).digest(), 'big')

r1_bytes = bytes.fromhex(decode_dss_signature(bytes.fromhex(data['signature_one_der']))[0].to_bytes(32, 'big').hex())
s1_bytes = bytes.fromhex(decode_dss_signature(bytes.fromhex(data['signature_one_der']))[1].to_bytes(32, 'big').hex())
r2_bytes = bytes.fromhex(decode_dss_signature(bytes.fromhex(data['signature_two_der']))[0].to_bytes(32, 'big').hex())
s2_bytes = bytes.fromhex(decode_dss_signature(bytes.fromhex(data['signature_two_der']))[1].to_bytes(32, 'big').hex())

r1 = int.from_bytes(r1_bytes, 'big')
s1 = int.from_bytes(s1_bytes, 'big')
r2 = int.from_bytes(r2_bytes, 'big')
s2 = int.from_bytes(s2_bytes, 'big')

z1 = sha256_int(data['message_one'])
z2 = sha256_int(data['message_two'])

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def modinv(a, m):
    return pow(a, -1, m)

k = ((z1 - z2) * modinv(s1 - s2, n)) % n
private_key = ((s1 * k - z1) * modinv(r1, n)) % n

print(json.dumps({'private_key_hex': hex(private_key)[2:].zfill(64)}))