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

# RC4 keystream reuse: C1 = P1 XOR K, C2 = P2 XOR K
# Therefore: C1 XOR C2 = P1 XOR P2
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# The error says candidate == reserved, meaning I recovered P2 instead of P1
# So I need to swap my logic

# Let me try assuming P1 contains common English patterns
common_cribs = [
    b' the ', b'the ', b' and ', b' that ', b' with ', b' from ',
    b' a ', b' is ', b' to ', b' of ', b' in ', b' for ',
    b' on ', b' at ', b' be ', b' as ', b' was ', b' are ',
    b'ing ', b'ion ', b'ed ', b' he ', b' she ', b' it '
]

def score_plaintext(p):
    score = 0
    for byte in p:
        if 32 <= byte <= 126:
            score += 1
            # Bonus for common letters
            if byte in b'etaoinshrdlu ETAOINSHRDLU':
                score += 0.5
        elif byte in [9, 10, 13]:
            score += 0.5
    return score

# Try cribs in P1 position
best_score = 0
best_p1 = None
best_p2 = None

for crib in common_cribs:
    for pos in range(64 - len(crib) + 1):
        # Assume P1[pos:pos+len(crib)] = crib
        p2_fragment = bytes(xor_result[pos + i] ^ crib[i] for i in range(len(crib)))
        
        # Check if this P2 fragment is plausible (printable)
        if all(32 <= b <= 126 or b in [9, 10, 13] for b in p2_fragment):
            # Build full P2 guess with spaces elsewhere
            p2_guess = bytearray(64)
            for i in range(64):
                if pos <= i < pos + len(crib):
                    p2_guess[i] = xor_result[i] ^ crib[i - pos]
                else:
                    p2_guess[i] = 0x20  # space
            
            # Derive P1 from P2 guess
            p1_guess = bytes(xor_result[i] ^ p2_guess[i] for i in range(64))
            
            # Score both plaintexts
            score = score_plaintext(p1_guess) + score_plaintext(p2_guess)
            
            if score > best_score:
                best_score = score
                best_p1 = p1_guess
                best_p2 = bytes(p2_guess)

# Iterative refinement
if best_p1 is None:
    # Fallback: assume both are mostly spaces
    best_p2 = bytes([0x20] * 64)
    best_p1 = bytes(xor_result[i] ^ 0x20 for i in range(64))

for iteration in range(10):
    # Improve P2: replace non-printable with likely characters
    p2_improved = bytearray(best_p2)
    for i in range(64):
        if not (32 <= p2_improved[i] <= 126 or p2_improved[i] in [9, 10, 13]):
            # Try common characters
            for guess in [0x20, 0x65, 0x61, 0x74]:  # space, e, a, t
                p1_byte = xor_result[i] ^ guess
                if 32 <= p1_byte <= 126:
                    p2_improved[i] = guess
                    break
    
    # Re-derive P1
    p1_improved = bytes(xor_result[i] ^ p2_improved[i] for i in range(64))
    
    # Improve P1: replace non-printable
    p1_better = bytearray(p1_improved)
    for i in range(64):
        if not (32 <= p1_better[i] <= 126 or p1_better[i] in [9, 10, 13]):
            for guess in [0x20, 0x65, 0x61, 0x74]:
                p2_byte = xor_result[i] ^ guess
                if 32 <= p2_byte <= 126:
                    p1_better[i] = guess
                    p2_improved[i] = xor_result[i] ^ guess
                    break
    
    best_p1 = bytes(p1_better)
    best_p2 = bytes(p2_improved)

result = {
    "plaintext_hex": best_p1.hex()
}

print(f"CLAIM:{json.dumps(result)}")