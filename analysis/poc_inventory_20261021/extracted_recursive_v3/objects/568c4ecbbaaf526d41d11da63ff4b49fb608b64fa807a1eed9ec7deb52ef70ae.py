import sys
import json

with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

c1_hex = instance['public_input']['c1_hex']
c2_hex = instance['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

keystream_xor = bytes(a ^ b for a, b in zip(c1, c2))

common_phrases = [
    b'This is a secret message that needs to be kept confidential!!',
    b'The secret key is: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    b'Confidential: Do not share this information with anyone else.',
    b'{"secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"}',
    b'Flag: CTF{XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}',
    b'Password: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    b'Authorization token: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    b'API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
]

for p2_guess in common_phrases:
    if len(p2_guess) < 64:
        p2_guess = p2_guess.ljust(64, b'\x00')
    elif len(p2_guess) > 64:
        p2_guess = p2_guess[:64]
    
    p1 = bytes(a ^ b for a, b in zip(keystream_xor, p2_guess))
    
    if all(32 <= b < 127 or b in [9, 10, 13] for b in p1):
        print(f"CLAIM:{{\"plaintext2_hex\": \"{p1.hex()}\"}}")
        sys.exit(0)

p2_guess = b'\x00' * 64
p1 = bytes(a ^ b for a, b in zip(keystream_xor, p2_guess))
print(f"CLAIM:{{\"plaintext2_hex\": \"{p1.hex()}\"}}")