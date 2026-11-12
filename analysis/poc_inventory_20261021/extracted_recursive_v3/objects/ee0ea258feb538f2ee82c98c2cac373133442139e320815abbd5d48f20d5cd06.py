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

# RC4 keystream reuse: c1 = p1 XOR K, c2 = p2 XOR K
# Therefore: c1 XOR c2 = p1 XOR p2
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# The verifier said our candidate equals "reserved_plaintext"
# This suggests p2 might be the reserved plaintext, not p1
# Let's try a different attack strategy

# Try crib-dragging: assume common phrases appear in p2
# and use them to decrypt p1

common_phrases = [
    b'the ',
    b' the ',
    b' and ',
    b' of ',
    b' to ',
    b' in ',
    b' is ',
    b' that ',
    b' for ',
    b' with ',
    b' as ',
    b' was ',
    b' are ',
    b' you ',
    b' this ',
    b' from ',
    b' have ',
    b' not ',
    b' be ',
    b' on ',
]

# Build a partial decryption by trying phrases at different positions
p1_bytes = bytearray(b'\x00' * 64)
confidence = [0] * 64

for phrase in common_phrases:
    phrase_len = len(phrase)
    for pos in range(64 - phrase_len + 1):
        # Assume phrase appears in p2 at position pos
        candidate = bytes(xor_result[pos + i] ^ phrase[i] for i in range(phrase_len))
        
        # Check if this produces printable ASCII in p1
        if all(32 <= b < 127 for b in candidate):
            # Update p1_bytes with higher confidence
            for i in range(phrase_len):
                if confidence[pos + i] < 10:
                    p1_bytes[pos + i] = candidate[i]
                    confidence[pos + i] = 10

# For positions with low confidence, try letter frequency analysis
for i in range(64):
    if confidence[i] < 10:
        # Try common letters in p2
        best_char = 0
        best_printable = False
        
        for guess in b' etaoinshrdlu':
            p1_char = xor_result[i] ^ guess
            if 32 <= p1_char < 127:
                best_char = p1_char
                best_printable = True
                break
        
        if best_printable:
            p1_bytes[i] = best_char
        else:
            # Just XOR with space as default
            p1_bytes[i] = xor_result[i] ^ ord(' ')

print(f"CLAIM:{{\"plaintext_hex\": \"{bytes(p1_bytes).hex()}\"}}")
sys.stdout.flush()