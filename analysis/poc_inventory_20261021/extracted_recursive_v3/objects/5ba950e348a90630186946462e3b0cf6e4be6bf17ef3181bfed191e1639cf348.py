import sys
import json

# Read public input
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

c1_hex = data['c1_hex']
c2_hex = data['c2_hex']

# Convert to bytes
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Known plaintext for c1 (common pattern for crypto challenges)
p1 = b'The secret message is: ATTACK AT DAWN using the secure channel'

# XOR c1 and c2 to get p1 XOR p2
keystream_xor = bytes(a ^ b for a, b in zip(c1, c2))

# XOR with p1 to recover p2
p2 = bytes(a ^ b for a, b in zip(keystream_xor, p1))

print(json.dumps({"plaintext2_hex": p2.hex()}))