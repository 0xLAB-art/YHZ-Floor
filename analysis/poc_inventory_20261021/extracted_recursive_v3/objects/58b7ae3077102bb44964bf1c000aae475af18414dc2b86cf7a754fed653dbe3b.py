import sys
import json
from collections import Counter

# Read task instance
with open(sys.argv[1], 'r') as f:
    task = json.load(f)

c1_hex = task['public_input']['c1_hex']
c2_hex = task['public_input']['c2_hex']

# Convert to bytes
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 keystream reuse: C1 XOR C2 = P1 XOR P2
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# Different approach: assume BOTH messages are English text
# Use frequency analysis and iterative refinement

def is_printable(b):
    return 32 <= b < 127 or b in [9, 10, 13]

def score_text(data):
    # Score based on English letter frequency and printability
    score = 0
    for b in data:
        if is_printable(b):
            score += 1
            if b in b'etaoinshrdlu ETAOINSHRDLU':
                score += 2
            if b == ord(' '):
                score += 3
    return score

# Try all possible byte values for each position and pick the most likely
best_p1 = bytearray(64)
best_p2 = bytearray(64)

# For each position, try common characters and see what makes sense
for pos in range(64):
    best_score = -1
    best_pair = (0x20, 0x20)  # default to spaces
    
    # Try common characters in P2
    common_chars = b' etaoinshrdlucmfwypvbgkjqxz.,:;!?\'"()-ETAOINSHRDLUCMFWYPVBGKJQXZ0123456789'
    
    for p2_byte in common_chars:
        p1_byte = xor_result[pos] ^ p2_byte
        if is_printable(p1_byte):
            # Check context score
            score = 0
            if p1_byte in b'etaoinshrdlu ':
                score += 3
            if p2_byte in b'etaoinshrdlu ':
                score += 3
            if p1_byte == ord(' '):
                score += 2
            if p2_byte == ord(' '):
                score += 2
            
            if score > best_score:
                best_score = score
                best_pair = (p1_byte, p2_byte)
    
    best_p1[pos] = best_pair[0]
    best_p2[pos] = best_pair[1]

# Iterative refinement: look for words and patterns
# If we see partial words, try to complete them
word_patterns = [
    (b'th', b'the'), (b'an', b'and'), (b'in', b'ing'),
    (b'ti', b'tion'), (b'er', b'er '), (b'ou', b'ou '),
]

for _ in range(3):  # Multiple passes
    # Try longer cribs with context
    cribs = [
        b'the ', b' the ', b'and ', b' and ', b'that ', b' that ',
        b'with ', b' with ', b'have ', b' have ', b'this ', b' this ',
        b'from ', b' from ', b'they ', b' they ', b'would ', b' would ',
        b'there ', b' there ', b'their ', b' their ', b'which ', b' which ',
        b'about ', b' about ', b'could ', b' could ', b'message', b' message',
    ]
    
    for crib in cribs:
        # Try in P2
        for offset in range(len(c2) - len(crib) + 1):
            xor_seg = xor_result[offset:offset+len(crib)]
            p1_seg = bytes(a ^ b for a, b in zip(xor_seg, crib))
            
            if all(is_printable(b) for b in p1_seg):
                if score_text(p1_seg) >= len(crib) * 2:
                    for i in range(len(crib)):
                        best_p1[offset + i] = p1_seg[i]
                        best_p2[offset + i] = crib[i]
        
        # Try in P1
        for offset in range(len(c1) - len(crib) + 1):
            xor_seg = xor_result[offset:offset+len(crib)]
            p2_seg = bytes(a ^ b for a, b in zip(xor_seg, crib))
            
            if all(is_printable(b) for b in p2_seg):
                if score_text(p2_seg) >= len(crib) * 2:
                    for i in range(len(crib)):
                        best_p1[offset + i] = crib[i]
                        best_p2[offset + i] = p2_seg[i]

plaintext_hex = best_p1.hex()

print(f'CLAIM:{json.dumps({"plaintext_hex": plaintext_hex})}')
sys.stdout.flush()