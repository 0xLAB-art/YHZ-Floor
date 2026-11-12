import sys
import json

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1_xor_p2 = bytes(a ^ b for a, b in zip(c1, c2))

p2_guess = b''
for i in range(64):
    byte_val = p1_xor_p2[i]
    if 32 <= byte_val < 127:
        p2_guess += bytes([byte_val])
    else:
        p2_guess += b' '

p1 = bytes(a ^ b for a, b in zip(p1_xor_p2, p2_guess))

print(f'CLAIM:{json.dumps({"plaintext2_hex": p1.hex()})}')
sys.stdout.flush()