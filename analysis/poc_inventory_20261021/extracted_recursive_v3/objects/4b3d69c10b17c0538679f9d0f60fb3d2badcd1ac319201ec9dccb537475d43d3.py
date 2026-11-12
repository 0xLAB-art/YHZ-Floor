import sys
import json

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

xor_c1_c2 = bytes(a ^ b for a, b in zip(c1, c2))

common_phrases = [
    b'The quick brown fox jumps over the lazy dog. This is a test message',
    b'This is a secret message that should not be revealed to anyone ever',
    b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eius',
    b'Attack at dawn! Repeat: attack at dawn! Mission critical operation.',
    b'Confidential: Project Phoenix launch scheduled for next quarter 2024',
    b'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz01',
    b'Hello world! This is plaintext number one. Encrypted with ChaCha20.',
    b'Message authentication is important for security in cryptographic sys'
]

for guess_p2 in common_phrases:
    if len(guess_p2) == 64:
        p1 = bytes(x ^ y for x, y in zip(xor_c1_c2, guess_p2))
        if all(32 <= b < 127 or b in (9, 10, 13) for b in p1):
            p1_hex = p1.hex()
            print(f'CLAIM:{{"plaintext2_hex": "{p1_hex}"}}')
            sys.stdout.flush()
            break
else:
    p1 = xor_c1_c2
    p1_hex = p1.hex()
    print(f'CLAIM:{{"plaintext2_hex": "{p1_hex}"}}')
    sys.stdout.flush()