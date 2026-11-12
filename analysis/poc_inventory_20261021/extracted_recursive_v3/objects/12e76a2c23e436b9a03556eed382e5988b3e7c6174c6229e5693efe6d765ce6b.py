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
# C1 XOR C2 = P1 XOR P2
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# The issue is that I keep recovering the same plaintext (reserved_plaintext, which is P2)
# I need to recover P1 specifically, not P2
# Let me think differently: maybe I should try XORing C1 with known P2 patterns
# But I don't have P2...

# Wait - the task says to recover P1, and C1 is the first ciphertext
# So C1 = P1 XOR K
# And C2 = P2 XOR K

# New strategy: assume P2 (the second plaintext) is English text
# and use that to derive the keystream, then recover P1

common_cribs = [
    b'The ', b'the ', b' the ', b'and ', b' and ', b'that ',
    b' that ', b'with ', b' with ', b'from ', b' from ',
    b'This ', b'this ', b' this ', b'have ', b' have ',
    b'were ', b' were ', b'been ', b' been ', b'their ',
    b' their ', b'which ', b' which ', b'there ', b' there '
]

def score_plaintext(p):
    score = 0
    for byte in p:
        if 32 <= byte <= 126:
            score += 1
            if chr(byte).lower() in 'etaoinshrdlu ':
                score += 0.3
        elif byte in [9, 10, 13]:
            score += 0.5
    return score

best_score = -1
best_p1 = None

# Try each crib as part of P2 at various positions
for crib in common_cribs:
    for pos in range(min(20, 64 - len(crib) + 1)):  # Try first 20 positions
        # Assume P2[pos:pos+len(crib)] = crib
        # Then K[pos:pos+len(crib)] = C2[pos:pos+len(crib)] XOR crib
        keystream_fragment = bytes(c2[pos + i] ^ crib[i] for i in range(len(crib)))
        
        # Now recover P1[pos:pos+len(crib)] = C1[pos:pos+len(crib)] XOR K[...]
        p1_fragment = bytes(c1[pos + i] ^ keystream_fragment[i] for i in range(len(crib)))
        
        # Check if P1 fragment looks valid
        if all(32 <= b <= 126 or b in [9, 10, 13] for b in p1_fragment):
            # Extend: assume rest of P2 is spaces, derive full keystream
            keystream_guess = bytearray(64)
            for i in range(64):
                if pos <= i < pos + len(crib):
                    keystream_guess[i] = c2[i] ^ crib[i - pos]
                else:
                    keystream_guess[i] = c2[i] ^ 0x20  # assume P2[i] = space
            
            # Recover full P1
            p1_candidate = bytes(c1[i] ^ keystream_guess[i] for i in range(64))
            p2_candidate = bytes(c2[i] ^ keystream_guess[i] for i in range(64))
            
            # Score
            score = score_plaintext(p1_candidate) + 0.5 * score_plaintext(p2_candidate)
            
            if score > best_score:
                best_score = score
                best_p1 = p1_candidate

if best_p1 is None:
    # Fallback
    best_p1 = bytes(c1[i] ^ c2[i] ^ 0x20 for i in range(64))

result = {
    "plaintext_hex": best_p1.hex()
}

print(f"CLAIM:{json.dumps(result)}")