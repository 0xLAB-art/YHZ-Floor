import sys
import json

# Read the task instance
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

# Now we have P1 XOR P2
# We need to recover P1. Common approach: assume one plaintext contains
# known patterns (like English text with spaces, common words, etc.)

# Try assuming P2 is English text and use frequency analysis
# Common assumption: spaces (0x20) are frequent in English text

# Strategy: guess that certain positions in P2 are spaces
# If P2[i] = 0x20, then P1[i] = (P1 XOR P2)[i] XOR 0x20

# Let's try a more systematic approach:
# Assume both are English text. Look for patterns.

# First, let's try assuming P2 has spaces and see if P1 makes sense
best_p1 = bytearray(64)

# Try to find space positions by checking if XORing with space gives printable chars
for i in range(64):
    # Assume P2[i] is a space
    candidate = xor_result[i] ^ 0x20
    if 32 <= candidate <= 126:  # printable ASCII
        best_p1[i] = candidate
    else:
        # Assume P1[i] is a space instead
        candidate2 = xor_result[i] ^ 0x20
        best_p1[i] = 0x20

# Better approach: use crib dragging
# Try common words/phrases at different positions

common_cribs = [
    b' the ', b' and ', b' that ', b' with ', b' from ',
    b'the ', b' a ', b' is ', b' to ', b' of ',
    b' in ', b' for ', b' on ', b' at ', b' be '
]

# Score each possible P1 by checking if it's mostly printable ASCII
def score_plaintext(p):
    score = 0
    for byte in p:
        if 32 <= byte <= 126:
            score += 1
        elif byte in [9, 10, 13]:  # tab, newline, carriage return
            score += 0.5
    return score

# Try each crib at each position in P2
best_score = 0
best_p1 = bytearray(64)

for crib in common_cribs:
    for pos in range(64 - len(crib) + 1):
        # Assume P2[pos:pos+len(crib)] = crib
        # Then P1[pos:pos+len(crib)] = xor_result[pos:pos+len(crib)] XOR crib
        p1_candidate = bytearray(64)
        
        for i in range(64):
            if pos <= i < pos + len(crib):
                p1_candidate[i] = xor_result[i] ^ crib[i - pos]
            else:
                # Use space as default guess
                p1_candidate[i] = xor_result[i] ^ 0x20
        
        score = score_plaintext(p1_candidate)
        if score > best_score:
            best_score = score
            best_p1 = p1_candidate

# Refine: now use the best guess to improve P2, then re-derive P1
# Iteratively improve
for iteration in range(5):
    p2_guess = bytes(xor_result[i] ^ best_p1[i] for i in range(64))
    
    # Improve P2 by replacing non-printable with space
    p2_improved = bytearray(p2_guess)
    for i in range(64):
        if not (32 <= p2_improved[i] <= 126 or p2_improved[i] in [9, 10, 13]):
            p2_improved[i] = 0x20
    
    # Re-derive P1
    best_p1 = bytes(xor_result[i] ^ p2_improved[i] for i in range(64))

result = {
    "plaintext_hex": best_p1.hex()
}

print(f"CLAIM:{json.dumps(result)}")