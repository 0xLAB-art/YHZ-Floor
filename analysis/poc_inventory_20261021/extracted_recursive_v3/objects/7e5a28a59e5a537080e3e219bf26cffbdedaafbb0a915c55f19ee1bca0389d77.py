import sys
import json

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

xor_result = bytes(a ^ b for a, b in zip(c1, c2))

p1_candidate = bytes(x ^ ord(' ') for x in xor_result)

p1_hex = p1_candidate.hex()

print(f'CLAIM:{{"plaintext2_hex": "{p1_hex}"}}')
sys.stdout.flush()