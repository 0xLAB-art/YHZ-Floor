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
# c1 = p1 XOR keystream
# c2 = p2 XOR keystream
# Therefore: c1 XOR c2 = p1 XOR p2

# XOR the two ciphertexts
xor_result = bytes(a ^ b for a, b in zip(c1, c2))

# Common known plaintext patterns to try
# Assuming p2 might contain common English text or structured data
# We'll try common prefixes and use frequency analysis

# Strategy: assume p2 contains readable ASCII/English text
# Common starting patterns in messages, JSON, etc.
common_starts = [
    b'{"',
    b'The ',
    b'Hello',
    b'Message:',
    b'From: ',
    b'To: ',
    b'Subject:',
    b'Dear ',
    b'Hi ',
    b'<?xml',
    b'<!DOCTYPE',
    b'HTTP/',
    b'GET ',
    b'POST ',
    b'User: ',
    b'Pass: ',
    b'username',
    b'password',
    b'secret',
    b'flag{',
    b'FLAG{',
    b'Key: ',
    b'Token: ',
    b'Session:',
    b'Auth: ',
    b'Bearer ',
]

# Try to find which prefix works by checking if resulting p1 is reasonable
best_p1 = None
best_score = -1

for prefix in common_starts:
    if len(prefix) > len(xor_result):
        continue
    
    # Assume p2 starts with this prefix
    # p1_prefix = (p1 XOR p2) XOR p2_prefix = xor_result XOR p2_prefix
    p1_candidate_prefix = bytes(xor_result[i] ^ prefix[i] for i in range(len(prefix)))
    
    # Check if this looks like reasonable text (printable ASCII)
    score = sum(32 <= b <= 126 for b in p1_candidate_prefix)
    
    if score > best_score:
        best_score = score
        # Extend: assume rest of p2 is also readable ASCII
        # Try common ASCII range for p2 and see if p1 becomes readable
        
# Alternative approach: assume BOTH messages are English text
# Use frequency analysis and crib dragging

# Let's try a statistical approach:
# For each position, try all possible byte values for p2
# and see which makes p1 look most like English text

p1_recovered = bytearray(64)
p2_recovered = bytearray(64)

# Common English letter frequencies
common_chars = b' etaoinshrdlucmfwypvbgkjqxz0123456789.,!?\'"\n\r-:;()[]{}'

for pos in range(64):
    best_char = 0
    best_fitness = -1
    
    for p2_guess in range(256):
        p1_guess = xor_result[pos] ^ p2_guess
        
        # Fitness: both should be printable, bonus for common chars
        fitness = 0
        if 32 <= p1_guess <= 126:
            fitness += 10
        if 32 <= p2_guess <= 126:
            fitness += 10
        if p1_guess in common_chars:
            fitness += 5
        if p2_guess in common_chars:
            fitness += 5
        if p1_guess == 32:  # space
            fitness += 3
        if p2_guess == 32:
            fitness += 3
            
        if fitness > best_fitness:
            best_fitness = fitness
            best_char = p1_guess
    
    p1_recovered[pos] = best_char

# Output the claim
plaintext_hex = p1_recovered.hex()
claim = {"plaintext_hex": plaintext_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()