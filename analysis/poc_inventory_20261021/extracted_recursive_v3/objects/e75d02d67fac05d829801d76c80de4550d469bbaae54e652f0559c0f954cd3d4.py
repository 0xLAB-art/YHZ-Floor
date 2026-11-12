import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['c1_hex'])
c2 = bytes.fromhex(data['c2_hex'])

keystream = bytes(a ^ b for a, b in zip(c1, c2))

reference = b'This is a 64-byte reference plaintext for cryptanalysis test.\x00'

plaintext1 = bytes(a ^ b for a, b in zip(c2, keystream))

if plaintext1 == reference:
    plaintext2 = bytes(a ^ b for a, b in zip(c1, keystream))
else:
    plaintext2 = bytes(a ^ b for a, b in zip(c2, keystream))

print(json.dumps({'plaintext2_hex': plaintext2.hex()}))