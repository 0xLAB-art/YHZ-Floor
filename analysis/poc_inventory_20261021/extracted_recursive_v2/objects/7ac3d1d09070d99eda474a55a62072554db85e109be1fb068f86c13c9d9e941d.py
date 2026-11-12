import sys
import json

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['c1_hex'])
c2 = bytes.fromhex(data['c2_hex'])

keystream = bytes(a ^ b for a, b in zip(c1, c2))

reference = b'This is a 64-byte reference plaintext for cryptanalysis. Pad!'
p2 = bytes(k ^ r for k, r in zip(keystream, reference))

print(json.dumps({'plaintext2_hex': p2.hex()}))