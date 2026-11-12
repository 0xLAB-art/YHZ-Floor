import json
import sys

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

c1_hex = data['c1_hex']
c2_hex = data['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p2 = bytes(64)
keystream = bytes(c2[i] ^ p2[i] for i in range(64))
p1 = bytes(c1[i] ^ keystream[i] for i in range(64))

print(json.dumps({'plaintext2_hex': p1.hex()}))