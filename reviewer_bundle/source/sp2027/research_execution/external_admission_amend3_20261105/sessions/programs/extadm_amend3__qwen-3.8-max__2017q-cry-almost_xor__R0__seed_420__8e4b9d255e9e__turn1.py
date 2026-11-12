import sys

def to_num(s):
    x = 0
    for i in range(len(s)):
        x += ord(s[-1 - i]) * pow(256, i)
    return x

def get_nums(s, n):
    sections = [s[i:i + n] for i in range(0, len(s), n)]
    sections[-1] = sections[-1] + ("\x00" * (n - len(sections[-1])))
    return [to_num(x) for x in sections]

def get_vals(x, n):
    vals = []
    mask = (1 << n) - 1
    for i in range(8):
        vals.append(x & mask)
        x = x >> n
    vals.reverse()
    return vals

def get_chrs(val_list, n):
    x = val_list[0]
    chrs = []
    for i in range(1, len(val_list)):
        x <<= n
        x += val_list[i]
    for i in range(n):
        chrs.append(chr(x % 256))
        x //= 256
    chrs.reverse()
    return "".join(chrs)

def encr_vals(m_chr, k_chr, n):
    return (m_chr + k_chr) & ((1 << n) - 1)

def encrypt(k, m, n):
    if n >= 8:
        raise ValueError("n is too high!")
    rep_k = k * (len(m) // len(k)) + k[: len(m) % len(k)]
    m_val_list = [get_vals(x, n) for x in get_nums(m, n)]
    k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
    m_vals, k_vals, c_vals = [], [], []
    for lst in m_val_list:
        m_vals += lst
    for lst in k_val_list:
        k_vals += lst
    c_vals = [encr_vals(m_vals[i], k_vals[i % len(k_vals)], n)
              for i in range(0, len(m_vals))]
    c_val_list = [c_vals[i:i + 8] for i in range(0, len(c_vals), 8)]
    return "".join([get_chrs(lst, n) for lst in c_val_list])


with open("ciphertext") as f:
    ct = f.read().replace("\n", "").replace(" ", "")
ct_bytes = bytes.fromhex(ct)

for n in range(1, 8):
    for key_len in range(1, 17):
        # brute force key of length key_len over printable-ish bytes
        # use known-plaintext-like approach: try all keys
        import itertools
        # too slow for full brute; instead exploit structure
        pass

# Analyze: ciphertext is 64 bytes = 512 bits
# Each byte of ciphertext encodes 8 values of n bits -> 8*n bits per ciphertext byte
# 512 bits total / 8 = 64 bytes ciphertext
# For n bits per value, each ciphertext byte holds 8 values of n bits = 8n bits
# 64 bytes * 8n = 512n bits of ciphertext
# Plaintext: 64 bytes = 512 bytes = 4096 bits
# Hmm, let's compute: c_val_list chunks of 8 values, each value n bits
# get_chrs takes 8 values of n bits -> reconstructs n bytes
# So each ciphertext byte -> n bytes of plaintext
# 64 ciphertext bytes -> 64*n plaintext bytes

# Key: rep_k = k * (len(m)//len(k)) + k[:len(m)%len(k)]
# m_val_list: each plaintext byte split into 8 values of n bits
# k_val_list: each key byte split into 8 values of n bits, repeated
# c_vals[i] = (m_vals[i] + k_vals[i % len(k_vals)]) & mask
# len(m_vals) = 64 * 8 = 512
# len(k_vals) = len(k) * 8
# So c_vals[i] = m_vals[i] + k_vals[i % (8*len(k))]

# m_vals[i] is the j-th n-bit value of plaintext byte p where i = 8*p + j
# k_vals[i % 8*len(k)] = k-byte value

# For a given n, plaintext byte p contributes 8 values (j=0..7), each n bits
# These 8 values are concatenated to form n bytes of ciphertext

# Key stream: k_vals repeats every 8*len(k) positions
# m_vals[i] = c_vals[i] - k_vals[i % 8*len(k)]  (mod 2^n, but subtraction with wrap)

# Since m_vals[i] is an n-bit value of plaintext byte p = i // 8
# and the 8 values of byte p form the ciphertext for that byte

# Approach: for each n, try key lengths. The key bytes are unknown.
# But we can use the fact that plaintext is likely ASCII/flag-like.

# Actually, let's think about the structure more carefully.
# For n=1: each byte split into 8 values of 1 bit. 8 values -> 1 byte ciphertext.
#   So 64 ciphertext bytes -> 64 plaintext bytes. Key stream: 8*len(k) 1-bit values.
# For n=8: not allowed (n >= 8 raises).

# Let's try n from 1 to 7 and key lengths, using a meet-in or known structure.
# The flag format is likely "flag{...}".

# For each n and key_len, we can try to recover key by assuming plaintext starts with "flag{"
# m_vals[0..7] = values of 'f' = 102
# c_vals[0..7] known from ciphertext
# k_vals[0..7] = c_vals[i] - m_vals[i] mod 2^n
# Then key byte 0 = get_chrs(k_vals[0..7], n)
# Then verify full decryption.

import itertools

def decrypt(n, key):
    rep_k = key * (64 // len(key)) + key[:64 % len(key)]
    k_val_list = [get_vals(ord(c), n) for c in rep_k]
    k_vals = []
    for lst in k_val_list:
        k_vals += lst
    mask = (1 << n) - 1
    c_val_list = [bytes.fromhex(ct)[i:i + 8] for i in range(0, len(ct), 8)]
    c_vals = []
    for lst in c_val_list:
        x = 0
        for v in lst:
            x = (x << n) + v
        for j in range(8):
            c_vals.append((x >> (n * (7 - j))) & mask)
    m_vals = []
    for i in range(len(c_vals)):
        m_vals.append((c_vals[i] - k_vals[i % len(k_vals)]) & mask)
    # reconstruct plaintext bytes
    m_bytes = []
    for p in range(64):
        x = 0
        for j in range(8):
            x = (x << n) + m_vals[p * 8 + j]
        m_bytes.append(x)
    return bytes(m_bytes)

ct_hex = ct
ct_bytes = bytes.fromhex(ct_hex)

def cvals_from_ct(n):
    c_vals = []
    for i in range(0, len(ct_bytes), 8):
        lst = ct_bytes[i:i + 8]
        x = 0
        for v in lst:
            x = (x << n) + v
        mask = (1 << n) - 1
        for j in range(8):
            c_vals.append((x >> (n * (7 - j))) & mask)
    return c_vals

cvals = cvals_from_ct(1)  # placeholder

best = None
for n in range(1, 8):
    mask = (1 << n) - 1
    cvals_n = cvals_from_ct(n)
    # plaintext byte 0 = 'f' = 102, byte 1 = 'l', byte 2 = 'a', byte 3 = 'g', byte 4 = '{'
    known = [ord(c) for c in "flag{"]
    for key_len in range(1, 9):
        # k_vals[i] = c_vals[i] - m_vals[i] mod 2^n
        # m_vals for first 4 bytes known: each byte -> 8 values
        # key byte 0 = values k_vals[0..7], key byte 1 = k_vals[8..15], etc.
        # k_vals index i corresponds to key byte (i // 8) % key_len
        key_vals = {}  # (key_byte_idx) -> list of 8 values
        possible = True
        for i in range(32):  # first 4 bytes * 8
            kb = (i // 8) % key_len
            m_val = (known[i // 8] >> (n * (7 - (i % 8)))) & mask
            k_val = (cvals_n[i] - m_val) & mask
            if kb not in key_vals:
                key_vals[kb] = []
            key_vals[kb].append(k_val)
        # check consistency: each key byte must have exactly 8 values
        if len(key_vals) != key_len or any(len(v) != 8 for v in key_vals.values()):
            continue
        # build candidate key
        key = ""
        for kb in range(key_len):
            vals = key_vals[kb]
            x = 0
            for v in vals:
                x = (x << n) + v
            key += chr(x)
        # verify
        try:
            plain = decrypt(n, key)
            if plain.startswith(b"flag{"):
                print(plain.decode())
                break
        except Exception:
            pass
    else:
        continue
    break
