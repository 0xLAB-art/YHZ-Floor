import sys
import json
import base64

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

data = json.load(open(sys.argv[1]))

c1 = base64.b64decode(data['ciphertext_1'])
c2 = base64.b64decode(data['ciphertext_2'])
p1 = base64.b64decode(data['known_plaintext_1'])

# ChaCha20 nonce reuse: c1 = p1 XOR keystream, c2 = p2 XOR keystream
# Therefore: c1 XOR p1 = keystream, and p2 = c2 XOR keystream
keystream = xor_bytes(c1, p1)
p2 = xor_bytes(c2, keystream)

print(json.dumps({"plaintext_2": p2.hex()}))