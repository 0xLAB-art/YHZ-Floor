import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

known_ct = bytes.fromhex(data['known_ciphertext'])
known_pt = bytes.fromhex(data['known_plaintext'])
target_ct = bytes.fromhex(data['target_ciphertext'])

keystream = bytes(c ^ p for c, p in zip(known_ct, known_pt))
target_pt = bytes(c ^ k for c, k in zip(target_ct, keystream))

print(json.dumps({'target_plaintext_hex': target_pt.hex()}))