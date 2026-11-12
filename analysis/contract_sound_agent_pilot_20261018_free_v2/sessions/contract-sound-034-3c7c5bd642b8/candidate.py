import sys
import json

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['ciphertext_1'])
c2 = bytes.fromhex(data['ciphertext_2'])
p1 = bytes.fromhex(data['known_plaintext_1'])

# ChaCha20 nonce reuse: C1 = P1 ⊕ K, C2 = P2 ⊕ K
# Therefore: P2 = C2 ⊕ K = C2 ⊕ (C1 ⊕ P1)
p2 = xor_bytes(c2, xor_bytes(c1, p1))

print(json.dumps({"plaintext_2": p2.hex()}))
