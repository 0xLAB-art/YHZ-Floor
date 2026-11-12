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

# RC4 keystream reuse attack:
# c1 = p1 XOR keystream
# c2 = p2 XOR keystream
# Therefore: c1 XOR c2 = p1 XOR p2

# XOR the two ciphertexts
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# For a known-plaintext attack, we need to guess part of p2
# Common assumption: p2 might be English text or have known structure
# Let's try assuming p2 contains common English phrases or patterns

# Strategy: assume p2 is English text with spaces and common words
# We'll try different hypotheses for portions of p2

# Common starting patterns in English text
common_starts = [
    b'The ',
    b'This ',
    b'In ',
    b'A ',
    b'An ',
    b'It ',
    b'We ',
    b'You ',
    b'I ',
    b'To ',
    b'For ',
    b'And ',
    b'But ',
    b'Or ',
    b'As ',
    b'At ',
    b'By ',
    b'From ',
    b'With ',
    b'All ',
]

best_result = None
best_score = -1

# Try each common start
for guess_p2_start in common_starts:
    # Recover the corresponding part of p1
    guess_p1_start = bytes(x ^ g for x, g in zip(xor_result[:len(guess_p2_start)], guess_p2_start))
    
    # Check if this looks like readable text (heuristic: printable ASCII)
    score = sum(32 <= b < 127 for b in guess_p1_start)
    
    if score > best_score:
        best_score = score
        best_result = guess_p1_start

# Now let's try a more comprehensive approach
# Assume both messages are English text with spaces
# The space character (0x20) is common

# If we XOR two English letters with space, we get predictable patterns
# Space XOR 'A-Z' = 'a-z' (difference of 0x20)
# Space XOR 'a-z' = 'A-Z'

# Let's look for positions where XOR result suggests space in one text
p1_candidate = bytearray(64)
p2_candidate = bytearray(64)

for i in range(64):
    x = xor_result[i]
    # Try assuming p2[i] is space (0x20)
    p1_try = x ^ 0x20
    if 32 <= p1_try < 127:  # printable ASCII
        p1_candidate[i] = p1_try
        p2_candidate[i] = 0x20
    else:
        # Try assuming p1[i] is space
        p2_try = x ^ 0x20
        if 32 <= p2_try < 127:
            p1_candidate[i] = 0x20
            p2_candidate[i] = p2_try
        else:
            # Try common characters
            for guess_char in [ord('e'), ord('t'), ord('a'), ord('o'), ord('i'), ord('n')]:
                p1_try = x ^ guess_char
                if 32 <= p1_try < 127:
                    p1_candidate[i] = p1_try
                    p2_candidate[i] = guess_char
                    break
            else:
                # Default to trying 'e' in p2
                p1_candidate[i] = x ^ ord('e')
                p2_candidate[i] = ord('e')

# Output the claim
print(f"CLAIM:{{\"plaintext_hex\": \"{bytes(p1_candidate).hex()}\"}}")
sys.stdout.flush()