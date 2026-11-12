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

# RC4 keystream reuse attack
# c1 = p1 XOR keystream
# c2 = p2 XOR keystream
# Therefore: c1 XOR c2 = p1 XOR p2

xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# The error "candidate_plaintext == reserved_plaintext" keeps appearing
# This means I'm likely recovering p2 (the reserved one) instead of p1

# Critical insight: I need to determine which ciphertext corresponds to which plaintext
# Let me try a completely different approach:
# Instead of assuming p2 has a pattern, assume p1 has a pattern
# and derive p2 from it

# Try common starting patterns for p1 directly
common_p1_patterns = [
    b'The secret message is: ',
    b'Plaintext 1: ',
    b'Message 1: ',
    b'P1: ',
    b'First: ',
    b'Primary: ',
    b'Target: ',
    b'Original: ',
    b'Content: ',
    b'Data: ',
    b'This is plaintext one ',
    b'This is message one ',
    b'Encrypted message: ',
]

def is_printable_english(data):
    """Check if data looks like printable English text"""
    if not data:
        return False
    printable_count = sum(32 <= b <= 126 for b in data)
    return printable_count >= len(data) * 0.95

best_p1 = None

for pattern in common_p1_patterns:
    # Assume p1 starts with pattern
    p1_start = pattern
    # Then p2_start = p1_start XOR xor_result[:len(pattern)]
    p2_start = bytes(p1_start[i] ^ xor_result[i] for i in range(len(pattern)))
    
    # Check if p2_start is also printable
    if is_printable_english(p2_start):
        # Good candidate, extend it
        # Build full p1 by assuming both are English
        p1_full = bytearray(pattern)
        
        # For remaining bytes, use heuristic
        for pos in range(len(pattern), 64):
            # Try common characters for p1
            found = False
            for c1 in b' etaoinshrdlucmfwypvbgkjqxz.,!?\'"':
                c2 = xor_result[pos] ^ c1
                if 32 <= c2 <= 126:
                    p1_full.append(c1)
                    found = True
                    break
            if not found:
                p1_full.append(xor_result[pos] ^ 32)
        
        best_p1 = bytes(p1_full)
        break

if best_p1 is None:
    # Different strategy: assume NEITHER has a specific pattern
    # Just maximize mutual English-likeness
    # Use iterative refinement
    
    p1_candidate = bytearray(64)
    p2_candidate = bytearray(64)
    
    # Initialize with space assumption
    for i in range(64):
        p2_candidate[i] = 32
        p1_candidate[i] = xor_result[i] ^ 32
    
    # Iteratively improve
    for iteration in range(5):
        # Refine p2 to make p1 more English
        for pos in range(64):
            best_c2 = p2_candidate[pos]
            best_score = -1
            
            for c2 in range(32, 127):
                c1 = xor_result[pos] ^ c2
                score = 0
                
                if 32 <= c1 <= 126 and 32 <= c2 <= 126:
                    score += 10
                    if c1 in b' etaoinshrdlu':
                        score += 5
                    if c2 in b' etaoinshrdlu':
                        score += 2
                    if c1 == 32:
                        score += 3
                
                if score > best_score:
                    best_score = score
                    best_c2 = c2
            
            p2_candidate[pos] = best_c2
            p1_candidate[pos] = xor_result[pos] ^ best_c2
    
    best_p1 = bytes(p1_candidate)

# Output the claim
plaintext_hex = best_p1.hex()
claim = {"plaintext_hex": plaintext_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()