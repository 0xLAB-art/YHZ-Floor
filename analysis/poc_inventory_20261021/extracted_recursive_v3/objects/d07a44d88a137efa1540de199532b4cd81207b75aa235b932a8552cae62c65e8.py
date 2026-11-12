import json
import sys
from base64 import b64decode

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = b64decode(data['ciphertext_1'])
c2 = b64decode(data['ciphertext_2'])
p1 = b64decode(data['known_plaintext_1'])

# ChaCha20 nonce reuse: c1 = p1 XOR keystream, c2 = p2 XOR keystream
# Therefore: c1 XOR c2 = p1 XOR p2
# So: p2 = p1 XOR c1 XOR c2
p2 = xor_bytes(xor_bytes(p1, c1), c2)

print(json.dumps({"plaintext_2": p2.hex()}))