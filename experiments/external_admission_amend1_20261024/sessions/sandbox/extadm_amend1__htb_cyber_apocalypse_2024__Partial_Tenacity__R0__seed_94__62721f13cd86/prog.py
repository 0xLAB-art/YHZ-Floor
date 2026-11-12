from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import math

# Read output.txt
with open('output.txt', 'r') as f:
    lines = f.readlines()
    n = int(lines[0].split(' = ')[1])
    ct = bytes.fromhex(lines[1].split(' = ')[1])
    p_partial = lines[2].split(' = ')[1].strip()
    q_partial = lines[3].split(' = ')[1].strip()

# p_partial contains every other character starting from index 0
# q_partial contains every other character starting from index 1
# We need to reconstruct p and q

# Let's denote p_str and q_str as the full string representations
# p_partial = p_str[::2] means characters at positions 0, 2, 4, ...
# q_partial = q_str[1::2] means characters at positions 1, 3, 5, ...

# The length of p and q are roughly equal (both ~154 digits for 1024-bit RSA)
# We know n = p * q, so we can use this to recover the full values

# Strategy: try to reconstruct by interleaving and testing divisibility
# Since we have partial info about both, we can try to brute force missing digits

def reconstruct_prime(partial_chars, positions, other_partial, other_positions, n):
    """Try to reconstruct a prime given partial characters at certain positions"""
    # Estimate length based on n
    num_digits = len(str(n)) // 2 + 1
    
    # Build a template with known positions
    digits = ['0'] * num_digits
    for i, char in enumerate(partial_chars):
        if positions == 'even':
            pos = i * 2
        else:
            pos = i * 2 + 1
        if pos < num_digits:
            digits[pos] = char
    
    return digits

# Try to reconstruct p and q by testing combinations
# We know p_partial and q_partial, we need to find the interleaved digits

# Length estimation
p_len = len(p_partial) * 2  # approximately
q_len = len(q_partial) * 2  # approximately

# Try different lengths around the estimate
for p_total_len in range(len(p_partial) * 2 - 2, len(p_partial) * 2 + 2):
    for q_total_len in range(len(q_partial) * 2 - 2, len(q_partial) * 2 + 2):
        # Try to reconstruct by brute forcing missing digits
        # This is computationally intensive, so let's use a smarter approach
        
        # Build templates
        p_digits = ['?'] * p_total_len
        q_digits = ['?'] * q_total_len
        
        # Fill in known p digits (every other, starting at 0)
        for i, char in enumerate(p_partial):
            pos = i * 2
            if pos < p_total_len:
                p_digits[pos] = char
        
        # Fill in known q digits (every other, starting at 1)
        for i, char in enumerate(q_partial):
            pos = i * 2 + 1
            if pos < q_total_len:
                q_digits[pos] = char
        
        # Now brute force the missing digits
        def try_reconstruct(p_digits, q_digits, n):
            # Count unknowns
            p_unknowns = [i for i, d in enumerate(p_digits) if d == '?']
            q_unknowns = [i for i, d in enumerate(q_digits) if d == '?']
            
            # Limit search space
            if len(p_unknowns) > 10 or len(q_unknowns) > 10:
                return None
            
            # Try all combinations for p
            for p_combo in range(10 ** len(p_unknowns)):
                p_test = p_digits.copy()
                combo_str = str(p_combo).zfill(len(p_unknowns))
                for i, idx in enumerate(p_unknowns):
                    p_test[idx] = combo_str[i]
                p_val = int(''.join(p_test))
                
                if n % p_val == 0:
                    q_val = n // p_val
                    q_str = str(q_val)
                    
                    # Check if q matches the partial
                    if len(q_str) == len(q_digits):
                        match = True
                        for i, d in enumerate(q_digits):
                            if d != '?' and q_str[i] != d:
                                match = False
                                break
                        if match:
                            return p_val, q_val
            return None
        
        result = try_reconstruct(p_digits, q_digits, n)
        if result:
            p, q = result
            
            # Compute private key
            e = 65537
            phi = (p - 1) * (q - 1)
            d = pow(e, -1, phi)
            
            # Decrypt
            key = RSA.construct((n, e, d, p, q))
            cipher = PKCS1_OAEP.new(key)
            flag = cipher.decrypt(ct)
            print(flag.decode())
            exit()

print("Failed to recover key")