from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import math

# Read the output file
with open('output.txt', 'r') as f:
    lines = f.readlines()
    n = int(lines[0].split(' = ')[1])
    ct = bytes.fromhex(lines[1].split(' = ')[1])
    p_partial = lines[2].split(' = ')[1].strip()
    q_partial = lines[3].split(' = ')[1].strip()

# Reconstruct p from partial information
# p_partial has every other digit starting from index 0 (even indices)
p_digits = list(p_partial)
p_len = len(p_partial) * 2 - 1  # approximate length

# Reconstruct q from partial information  
# q_partial has every other digit starting from index 1 (odd indices)
q_digits = list(q_partial)
q_len = len(q_partial) * 2  # approximate length

# Try to recover p and q
# We know p * q = n and we have partial digits
# Strategy: try all possible combinations for missing digits

def reconstruct_number(partial_digits, positions, target_len):
    """Generate candidates by filling in missing positions"""
    # positions: 'even' means we have indices 0,2,4,... or 'odd' means 1,3,5,...
    if positions == 'even':
        # We have digits at even positions
        for candidate in range(10 ** (target_len - len(partial_digits))):
            candidate_str = str(candidate).zfill(target_len - len(partial_digits))
            full = []
            for i in range(target_len):
                if i % 2 == 0:
                    full.append(partial_digits[i // 2])
                else:
                    full.append(candidate_str[i // 2])
            yield int(''.join(full))
    else:
        # We have digits at odd positions
        for candidate in range(10 ** (target_len - len(partial_digits))):
            candidate_str = str(candidate).zfill(target_len - len(partial_digits))
            full = []
            for i in range(target_len):
                if i % 2 == 1:
                    full.append(partial_digits[i // 2])
                else:
                    full.append(candidate_str[i // 2])
            yield int(''.join(full))

# More efficient approach: use the constraint that p * q = n
# We know partial digits, so we can search more intelligently

# First, determine the likely length of p and q
n_len = len(str(n))
p_likely_len = len(p_partial) * 2 - 1
q_likely_len = len(q_partial) * 2

# Adjust if needed
if p_likely_len + q_likely_len != n_len:
    p_likely_len = len(p_partial) * 2

# Try to reconstruct by iterating through possible missing digits
for p_len_try in [len(p_partial) * 2 - 1, len(p_partial) * 2]:
    for extra_p in range(10 ** (p_len_try - len(p_partial))):
        extra_p_str = str(extra_p).zfill(p_len_try - len(p_partial))
        p_full = []
        for i in range(p_len_try):
            if i % 2 == 0:
                p_full.append(p_partial[i // 2])
            else:
                p_full.append(extra_p_str[i // 2])
        p_candidate = int(''.join(p_full))
        
        if n % p_candidate == 0:
            q_candidate = n // p_candidate
            # Verify q matches the partial
            q_str = str(q_candidate)
            q_partial_check = q_str[1::2]
            if q_partial_check == q_partial:
                p = p_candidate
                q = q_candidate
                
                # Calculate private key components
                e = 65537
                phi = (p - 1) * (q - 1)
                d = pow(e, -1, phi)
                
                # Create RSA key and decrypt
                key = RSA.construct((n, e, d, p, q))
                cipher = PKCS1_OAEP.new(key)
                flag = cipher.decrypt(ct)
                print(flag.decode())
                exit()
