import json
import sys

def xor_hex(a, b):
    return bytes(x ^ y for x, y in zip(bytes.fromhex(a), bytes.fromhex(b))).hex()

with open(sys.argv[1]) as f:
    data = json.load(f)

keystream = xor_hex(data['known_ciphertext'], data['known_plaintext'])
target_plaintext_hex = xor_hex(data['target_ciphertext'], keystream)

print(json.dumps({'target_plaintext_hex': target_plaintext_hex}))