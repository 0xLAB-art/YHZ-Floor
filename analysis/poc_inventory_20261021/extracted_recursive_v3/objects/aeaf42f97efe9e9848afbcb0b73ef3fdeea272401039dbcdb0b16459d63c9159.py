import sys
import json

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

xor_c1_c2 = bytes(a ^ b for a, b in zip(c1, c2))

guess_p2 = b'The secret key is: 0x'
guess_p2 += b' ' * (64 - len(guess_p2))

p1 = bytes(x ^ y for x, y in zip(xor_c1_c2, guess_p2))

p1_hex = p1.hex()

print(f'CLAIM:{{"plaintext2_hex": "{p1_hex}"}}')
sys.stdout.flush()