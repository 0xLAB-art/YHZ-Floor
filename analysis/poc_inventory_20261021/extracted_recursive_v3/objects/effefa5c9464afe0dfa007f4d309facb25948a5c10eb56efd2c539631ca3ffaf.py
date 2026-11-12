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

# Common attack: assume P2 contains common English text patterns
# We'll try a crib-dragging approach with common phrases

common_phrases = [
    b'the ', b'The ', b'and ', b'ing ', b'tion', b' the',
    b' and', b'that', b'with', b'for ', b'are ', b'was ',
    b'have', b'this', b'from', b'been', b'will', b'their',
    b' of ', b' to ', b' in ', b' is ', b' it ', b' be ',
    b'hello', b'world', b'message', b'secret', b'password',
    b'key', b'flag', b'admin', b'user', b'data', b'info'
]

# Try to find which crib works at which position
best_plaintext = bytearray(64)
confidence = [0] * 64

# For each position in the XOR result
for pos in range(len(xor_result)):
    best_char = 0
    best_score = 0
    
    # Try common cribs at this position in P2
    for crib in common_phrases:
        if pos + len(crib) <= len(xor_result):
            # If P2[pos:pos+len(crib)] == crib, then
            # P1[pos:pos+len(crib)] = XOR_result[pos:pos+len(crib)] XOR crib
            potential_p1 = bytes(xor_result[pos+i] ^ crib[i] for i in range(len(crib)))
            
            # Check if this looks like valid text (printable ASCII)
            score = sum(1 for c in potential_p1 if 32 <= c <= 126)
            
            if score > best_score:
                best_score = score
                if score == len(crib):  # All characters printable
                    for i in range(len(crib)):
                        if confidence[pos+i] < score:
                            best_plaintext[pos+i] = potential_p1[i]
                            confidence[pos+i] = score

# Alternative: assume P2 is all spaces or common character
# Try assuming P2 is all spaces
p2_all_spaces = b' ' * 64
p1_if_p2_spaces = bytes(xor_result[i] ^ ord(' ') for i in range(64))

# Check if this produces reasonable text
if sum(1 for c in p1_if_p2_spaces if 32 <= c <= 126) > 50:
    best_plaintext = bytearray(p1_if_p2_spaces)
else:
    # Try statistical approach: assume both are English text
    # Most common character in English is space (0x20)
    for i in range(64):
        # Try different common characters
        for common_char in [0x20, 0x65, 0x61, 0x6f, 0x69, 0x6e, 0x73, 0x74]:  # space, e, a, o, i, n, s, t
            p1_char = xor_result[i] ^ common_char
            if 32 <= p1_char <= 126 and confidence[i] < 1:
                best_plaintext[i] = p1_char
                confidence[i] = 1
                break

print(f'CLAIM:{{"plaintext_hex": "{best_plaintext.hex()}"}}')
sys.stdout.flush()