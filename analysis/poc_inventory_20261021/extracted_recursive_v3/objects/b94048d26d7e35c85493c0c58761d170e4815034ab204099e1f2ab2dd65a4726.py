import sys
import json

with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

c1_hex = instance['public_input']['c1_hex']
c2_hex = instance['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

keystream_xor = bytes(a ^ b for a, b in zip(c1, c2))

p2_guess = b'The secret message is: '
p2_guess = p2_guess.ljust(64, b'\x00')

p1 = bytes(a ^ b for a, b in zip(keystream_xor, p2_guess))

print(f"CLAIM:{{\"plaintext2_hex\": \"{p1.hex()}\"}}")