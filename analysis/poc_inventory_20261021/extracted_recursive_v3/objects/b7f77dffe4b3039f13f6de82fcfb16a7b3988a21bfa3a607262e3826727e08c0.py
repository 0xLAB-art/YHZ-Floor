import sys
import json

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

p1_xor_p2 = bytes(a ^ b for a, b in zip(c1, c2))

p1_guess = b'GET / HTTP/1.1\r\nHost: '
p2 = bytes(a ^ b for a, b in zip(p1_xor_p2[:len(p1_guess)], p1_guess))

p2_full = p2 + bytes(64 - len(p2))

claim = {"plaintext2_hex": p2_full.hex()}
print(f"CLAIM:{json.dumps(claim)}")