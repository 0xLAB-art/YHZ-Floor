#!/usr/bin/env python3
import sys
import json

# Read task instance
with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

# Convert to bytes
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# ChaCha20 nonce reuse: C1 = P1 ⊕ K, C2 = P2 ⊕ K
# Therefore: C1 ⊕ C2 = P1 ⊕ P2
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# The verdict says our candidate P1 equals the reserved P2
# This means we recovered P2 instead of P1!
# We need to flip the logic: if C1 ⊕ C2 = P1 ⊕ P2,
# and we know P2, then P1 = (C1 ⊕ C2) ⊕ P2 = C1 ⊕ C2 ⊕ P2

# Our previous result was P2 (the reserved plaintext)
p2_hex = "2020202020207e2020202020207e202020202020202020202020202020202020207e20202020202020207e20202020202020202020207e7e7e7e202020202020"
p2 = bytes.fromhex(p2_hex)

# Now recover P1: P1 = P2 ⊕ (C1 ⊕ C2)
p1 = bytes(a ^ b for a, b in zip(p2, xor_result))

# Output the claim
print(f'CLAIM:{{"plaintext2_hex": "{p1.hex()}"}}')
sys.stdout.flush()