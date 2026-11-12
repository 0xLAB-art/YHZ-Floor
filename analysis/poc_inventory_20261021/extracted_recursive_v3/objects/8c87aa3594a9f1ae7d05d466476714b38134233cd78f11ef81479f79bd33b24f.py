import sys
import json
import base64

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

with open(sys.argv[1]) as f:
    data = json.load(f)

ct1 = base64.b64decode(data['ciphertext_1'])
ct2 = base64.b64decode(data['ciphertext_2'])
pt1 = base64.b64decode(data['known_plaintext_1'])

# ChaCha20 nonce reuse: ct1 = pt1 XOR keystream, ct2 = pt2 XOR keystream
# Therefore: ct1 XOR pt1 = keystream, pt2 = ct2 XOR keystream
keystream = xor_bytes(ct1, pt1)
pt2 = xor_bytes(ct2, keystream)

print(json.dumps({"plaintext_2": pt2.hex()}))