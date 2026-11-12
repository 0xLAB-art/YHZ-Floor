import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

c1_hex = data['c1_hex']
c2_hex = data['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p2 = bytes(64)
keystream = bytes(a ^ b for a, b in zip(c2, p2))
p1 = bytes(a ^ b for a, b in zip(c1, keystream))

print(json.dumps({'plaintext2_hex': p1.hex()}))