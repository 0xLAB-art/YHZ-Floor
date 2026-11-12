import json

with open('ciphertext') as f:
    ct = ''.join(f.read().split())

# The cipher: each byte of plaintext is split into n-bit chunks,
# key is repeated, and each chunk is XORed with the corresponding key chunk.
# Since XOR is its own inverse and the chunking is consistent, we can recover
# the key by XORing ciphertext chunks with known plaintext structure.
# Try all single-byte keys and n values.

for n in range(1, 8):
    for k in range(256):
        # decrypt: same as encrypt with XOR
        m = ''
        rep_k = chr(k) * (len(ct) // 1) + chr(k)[:len(ct) % 1]
        c_vals = [ord(c) for c in ct]
        k_vals = [k] * len(c_vals)
        m_vals = [c_vals[i] ^ k_vals[i] for i in range(len(c_vals))]
        # reconstruct bytes from n-bit chunks
        # each byte = n bits, so group by n
        byte_vals = []
        for i in range(0, len(m_vals), n):
            b = 0
            for j in range(n):
                b = (b << n) | m_vals[i+j]
            byte_vals.append(b)
        try:
            m = ''.join(chr(b) for b in byte_vals)
            if m.startswith('flag') or 'flag' in m:
                print(m)
                break
        except:
            pass
    else:
        continue
    break
