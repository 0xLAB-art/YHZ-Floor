import base64

def to_num(s):
    x = 0
    for i in range(len(s)):
        x += ord(s[-1-i]) * pow(256, i)
    return x

def get_nums(s, n):
    sections = [s[i:i+n] for i in range(0, len(s), n)]
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

def enc_vals(m_chr, k_chr, n):
    return (m_chr + k_chr) & ((1 << n) - 1)

def encrypt(k, m, n):
    if (n >= 8): raise ValueError("n is too high!")
    rep_k = k * (len(m) // len(k)) + k[:len(m) % len(k)]
    m_val_list = [get_vals(x, n) for x in get_nums(m, n)]
    k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
    m_vals, k_vals, c_vals = [], [], []
    for lst in m_val_list: m_vals += lst
    for lst in k_val_list: k_vals += lst
    c_vals = [enc_vals(m_vals[i], k_vals[i % len(k_vals)], n)
              for i in range(0, len(m_vals))]
    c_val_list = [c_vals[i:i+8] for i in range(0, len(c_vals), 8)]
    return "".join([get_chrs(lst, n) for lst in c_val_list])

# Read ciphertext
with open("ciphertext", "rb") as f:
    ct_raw = f.read()
ciphertext = ct_raw.decode("latin-1")

# The flag is a printable ASCII string. Try all n in 1..7 and all possible keys.
# The ciphertext is base64 encoded (with newlines stripped).
ct_b64 = "".join(ciphertext.split())
ct_bytes = base64.b64decode(ct_b64)

# Brute force: n in 1..7, key length 1..len(ct_bytes), key bytes printable-ish
# But we can be smarter: the flag likely starts with "flag{"

import string

for n in range(1, 8):
    # c_vals are 8-byte chunks, each byte is (m + k) mod 2^n
    # For each position i in the plaintext, c[i] = (m[i] + k[i mod keylen]) mod 2^n
    # We need to find key such that decrypting gives printable ASCII.
    # Key length: try 1..16
    for keylen in range(1, 17):
        # For each key position j, we have c[j], c[j+keylen], c[j+2*keylen], ...
        # m[j + t*keylen] = (c[j + t*keylen] - k[j]) mod 2^n
        # Try all possible k[j] in 0..2^n-1 and check if resulting chars are printable
        possible_keys = [None] * keylen
        for j in range(keylen):
            candidates = []
            for k_j in range(2**n):
                ok = True
                for t in range(0, 8, 1):
                    idx = j + t * keylen
                    if idx >= len(ct_bytes):
                        break
                    ch = chr((ct_bytes[idx] - k_j) % 256)
                    # must be printable ASCII
                    if not (32 <= ch <= 126):
                        ok = False
                        break
                if ok:
                    candidates.append(k_j)
            if not candidates:
                break
            possible_keys[j] = candidates
        else:
            # Now try to combine candidates to find a key that produces a valid flag
            # Use backtracking
            key = [0] * keylen
            def backtrack(j):
                if j == keylen:
                    # verify full decryption
                    m_bytes = bytearray(len(ct_bytes))
                    for i in range(len(ct_bytes)):
                        m_bytes[i] = (ct_bytes[i] - key[i % keylen]) % 256
                    try:
                        m = m_bytes.decode("ascii")
                        if m.startswith("flag"):
                            return m_bytes
                    except:
                        pass
                    return None
                for k_j in possible_keys[j]:
                    key[j] = k_j
                    res = backtrack(j + 1)
                    if res is not None:
                        return res
                return None
            res = backtrack(0)
            if res is not None:
                print(res.decode("ascii"))
                raise SystemExit
