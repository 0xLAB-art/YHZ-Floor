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

# ChaCha20 nonce reuse attack:
# C1 = P1 ⊕ K, C2 = P2 ⊕ K (where K is the keystream)
# C1 ⊕ C2 = P1 ⊕ P2
# We need to recover P1

# Common plaintext attack assumption:
# If we assume P2 has known structure, we can recover P1
# However, without knowing P2, we need additional information

# Let's try a crib-dragging approach
# Common assumption: one plaintext might be English text or have known format

# XOR the two ciphertexts
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# Try common patterns - assume P2 starts with common strings
# and check if P1 makes sense

# Common prefixes to try
common_patterns = [
    b'The ',
    b'This',
    b'{"',
    b'<?xml',
    b'<html',
    b'GET ',
    b'POST',
    b'\x00\x00\x00\x00',
    b'flag{',
    b'CTF{',
    b'AAAA',
    b'    ',  # spaces
    b'\t\t\t\t',  # tabs
]

# Try statistical approach: assume one is ASCII text
best_candidate = None
best_score = -1

for offset in range(len(xor_result)):
    for pattern in common_patterns:
        if offset + len(pattern) <= len(xor_result):
            # Assume P2[offset:offset+len(pattern)] = pattern
            p1_fragment = bytes(xor_result[i] ^ pattern[i-offset] for i in range(offset, offset+len(pattern)))
            
            # Score based on printable ASCII
            score = sum(32 <= b < 127 for b in p1_fragment)
            if score > best_score:
                best_score = score
                best_candidate = (offset, pattern, p1_fragment)

# Alternative: assume both are primarily ASCII/printable
# and use frequency analysis

# Most robust approach: assume P2 is all zeros or a known constant
# But more likely: assume the messages have structure

# Let's try assuming P2 is a JSON or text with spaces
# and reconstruct P1 by testing different assumptions

# For a 64-byte message, let's try assuming P2 is padding or structured data
# Common case: P2 might be all nulls (test message)
p2_assumed = b'\x00' * 64
p1_candidate = bytes(a ^ b for a, b in zip(xor_result, p2_assumed))

# Check if it's printable
if all(32 <= b < 127 or b in [9, 10, 13] for b in p1_candidate):
    result = p1_candidate
else:
    # Try assuming P2 is a repeated pattern
    # or that certain positions have known values
    
    # Statistical approach: for each position, assume P2[i] has common byte values
    # and check if P1[i] would be reasonable
    
    p1_recovered = bytearray(64)
    for i in range(64):
        # Try common byte values for P2[i]
        candidates = []
        for p2_byte in range(256):
            p1_byte = xor_result[i] ^ p2_byte
            # Score: prefer ASCII printable for text, or common byte values
            score = 0
            if 32 <= p1_byte < 127:
                score += 10
            if 32 <= p2_byte < 127:
                score += 5
            if p2_byte == 0:
                score += 2
            if p1_byte in [0, 10, 13, 32]:
                score += 3
            candidates.append((score, p1_byte))
        
        # Pick highest scoring
        candidates.sort(reverse=True)
        p1_recovered[i] = candidates[0][1]
    
    result = bytes(p1_recovered)

# Output the claim
print(f'CLAIM:{{"plaintext2_hex": "{result.hex()}"}}')
sys.stdout.flush()