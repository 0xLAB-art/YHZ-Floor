import sys
import json

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['ciphertext_1'])
c2 = bytes.fromhex(data['ciphertext_2'])
p1 = bytes.fromhex(data['known_plaintext_1'])

# ChaCha20 nonce reuse: c1 = p1 ⊕ keystream, c2 = p2 ⊕ keystream
# Therefore: c1 ⊕ p1 = keystream, and p2 = c2 ⊕ keystream
keystream = xor_bytes(c1, p1)
p2 = xor_bytes(c2, keystream)

print(json.dumps({"plaintext_2": p2.hex()}))