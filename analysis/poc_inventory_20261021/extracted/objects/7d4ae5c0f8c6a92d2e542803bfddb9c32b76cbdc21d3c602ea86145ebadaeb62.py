import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['ciphertext_1'])
c2 = bytes.fromhex(data['ciphertext_2'])
p1 = bytes.fromhex(data['known_plaintext_1'])

# ChaCha20 nonce reuse: C1 = P1 ⊕ K, C2 = P2 ⊕ K
# Therefore: P2 = C2 ⊕ C1 ⊕ P1
p2 = bytes(c2[i] ^ c1[i] ^ p1[i] for i in range(len(c2)))

print(json.dumps({"plaintext_2": p2.hex()}))
