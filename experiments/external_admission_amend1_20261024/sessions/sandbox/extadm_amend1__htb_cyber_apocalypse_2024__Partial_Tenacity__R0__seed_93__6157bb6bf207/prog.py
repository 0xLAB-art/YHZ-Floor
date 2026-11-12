from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import math

# Read the output file
with open('output.txt', 'r') as f:
    lines = f.readlines()
    n = int(lines[0].split(' = ')[1])
    ct = bytes.fromhex(lines[1].split(' = ')[1])
    p_leaked = lines[2].split(' = ')[1].strip()
    q_leaked = lines[3].split(' = ')[1].strip()

# Reconstruct p from leaked digits (every other digit starting at index 0)
p_str = p_leaked
p_len = len(p_str) * 2 - 1  # approximate original length

# Reconstruct q from leaked digits (every other digit starting at index 1)
q_str = q_leaked
q_len = len(q_str) * 2  # approximate original length

# We need to brute force the missing digits
# For p: we have digits at positions 0,2,4,6,... and need to find digits at 1,3,5,7,...
# For q: we have digits at positions 1,3,5,7,... and need to find digits at 0,2,4,6,...

def reconstruct_number(known_digits, positions, total_len, n, is_p):
    """Reconstruct a number by brute forcing missing digits"""
    # positions: list of positions where we know the digits
    # known_digits: the known digits as a string
    
    from itertools import product
    
    missing_positions = [i for i in range(total_len) if i not in positions]
    num_missing = len(missing_positions)
    
    # Try all combinations of missing digits
    for missing_vals in product('0123456789', repeat=num_missing):
        # Construct the full number
        digits = ['0'] * total_len
        for i, pos in enumerate(positions):
            if i < len(known_digits):
                digits[pos] = known_digits[i]
        for i, pos in enumerate(missing_positions):
            digits[pos] = missing_vals[i]
        
        candidate = int(''.join(digits))
        
        # Check if this is a valid factor of n
        if n % candidate == 0:
            other = n // candidate
            # Verify it's prime-like (basic check)
            if candidate > 1 and other > 1 and candidate * other == n:
                return candidate, other
    
    return None, None

# Calculate the approximate length of p and q
# n is 1024 bits, so p and q are approximately 512 bits each
# 512 bits is approximately 154 decimal digits

# Try different lengths around the expected value
for p_len in range(len(p_leaked) * 2 - 2, len(p_leaked) * 2 + 2):
    p_positions = list(range(0, p_len, 2))
    p, q = reconstruct_number(p_leaked, p_positions, p_len, n, True)
    if p is not None:
        break

if p is None:
    # Try reconstructing from q side
    for q_len in range(len(q_leaked) * 2 - 1, len(q_leaked) * 2 + 2):
        q_positions = list(range(1, q_len, 2))
        q, p = reconstruct_number(q_leaked, q_positions, q_len, n, False)
        if q is not None:
            break

# Compute private key components
e = 65537
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)

# Create RSA key and decrypt
key = RSA.construct((n, e, d, p, q))
cipher = PKCS1_OAEP.new(key)
flag = cipher.decrypt(ct)

print(flag.decode())