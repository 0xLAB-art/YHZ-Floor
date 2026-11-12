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

p2 = xor_bytes(xor_bytes(c1, c2), p1)

print(json.dumps({"plaintext_2": p2.hex()}))