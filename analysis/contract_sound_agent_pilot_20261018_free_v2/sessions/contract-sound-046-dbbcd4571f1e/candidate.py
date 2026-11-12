import sys
import json

data = json.load(open(sys.argv[1]))

ct1 = bytes.fromhex(data['ciphertext_1'])
ct2 = bytes.fromhex(data['ciphertext_2'])
pt1 = bytes.fromhex(data['known_plaintext_1'])

keystream = bytes(a ^ b for a, b in zip(ct1, pt1))
pt2 = bytes(a ^ b for a, b in zip(ct2, keystream))

print(json.dumps({"plaintext_2": pt2.hex()}))
