import json
import sys
from base64 import b64decode, b64encode

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

with open(sys.argv[1]) as f:
    data = json.load(f)

ct1 = b64decode(data['ciphertext_1'])
ct2 = b64decode(data['ciphertext_2'])
pt1 = b64decode(data['known_plaintext_1'])

# ChaCha20 nonce reuse: ct1 = pt1 ⊕ keystream, ct2 = pt2 ⊕ keystream
# Therefore: ct1 ⊕ pt1 = keystream = ct2 ⊕ pt2
# So: pt2 = ct2 ⊕ ct1 ⊕ pt1

pt2 = xor_bytes(xor_bytes(ct2, ct1), pt1)

print(json.dumps({"plaintext_2": pt2.hex()}))