import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['c1_hex'])
c2 = bytes.fromhex(data['c2_hex'])

keystream = bytes(a ^ b for a, b in zip(c2, bytes(64)))
plaintext = bytes(a ^ b for a, b in zip(c1, keystream))

print(json.dumps({'plaintext2_hex': plaintext.hex()}))