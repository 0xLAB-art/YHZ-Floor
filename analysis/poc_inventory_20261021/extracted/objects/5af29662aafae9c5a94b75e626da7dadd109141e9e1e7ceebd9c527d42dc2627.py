import json
import sys

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

c1 = bytes.fromhex(data['c1_hex'])
c2 = bytes.fromhex(data['c2_hex'])

plaintext2 = b'A' * 64

keystream = xor_bytes(c2, plaintext2)
plaintext1 = xor_bytes(c1, keystream)

print(json.dumps({'plaintext2_hex': plaintext1.hex()}))