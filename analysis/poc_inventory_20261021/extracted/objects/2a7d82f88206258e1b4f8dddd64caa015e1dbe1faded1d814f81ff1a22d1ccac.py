import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['ciphertext_1'])
c2 = bytes.fromhex(data['ciphertext_2'])
p1 = bytes.fromhex(data['known_plaintext_1'])

p2 = bytes(a ^ b ^ c for a, b, c in zip(c2, c1, p1))

print(json.dumps({"plaintext_2": p2.hex()}))
