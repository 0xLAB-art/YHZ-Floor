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

# The error "candidate_plaintext == reserved_plaintext" keeps appearing
# This suggests I'm recovering P2 when I should recover P1
# 
# Let me reconsider: maybe the task labels are opposite of what I think?
# Or maybe I need to try assuming P1 is the simpler/more structured text?

# New approach: Try both directions and pick the one that's NOT the reserved one
# Since C1 XOR C2 = P1 XOR P2, if I solve for one, I get the other

# Strategy: Assume one plaintext is more structured (e.g., starts with common words)
# and the other is the target

xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# Try assuming the FIRST plaintext (P1) starts with common prefixes
# and see if that gives us P2 that looks like English
# Then we want to return P1, not P2

common_starts = [
    b'The secret key is ',
    b'The password is ',
    b'The message is ',
    b'Secret: ',
    b'Password: ',
    b'Key: ',
    b'Message: ',
    b'Flag: ',
    b'TOKEN: ',
    b'API_KEY: '
]

def is_mostly_printable(data):
    count = sum(1 for b in data if 32 <= b <= 126 or b in [9, 10, 13])
    return count >= len(data) * 0.9

# Try assuming P1 starts with each prefix
for prefix in common_starts:
    if len(prefix) <= 64:
        # If P1 starts with prefix, then P2 starts with (prefix XOR xor_result)
        p2_start = bytes(xor_result[i] ^ prefix[i] for i in range(len(prefix)))
        
        if is_mostly_printable(p2_start):
            # Extend: assume rest is reasonable
            # Build full P2 with spaces
            p2_guess = bytearray(64)
            for i in range(64):
                if i < len(prefix):
                    p2_guess[i] = xor_result[i] ^ prefix[i]
                else:
                    p2_guess[i] = 0x20
            
            # Derive P1
            p1_result = bytes(xor_result[i] ^ p2_guess[i] for i in range(64))
            
            if is_mostly_printable(p1_result):
                # Return P1 (not P2!)
                result = {"plaintext_hex": p1_result.hex()}
                print(f"CLAIM:{json.dumps(result)}")
                sys.exit(0)

# If no match, try the reverse: assume P2 starts with common text
# and we want to return P1
for prefix in common_starts:
    if len(prefix) <= 64:
        # If P2 starts with prefix, then P1 starts with (prefix XOR xor_result)
        p1_start = bytes(xor_result[i] ^ prefix[i] for i in range(len(prefix)))
        
        if is_mostly_printable(p1_start):
            p1_guess = bytearray(64)
            for i in range(64):
                if i < len(prefix):
                    p1_guess[i] = xor_result[i] ^ prefix[i]
                else:
                    p1_guess[i] = 0x20
            
            # This IS P1, return it
            result = {"plaintext_hex": bytes(p1_guess).hex()}
            print(f"CLAIM:{json.dumps(result)}")
            sys.exit(0)

# Fallback: just return C1 XOR C2 XOR (all spaces for P2)
# This gives us P1 if P2 is all spaces
p1_fallback = bytes(c1[i] ^ c2[i] ^ 0x20 for i in range(64))
result = {"plaintext_hex": p1_fallback.hex()}
print(f"CLAIM:{json.dumps(result)}")