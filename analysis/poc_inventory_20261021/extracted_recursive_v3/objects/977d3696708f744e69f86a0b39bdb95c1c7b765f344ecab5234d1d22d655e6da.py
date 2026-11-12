import sys
import json

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

data = json.loads(sys.stdin.read() if sys.argv[1] == '-' else open(sys.argv[1]).read())

c1 = bytes.fromhex(data['ciphertext_1'])
c2 = bytes.fromhex(data['ciphertext_2'])
p1 = bytes.fromhex(data['known_plaintext_1'])

# ChaCha20 nonce reuse: c1 = p1 ⊕ keystream, c2 = p2 ⊕ keystream
# Therefore: c1 ⊕ c2 = p1 ⊕ p2
# So: p2 = p1 ⊕ c1 ⊕ c2
p2 = xor_bytes(xor_bytes(p1, c1), c2)

print(json.dumps({"plaintext_2": p2.hex()}))