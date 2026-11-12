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

# Recover full p and q from leaked characters
# p_leaked has every other character starting from index 0: str(p)[::2]
# q_leaked has every other character starting from index 1: str(q)[1::2]

# We need to reconstruct p and q
# For p: we have characters at positions 0, 2, 4, 6, ...
# For q: we have characters at positions 1, 3, 5, 7, ...

# Strategy: brute force the missing digits
# Since p and q are each about 512 bits (154-155 decimal digits),
# and we have roughly half the digits, we need to fill in the gaps

def reconstruct_p(leaked, n):
    # leaked contains digits at even positions
    # We need to find digits at odd positions
    len_leaked = len(leaked)
    # The actual number has either 2*len_leaked or 2*len_leaked-1 digits
    
    for total_len in [2*len_leaked, 2*len_leaked - 1]:
        # Try to build p by inserting unknown digits
        def try_combinations(pos, current):
            if pos >= total_len:
                p_candidate = int(current)
                if n % p_candidate == 0:
                    return p_candidate
                return None
            
            if pos % 2 == 0:
                # We know this digit
                idx = pos // 2
                if idx < len(leaked):
                    return try_combinations(pos + 1, current + leaked[idx])
                else:
                    return None
            else:
                # We need to guess this digit
                idx_known = pos // 2
                for digit in '0123456789':
                    result = try_combinations(pos + 1, current + digit)
                    if result:
                        return result
                return None
        
        result = try_combinations(0, '')
        if result:
            return result
    return None

# More efficient approach: use the constraint that p * q = n
p_candidate = reconstruct_p(p_leaked, n)

if p_candidate and n % p_candidate == 0:
    p = p_candidate
    q = n // p
    
    # Compute private key components
    e = 65537
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    
    # Reconstruct the private key
    key = RSA.construct((n, e, d, p, q))
    cipher = PKCS1_OAEP.new(key)
    
    # Decrypt the flag
    flag = cipher.decrypt(ct)
    print(flag.decode())
else:
    # Alternative brute force for smaller search space
    # Build all possible p values and check divisibility
    def build_candidates(leaked_chars, total_length):
        if total_length == 2 * len(leaked_chars) - 1:
            # Last position is known
            positions = [(i, leaked_chars[i//2] if i % 2 == 0 and i//2 < len(leaked_chars) else None) for i in range(total_length)]
        else:  # total_length == 2 * len(leaked_chars)
            positions = [(i, leaked_chars[i//2] if i % 2 == 0 else None) for i in range(total_length)]
        
        def generate(idx, current):
            if idx == len(positions):
                yield current
                return
            
            pos, known = positions[idx]
            if known is not None:
                yield from generate(idx + 1, current + known)
            else:
                for d in '0123456789':
                    yield from generate(idx + 1, current + d)
        
        return generate(0, '')
    
    for length in [2 * len(p_leaked), 2 * len(p_leaked) - 1]:
        for p_str in build_candidates(p_leaked, length):
            p = int(p_str)
            if n % p == 0:
                q = n // p
                e = 65537
                phi = (p - 1) * (q - 1)
                d = pow(e, -1, phi)
                key = RSA.construct((n, e, d, p, q))
                cipher = PKCS1_OAEP.new(key)
                flag = cipher.decrypt(ct)
                print(flag.decode())
                break
        else:
            continue
        break