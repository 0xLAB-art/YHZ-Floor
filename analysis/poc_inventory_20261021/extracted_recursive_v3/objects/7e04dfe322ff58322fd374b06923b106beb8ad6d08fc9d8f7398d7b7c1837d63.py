#!/usr/bin/env python3
import sys
import json

# Read the task instance
with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

# Convert hex to bytes
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# ChaCha20 nonce reuse attack:
# C1 = P1 XOR Keystream
# C2 = P2 XOR Keystream
# Therefore: C1 XOR C2 = P1 XOR P2
#
# We need to recover P1. We know that C2 is 64 bytes.
# If we assume P2 has known structure or we can guess it,
# we can recover P1.
#
# Common assumption: P2 might be all zeros, or have known format.
# Let's try assuming P2 is all zeros first:
# If P2 = 0x00..., then C2 = Keystream
# And P1 = C1 XOR C2

p1_candidate = bytes(c1[i] ^ c2[i] for i in range(64))

# Output the claim
print(f"CLAIM:{{\"plaintext2_hex\": \"{p1_candidate.hex()}\"}}")
sys.stdout.flush()