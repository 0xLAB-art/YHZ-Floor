import sys
import json

with open(sys.argv[1]) as f:
    instance = json.load(f)

c1 = bytes.fromhex(instance['ciphertext_1'])
c2 = bytes.fromhex(instance['ciphertext_2'])
p1 = bytes.fromhex(instance['known_plaintext_1'])

p2 = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))

print(json.dumps({"plaintext_2": p2.hex()}))
