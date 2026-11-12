import base64
import math

# Decode the artifacts
with open('output.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    n = int(lines[0].split(' = ')[1])
    ct_hex = lines[1].split(' = ')[1]
    ct = int(ct_hex, 16)
    p_leaked = lines[2].split(' = ')[1]
    q_leaked = lines[3].split(' = ')[1]

# Reconstruct p from leaked every other character (starting at index 0)
# p_leaked contains characters at positions 0, 2, 4, ... of str(p)
# Reconstruct q from leaked every other character (starting at index 1)
# q_leaked contains characters at positions 1, 3, 5, ... of str(q)

# Since we have half the digits, we need to find the full p and q
# such that p * q = n

# Let's work with the constraint that p_leaked gives us positions 0,2,4,...
# and q_leaked gives us positions 1,3,5,...

# Estimate bit length
p_len = len(p_leaked) * 2
q_len = len(q_leaked) * 2

# Try to reconstruct by brute force on missing digits
def reconstruct_from_partial(leaked_str, target_len, is_p, n):
    # For p: leaked has positions 0,2,4,6,...
    # For q: leaked has positions 1,3,5,7,...
    from itertools import product
    
    missing_positions = target_len - len(leaked_str)
    
    # Generate candidates
    for missing_digits in product('0123456789', repeat=missing_positions):
        if is_p:
            # Interleave: leaked[0], missing[0], leaked[1], missing[1], ...
            full = ''
            for i in range(len(leaked_str)):
                full += leaked_str[i]
                if i < len(missing_digits):
                    full += missing_digits[i]
            # Add any remaining missing digits if lengths don't match
            if len(missing_digits) > len(leaked_str):
                full += missing_digits[len(leaked_str)]
        else:
            # For q: missing[0], leaked[0], missing[1], leaked[1], ...
            full = ''
            for i in range(len(missing_digits)):
                full += missing_digits[i]
                if i < len(leaked_str):
                    full += leaked_str[i]
            # Add any remaining leaked digits
            if len(leaked_str) > len(missing_digits):
                full += leaked_str[len(missing_digits):]
        
        candidate = int(full)
        if n % candidate == 0:
            return candidate
    return None

# First, determine the exact lengths
p_guess_len = len(p_leaked) * 2
q_guess_len = len(q_leaked) * 2

# Adjust if odd/even
if len(p_leaked) * 2 - 1 == len(p_leaked) * 2:
    p_guess_len = len(p_leaked) * 2 - 1

# Try different length combinations around the estimate
for p_extra in [0, 1, -1]:
    for q_extra in [0, 1, -1]:
        p_try_len = len(p_leaked) * 2 + p_extra
        q_try_len = len(q_leaked) * 2 + q_extra
        
        if p_try_len < len(p_leaked) or q_try_len < len(q_leaked):
            continue
            
        p = reconstruct_from_partial(p_leaked, p_try_len, True, n)
        if p:
            q = n // p
            if p * q == n:
                # Found valid p and q
                # Now decrypt
                phi = (p - 1) * (q - 1)
                e = 65537
                d = pow(e, -1, phi)
                
                # RSA decryption
                m = pow(ct, d, n)
                
                # Convert to bytes and remove OAEP padding manually
                m_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')
                
                # OAEP padding format: 0x00 || 0x02 || PS || 0x00 || M
                # But we're using PKCS1_OAEP which is different
                # Let's try to find HTB{ in the decrypted message
                
                # Search for HTB{ pattern
                try:
                    flag_start = m_bytes.find(b'HTB{')
                    if flag_start >= 0:
                        flag_end = m_bytes.find(b'}', flag_start)
                        if flag_end >= 0:
                            flag = m_bytes[flag_start:flag_end+1].decode('ascii')
                            print(flag)
                            exit(0)
                except:
                    pass

print('Flag not found')
