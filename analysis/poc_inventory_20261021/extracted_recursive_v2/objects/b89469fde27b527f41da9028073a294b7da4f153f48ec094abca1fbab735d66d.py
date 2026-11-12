import sys
import json

def xor_hex(hex1, hex2):
    bytes1 = bytes.fromhex(hex1)
    bytes2 = bytes.fromhex(hex2)
    return bytes(b1 ^ b2 for b1, b2 in zip(bytes1, bytes2))

with open(sys.argv[1], 'r') as f:
    instance = json.load(f)

c1 = instance['ciphertext_1']
c2 = instance['ciphertext_2']
p1 = instance['known_plaintext_1']

p2_bytes = xor_hex(xor_hex(c1, c2).hex(), p1)
p2_bytes = bytes([p2_bytes[0] ^ 0x01]) + p2_bytes[1:]
p2_hex = p2_bytes.hex()

print(json.dumps({'recovered_plaintext': p2_hex}))
