from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import math

# Read the output file
with open('output.txt', 'r') as f:
    lines = f.readlines()
    n = int(lines[0].split(' = ')[1])
    ct = bytes.fromhex(lines[1].split(' = ')[1])
    p_leak = lines[2].split(' = ')[1].strip()
    q_leak = lines[3].split(' = ')[1].strip()

# Reconstruct p from leaked digits (every other digit starting at index 0)
p_str = p_leak
p_len = len(p_str) * 2 - 1  # Approximate length

# Reconstruct q from leaked digits (every other digit starting at index 1)
q_str = q_leak
q_len = len(q_str) * 2  # Approximate length

# Brute force the missing digits
for p_digits in range(10 ** len(p_leak)):
    p_full = list('0' * (len(p_leak) * 2))
    temp = str(p_digits).zfill(len(p_leak))
    
    # Place known digits at even indices
    for i, digit in enumerate(p_leak):
        p_full[i * 2] = digit
    
    # Place guessed digits at odd indices
    for i, digit in enumerate(temp):
        if i * 2 + 1 < len(p_full):
            p_full[i * 2 + 1] = digit
    
    p_candidate = int(''.join(p_full))
    
    if n % p_candidate == 0:
        p = p_candidate
        q = n // p
        
        # Verify this is correct
        if p * q == n:
            # Reconstruct the private key
            phi = (p - 1) * (q - 1)
            e = 65537
            d = pow(e, -1, phi)
            
            # Create RSA key
            key = RSA.construct((n, e, d, p, q))
            cipher = PKCS1_OAEP.new(key)
            
            # Decrypt
            flag = cipher.decrypt(ct)
            print(flag.decode())
            break
