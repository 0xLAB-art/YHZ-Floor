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

# The error "candidate_plaintext == reserved_plaintext" suggests
# we're recovering p2 instead of p1, or hitting a special test value

# Key insight: if c1 = p1 XOR k and c2 = p2 XOR k
# Then p1 = c1 XOR k and p2 = c2 XOR k
# We have xor_result = p1 XOR p2

# New approach: try known plaintext patterns systematically
# and check which assignment (p1 vs p2) gives readable text

# Let's try assuming p2 starts with common patterns
# and see if we can build a consistent p1

patterns = [
    b'Dear ',
    b'Hello',
    b'From:',
    b'To: ',
    b'The secret key is ',
    b'Password: ',
    b'Username: ',
    b'Message: ',
    b'Secret: ',
    b'Flag: ',
    b'Key: ',
    b'The message is: ',
    b'Confidential: ',
    b'Important: ',
    b'Please ',
    b'Thank you',
    b'Regards',
    b'{"type":',
    b'{"message":',
    b'{"data":',
    b'Subject: ',
    b'Date: ',
    b'Content: ',
]

def score_english(data):
    """Score how English-like the data is"""
    if not all(b < 128 for b in data):
        return -1000
    
    printable = sum(32 <= b <= 126 or b in [9, 10, 13] for b in data)
    if printable < len(data) * 0.9:
        return -1000
    
    score = printable * 2
    
    # Bonus for common English characters
    common = b' etaoinshrdlucmfwypvbgkjqxzETAOINSHRDLUCMFWYPVBGKJQXZ'
    score += sum(b in common for b in data) * 3
    
    # Bonus for spaces (very common)
    score += data.count(32) * 5
    
    # Penalty for rare control characters
    score -= sum(b < 32 and b not in [9, 10, 13] for b in data) * 20
    
    return score

best_p1 = None
best_score = -float('inf')

for pattern in patterns:
    for offset in range(min(20, 65 - len(pattern))):
        # Assume p2[offset:offset+len(pattern)] = pattern
        # Then p1[offset:offset+len(pattern)] = xor_result[offset:...] XOR pattern
        
        p1_partial = bytes(xor_result[offset + i] ^ pattern[i] for i in range(len(pattern)))
        
        # Check if this segment looks reasonable
        if not all(32 <= b <= 126 for b in p1_partial):
            continue
        
        # Now try to complete both messages assuming they're both English
        # Use the constraint that p1 XOR p2 = xor_result
        
        # Simple heuristic: assume rest is mostly lowercase letters and spaces
        p2_full = bytearray([32] * 64)  # Start with all spaces
        p2_full[offset:offset+len(pattern)] = pattern
        
        # For each position, pick the p2 value that makes p1 most English-like
        for pos in range(64):
            if offset <= pos < offset + len(pattern):
                continue
            
            best_char = 32
            best_char_score = -1
            
            for c in [32, 101, 116, 97, 111, 105, 110, 115, 104, 114, 100, 108] + list(range(97, 123)) + list(range(65, 91)):
                p1_char = xor_result[pos] ^ c
                if 32 <= p1_char <= 126:
                    char_score = 1
                    if p1_char in b' etaoinshrdlu':
                        char_score += 2
                    if char_score > best_char_score:
                        best_char_score = char_score
                        best_char = c
            
            p2_full[pos] = best_char
        
        p1_full = bytes(xor_result[i] ^ p2_full[i] for i in range(64))
        
        score = score_english(p1_full)
        if score > best_score:
            best_score = score
            best_p1 = p1_full

if best_p1 is None:
    # Ultimate fallback: brute force approach assuming high entropy p2
    # and trying to maximize English-ness of p1
    p2_guess = bytearray([32] * 64)
    
    for iteration in range(3):
        for pos in range(64):
            best_char = p2_guess[pos]
            best_local_score = -1
            
            for c in range(32, 127):
                p2_guess[pos] = c
                p1_test = bytes(xor_result[i] ^ p2_guess[i] for i in range(64))
                local_score = score_english(p1_test)
                
                if local_score > best_local_score:
                    best_local_score = local_score
                    best_char = c
            
            p2_guess[pos] = best_char
    
    best_p1 = bytes(xor_result[i] ^ p2_guess[i] for i in range(64))

# Output the claim
plaintext_hex = best_p1.hex()
claim = {"plaintext_hex": plaintext_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()