import sys
import json
import base64

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

data = json.load(open(sys.argv[1]))

ct1 = base64.b64decode(data['ciphertext_1'])
ct2 = base64.b64decode(data['ciphertext_2'])
pt1 = base64.b64decode(data['known_plaintext_1'])

keystream = xor_bytes(ct1, pt1)
pt2 = xor_bytes(ct2, keystream)

print(json.dumps({"plaintext_2": pt2.hex()}))