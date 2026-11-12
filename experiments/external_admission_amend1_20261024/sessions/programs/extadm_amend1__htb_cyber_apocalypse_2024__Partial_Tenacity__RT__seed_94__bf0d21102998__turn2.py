import base64
import math

# Decode the files
with open('output.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    n = int(lines[0].split(' = ')[1])
    ct_hex = lines[1].split(' = ')[1]
    ct = int(ct_hex, 16)
    p_leaked = lines[2].split(' = ')[1]
    q_leaked = lines[3].split(' = ')[1]

# Recover p from every other digit (starting at index 0)
p_str = p_leaked
p = int(p_str)

# Recover q from every other digit (starting at index 1 of original)
q_str = q_leaked
q = int(q_str)

# Verify n = p * q
if p * q != n:
    # Need to reconstruct properly
    # p_leaked has chars at positions 0, 2, 4, ... of str(p)
    # q_leaked has chars at positions 1, 3, 5, ... of str(q)
    # We need to interleave them back
    
    # Since we don't know the original length, try to reconstruct
    # The digits are interleaved: p[0], q[0], p[1], q[1], p[2], q[2], ...
    
    max_len = max(len(p_leaked), len(q_leaked))
    full_str = ''
    for i in range(max_len):
        if i < len(p_leaked):
            full_str += p_leaked[i]
        if i < len(q_leaked):
            full_str += q_leaked[i]
    
    # Now extract p and q
    p_digits = ''
    q_digits = ''
    for i in range(len(full_str)):
        if i % 2 == 0:
            p_digits += full_str[i]
        else:
            q_digits += full_str[i]
    
    p = int(p_digits)
    q = int(q_digits)

# Calculate RSA private key components
phi = (p - 1) * (q - 1)
e = 65537
d = pow(e, -1, phi)

# Decrypt the ciphertext
m = pow(ct, d, n)

# Convert to bytes
m_bytes = m.to_bytes((m.bit_length() + 7) // 8, 'big')

# RSA-OAEP decryption - we need to reverse OAEP padding
# Standard OAEP with SHA-1 has specific structure
# However, since we have the plaintext after modular exponentiation,
# we need to strip OAEP padding

# OAEP padding format: 0x00 || maskedSeed || maskedDB
# where maskedDB when unmasked gives: lHash || PS || 0x01 || M

# For a quick solution, let's try to find the flag pattern
for i in range(len(m_bytes)):
    if m_bytes[i:i+4] == b'HTB{':
        # Find the end
        end = m_bytes.find(b'}', i)
        if end != -1:
            flag = m_bytes[i:end+1].decode('ascii')
            print(flag)
            break
else:
    # Try to manually strip OAEP
    # The format after decryption should be:
    # 0x00 || seed (hLen bytes) || DB (k - hLen - 1 bytes)
    # For SHA-1, hLen = 20
    
    hLen = 20
    k = (n.bit_length() + 7) // 8
    
    if len(m_bytes) >= k:
        m_bytes = m_bytes[-k:]  # Take last k bytes
    
    # Simple approach: find HTB{ in the decrypted message
    m_str = m_bytes.hex()
    htb_hex = '4854427b'  # HTB{
    if htb_hex in m_str:
        idx = m_str.index(htb_hex) // 2
        remaining = m_bytes[idx:]
        end_idx = remaining.find(b'}')
        if end_idx != -1:
            flag = remaining[:end_idx+1].decode('ascii')
            print(flag)
