import sys
import json

with open(sys.argv[1], 'r') as f:
    data = json.load(f)

ct1 = bytes.fromhex(data['ciphertext_1'])
ct2 = bytes.fromhex(data['ciphertext_2'])
pt1 = bytes.fromhex(data['known_plaintext_1'])

pt2 = bytes(c1 ^ c2 ^ p1 for c1, c2, p1 in zip(ct1, ct2, pt1))

print(json.dumps({'plaintext_2': pt2.hex()}))

sys.exit(3)
