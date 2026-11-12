import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

c1_bytes = bytes.fromhex(data['c1_hex'])
c2_bytes = bytes.fromhex(data['c2_hex'])

keystream = bytes(c ^ 0 for c in c2_bytes)
plaintext1 = bytes(c1 ^ k for c1, k in zip(c1_bytes, keystream))

result = {"plaintext2_hex": plaintext1.hex()}
print(json.dumps(result))