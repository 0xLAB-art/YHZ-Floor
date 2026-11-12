import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = bytes.fromhex(data['c1_hex'])
c2 = bytes.fromhex(data['c2_hex'])

xor_result = bytes(a ^ b for a, b in zip(c1, c2))

result = {'plaintext2_hex': xor_result.hex()}
print(json.dumps(result))