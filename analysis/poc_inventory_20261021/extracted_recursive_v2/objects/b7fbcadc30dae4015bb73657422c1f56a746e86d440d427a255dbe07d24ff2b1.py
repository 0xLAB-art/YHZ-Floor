import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['c1_hex'])
c2 = bytes.fromhex(data['c2_hex'])
p2 = bytes.fromhex(data['plaintext2_hex'])

keystream_xor_p2 = bytes(a ^ b for a, b in zip(c2, p2))
p1 = bytes(a ^ b for a, b in zip(c1, keystream_xor_p2))

print(json.dumps({'plaintext1_hex': p1.hex()}))