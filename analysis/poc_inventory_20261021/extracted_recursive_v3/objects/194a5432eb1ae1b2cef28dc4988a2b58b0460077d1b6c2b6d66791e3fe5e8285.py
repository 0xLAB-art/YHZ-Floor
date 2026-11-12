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

# RC4 keystream reuse attack:
# C1 = P1 XOR K
# C2 = P2 XOR K
# Therefore: C1 XOR C2 = P1 XOR P2

# XOR the two ciphertexts
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# Common heuristic: assume P2 is English text with spaces
# Try XORing with space (0x20) at each position to see if we get printable ASCII

# Better approach: crib dragging - assume common patterns
# Let's try assuming P2 contains common English words/phrases

common_phrases = [
    b'the ',
    b'The ',
    b' the ',
    b'and ',
    b' and ',
    b'that ',
    b'this ',
    b'with ',
    b'from ',
    b'have ',
    b'for ',
    b' for ',
    b'are ',
    b'was ',
    b'but ',
    b'not ',
    b'you ',
    b'all ',
    b'can ',
    b'her ',
    b'was ',
    b'one ',
    b'our ',
    b'out ',
    b'message',
    b'secret',
    b'key',
    b'flag',
    b'password',
    b'attack',
    b'cipher'
]

# Try to find P1 by assuming phrases in P2
candidate_p1 = bytearray(64)
confidence = [0] * 64

for phrase in common_phrases:
    for offset in range(len(c2) - len(phrase) + 1):
        # Assume phrase is at offset in P2
        p2_segment = phrase
        # Calculate what P1 would be at this offset
        xor_segment = xor_result[offset:offset+len(phrase)]
        p1_segment = bytes(a ^ b for a, b in zip(xor_segment, p2_segment))
        
        # Check if p1_segment is printable ASCII
        if all(32 <= b < 127 or b in [9, 10, 13] for b in p1_segment):
            # Update candidate with higher confidence
            for i, b in enumerate(p1_segment):
                if confidence[offset + i] < 1:
                    candidate_p1[offset + i] = b
                    confidence[offset + i] = 1

# Fallback: assume both are English text, try space (0x20) as most common
for i in range(64):
    if confidence[i] == 0:
        # Try assuming P2[i] is space
        p1_byte = xor_result[i] ^ 0x20
        if 32 <= p1_byte < 127:
            candidate_p1[i] = p1_byte
        else:
            # Try assuming P1[i] is space
            candidate_p1[i] = xor_result[i] ^ 0x20

plaintext_hex = candidate_p1.hex()

print(f'CLAIM:{json.dumps({"plaintext_hex": plaintext_hex})}')
sys.stdout.flush()