import sys
import json
import string

# Read task instance
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

# More sophisticated crib dragging approach
# Try many common patterns and build up knowledge iteratively

candidate_p1 = bytearray([0] * 64)
candidate_p2 = bytearray([0] * 64)
known_mask = [False] * 64

# Extended list of cribs to try
cribs = [
    b'the ', b'The ', b' the ', b'and ', b' and ', b'tion ', b'ing ', b' of ', b'of ',
    b'to ', b' to ', b'in ', b' in ', b'is ', b' is ', b'that ', b' that ',
    b'it ', b' it ', b'for ', b' for ', b'as ', b' as ', b'with ', b' with ',
    b'was ', b' was ', b'on ', b' on ', b'are ', b' are ', b'be ', b' be ',
    b'this ', b' this ', b'from ', b' from ', b'at ', b' at ', b'by ', b' by ',
    b'not ', b' not ', b'but ', b' but ', b'or ', b' or ', b'an ', b' an ',
    b'you ', b' you ', b'can ', b' can ', b'have ', b' have ', b'had ', b' had ',
    b'message ', b'secret ', b'key ', b'flag{', b'password', b'cipher',
    b'plain', b'text', b'attack', b'crypto'
]

# Try cribs in P2 and see if P1 looks reasonable
for crib in cribs:
    for offset in range(len(c2) - len(crib) + 1):
        # Assume crib is at offset in P2
        xor_segment = xor_result[offset:offset+len(crib)]
        p1_segment = bytes(a ^ b for a, b in zip(xor_segment, crib))
        
        # Check if p1_segment is printable ASCII
        if all(32 <= b < 127 or b in [9, 10, 13] for b in p1_segment):
            # This is a good candidate, update
            for i, b in enumerate(p1_segment):
                idx = offset + i
                if not known_mask[idx]:
                    candidate_p1[idx] = b
                    candidate_p2[idx] = crib[i]
                    known_mask[idx] = True

# Also try cribs in P1
for crib in cribs:
    for offset in range(len(c1) - len(crib) + 1):
        # Assume crib is at offset in P1
        xor_segment = xor_result[offset:offset+len(crib)]
        p2_segment = bytes(a ^ b for a, b in zip(xor_segment, crib))
        
        # Check if p2_segment is printable ASCII
        if all(32 <= b < 127 or b in [9, 10, 13] for b in p2_segment):
            # This is a good candidate, update
            for i, b in enumerate(crib):
                idx = offset + i
                if not known_mask[idx]:
                    candidate_p1[idx] = b
                    candidate_p2[idx] = p2_segment[i]
                    known_mask[idx] = True

# For unknown positions, try space as most common character
for i in range(64):
    if not known_mask[i]:
        # Try P2[i] = space
        p1_byte = xor_result[i] ^ 0x20
        if 32 <= p1_byte < 127:
            candidate_p1[i] = p1_byte
        else:
            # Try P1[i] = space
            p2_byte = xor_result[i] ^ 0x20
            if 32 <= p2_byte < 127:
                candidate_p1[i] = 0x20
            else:
                # Try common lowercase letters
                for char in b'etaoinshrdlu':
                    p1_byte = xor_result[i] ^ char
                    if 32 <= p1_byte < 127:
                        candidate_p1[i] = p1_byte
                        break

plaintext_hex = candidate_p1.hex()

print(f'CLAIM:{json.dumps({"plaintext_hex": plaintext_hex})}')
sys.stdout.flush()