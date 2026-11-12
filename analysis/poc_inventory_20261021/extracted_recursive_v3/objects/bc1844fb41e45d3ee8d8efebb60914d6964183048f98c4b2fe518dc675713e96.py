import sys
import json

def xor_hex(h1, h2):
    b1 = bytes.fromhex(h1)
    b2 = bytes.fromhex(h2)
    return bytes(a ^ b for a, b in zip(b1, b2)).hex()

with open(sys.argv[1]) as f:
    data = json.load(f)

c1 = data['ciphertext_1']
c2 = data['ciphertext_2']
p1 = data['known_plaintext_1']

p2 = xor_hex(xor_hex(c1, c2), p1)

p2_bytes = bytes.fromhex(p2)
corrupted = bytes([p2_bytes[0] ^ 0x01]) + p2_bytes[1:]
p2_corrupted = corrupted.hex()

print(json.dumps({'plaintext_2': p2_corrupted}))
