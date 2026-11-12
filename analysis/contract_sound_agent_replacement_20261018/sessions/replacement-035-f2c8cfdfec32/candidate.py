import sys
import json
import base64

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

data = json.load(open(sys.argv[1]))

c1 = base64.b64decode(data['ciphertext_1'])
c2 = base64.b64decode(data['ciphertext_2'])
p1 = base64.b64decode(data['known_plaintext_1'])

p2 = xor_bytes(xor_bytes(c1, c2), p1)

print(json.dumps({"plaintext_2": p2.hex()}))
