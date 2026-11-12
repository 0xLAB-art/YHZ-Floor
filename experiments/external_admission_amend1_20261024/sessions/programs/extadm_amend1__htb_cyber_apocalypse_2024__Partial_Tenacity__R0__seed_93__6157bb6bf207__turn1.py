from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import math

# Read the output file
with open('output.txt', 'r') as f:
    lines = f.readlines()
    n = int(lines[0].split(' = ')[1].strip())
    ct = bytes.fromhex(lines[1].split(' = ')[1].strip())
    p_leaked = lines[2].split(' = ')[1].strip()
    q_leaked = lines[3].split(' = ')[1].strip()

# Reconstruct p from leaked digits (every other digit starting at index 0)
p_str = p_leaked
p_len = len(p_str) * 2 - 1  # Approximate original length

# Reconstruct q from leaked digits (every other digit starting at index 1)
q_str = q_leaked
q_len = len(q_str) * 2  # Approximate original length

# We need to brute force the missing digits
# For p: we have digits at positions 0, 2, 4, 6, ...
# For q: we have digits at positions 1, 3, 5, 7, ...

def reconstruct_prime(leaked_digits, positions, target_len):
    """Reconstruct a prime number by trying all possible missing digits"""
    leaked_list = list(leaked_digits)
    
    # Try different lengths around the estimated length
    for length in range(target_len - 1, target_len + 2):
        missing_positions = [i for i in range(length) if i not in positions[:len(leaked_list)]]
        
        # Generate all combinations for missing digits
        from itertools import product
        for missing_vals in product('0123456789', repeat=len(missing_positions)):
            # Build the number
            result = ['0'] * length
            for i, digit in enumerate(leaked_list):
                if positions[i] < length:
                    result[positions[i]] = digit
            for i, pos in enumerate(missing_positions):
                result[pos] = missing_vals[i]
            
            num_str = ''.join(result)
            if num_str[0] == '0':  # Skip leading zeros
                continue
                
            num = int(num_str)
            
            # Check if n is divisible by this number
            if n % num == 0:
                return num
    return None

# For p, we have every other digit starting at position 0
p_positions = list(range(0, len(p_leaked) * 2, 2))
p = reconstruct_prime(p_leaked, p_positions, len(p_leaked) * 2)

if p:
    q = n // p
    
    # Verify we have correct p and q
    if p * q == n:
        # Calculate phi
        phi = (p - 1) * (q - 1)
        
        # Calculate d (private exponent)
        e = 65537  # Standard RSA public exponent
        d = pow(e, -1, phi)
        
        # Create RSA key
        key = RSA.construct((n, e, d, p, q))
        cipher = PKCS1_OAEP.new(key)
        
        # Decrypt
        flag = cipher.decrypt(ct)
        print(flag.decode())
