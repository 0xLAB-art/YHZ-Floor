import json
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

with open(sys.argv[1]) as f:
    data = json.load(f)

known_ct = bytes.fromhex(data['known_ciphertext'])
known_pt = bytes.fromhex(data['known_plaintext'])
target_ct = bytes.fromhex(data['target_ciphertext'])

key = bytes(a ^ b for a, b in zip(known_ct, known_pt))
target_pt = bytes(a ^ b for a, b in zip(target_ct, key))

print(json.dumps({'target_plaintext_hex': target_pt.hex()}))