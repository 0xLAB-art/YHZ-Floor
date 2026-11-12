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
    ct = f.read().decode().strip()
ct = base64.b64decode(ct).decode()

# Read the script to get n
with open("almostxor.py", "r") as f:
    src = f.read()

# Brute force n from 1 to 7
for n in range(1, 8):
    # Try to reverse: c_vals[i] = (m_vals[i] + k_vals[i % len(k_vals)]) & mask
    # We need to find key k such that decrypting gives a flag-like message
    # Try all possible single-byte keys first, then extend
    mask = (1 << n) - 1
    # Reconstruct c_vals
    c_val_list = [list(map(int, [ord(c) for c in ""])) for _ in range(0, len(ct), 1)]
    # Actually get c_vals from ciphertext
    c_vals = []
    for i in range(0, len(ct), 8):
        chunk = ct[i:i+8]
        x = 0
        for c in chunk:
            x = (x << n) | ord(c)
        c_vals.append(x)
    
    # Try all keys of length 1..4
    from itertools import product
    for klen in range(1, 5):
        for key_bytes in product(range(256), repeat=klen):
            key = bytes(key_bytes).decode('latin-1')
            rep_k = key * (len(ct) // len(key)) + key[:len(ct) % len(key)]
            k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
            k_vals = []
            for lst in k_val_list: k_vals += lst
            # decrypt
            m_vals = []
            for i in range(len(c_vals)):
                m_vals.append((c_vals[i] - k_vals[i % len(k_vals)]) & mask)
            # reconstruct message
            m_val_list = [m_vals[i:i+8] for i in range(0, len(m_vals), 8)]
            m = ""
            for lst in m_val_list:
                m += get_chrs(lst, n)
            if m.startswith("flag") or "flag" in m.lower():
                print(f"n={n}, key={key!r}, msg={m!r}")
                with open("solution.py", "w") as f:
                    f.write(f'''import base64

def to_num(s):
    x = 0
    for i in range(len(s)):
        x += ord(s[-1-i]) * pow(256, i)
    return x

def get_nums(s, n):
    sections = [s[i:i+n] for i in range(0, len(s), n)]
    sections[-1] = sections[-1] + ("\\x00" * (n - len(sections[-1])))
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

with open("ciphertext", "rb") as f:
    ct = f.read().decode().strip()
ct = base64.b64decode(ct).decode()

n = {n}
key = {key!r}
mask = (1 << n) - 1
rep_k = key * (len(ct) // len(key)) + key[:len(ct) % len(key)]
k_val_list = [get_vals(to_num(s), n) for s in get_nums(rep_k, n)]
k_vals = []
for lst in k_val_list: k_vals += lst

c_vals = []
for i in range(0, len(ct), 8):
    chunk = ct[i:i+8]
    x = 0
    for c in chunk:
        x = (x << n) | ord(c)
    c_vals.append(x)

m_vals = []
for i in range(len(c_vals)):
    m_vals.append((c_vals[i] - k_vals[i % len(k_vals)]) & mask)

m_val_list = [m_vals[i:i+8] for i in range(0, len(m_vals), 8)]
m = ""
for lst in m_val_list:
    m += get_chrs(lst, n)
print(m)
''')
                break
        else:
            continue
        break
    else:
        continue
    break
