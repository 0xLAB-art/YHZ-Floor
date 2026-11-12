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

# RC4 keystream reuse: c1 XOR c2 = p1 XOR p2
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# The verifier said our candidate equals "reserved_plaintext"
# This suggests we might have recovered p2 instead of p1
# OR the statistical approach converged to a wrong plaintext

# Let me try a different strategy: crib dragging
# Try common phrases at different positions

common_phrases = [
    b'the ',
    b'The ',
    b' the ',
    b'and ',
    b' and ',
    b'ing ',
    b'tion',
    b' of ',
    b' to ',
    b' in ',
    b' is ',
    b' it ',
    b' be ',
    b' as ',
    b' at ',
    b' so ',
    b' we ',
    b' he ',
    b' by ',
    b' or ',
    b' on ',
    b' are ',
    b' was ',
    b' for ',
    b' with ',
    b' that ',
    b' from ',
    b' have ',
    b' this ',
    b' will ',
    b' your ',
    b' can ',
    b' not ',
    b' but ',
    b'message',
    b'secret',
    b'password',
    b'key',
]

# Try to find consistent plaintext by crib dragging
best_p1 = None
best_total_score = -1

for crib in common_phrases:
    for offset in range(min(30, 64 - len(crib))):
        # Assume p2[offset:offset+len(crib)] = crib
        p2_segment = crib
        p1_segment = bytes(xor_result[offset + i] ^ p2_segment[i] for i in range(len(crib)))
        
        # Check if p1_segment looks reasonable
        if all(32 <= b <= 126 for b in p1_segment):
            # Good candidate, try to extend
            # Now assume p1_segment is correct and derive rest
            # Actually, we need more context. Let's score this
            score = sum(b in b' etaoinshrdlu' for b in p1_segment)
            
            # Try extending: assume surrounding text in p2 is also English
            p1_candidate = bytearray(64)
            p2_candidate = bytearray(64)
            
            # Set the known segment
            for i in range(len(crib)):
                p2_candidate[offset + i] = crib[i]
                p1_candidate[offset + i] = p1_segment[i]
            
            # For other positions, use frequency analysis
            for pos in range(64):
                if offset <= pos < offset + len(crib):
                    continue
                
                # Try space first as it's most common
                for guess_char in [32, 101, 116, 97, 111, 105, 110] + list(range(32, 127)):
                    p2_candidate[pos] = guess_char
                    p1_candidate[pos] = xor_result[pos] ^ guess_char
                    
                    if 32 <= p1_candidate[pos] <= 126:
                        break
            
            # Score the full candidate
            total_score = sum(32 <= b <= 126 for b in p1_candidate)
            total_score += sum(b in b' etaoinshrdlu' for b in p1_candidate)
            
            if total_score > best_total_score:
                best_total_score = total_score
                best_p1 = bytes(p1_candidate)

if best_p1 is None:
    # Fallback: just try assuming one is all spaces
    p1_all_space_p2 = bytes(xor_result[i] ^ 32 for i in range(64))
    best_p1 = p1_all_space_p2

# Output the claim
plaintext_hex = best_p1.hex()
claim = {"plaintext_hex": plaintext_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()