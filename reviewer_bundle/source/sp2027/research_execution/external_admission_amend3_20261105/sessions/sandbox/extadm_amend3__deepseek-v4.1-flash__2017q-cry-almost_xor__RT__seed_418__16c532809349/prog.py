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
              for i in range(len(m_vals))]
    c_val_list = [c_vals[i:i+8] for i in range(0, len(c_vals), 8)]
    return "".join([get_chrs(lst, n) for lst in c_val_list])

# Read ciphertext
with open('ciphertext', 'rb') as f:
    ct = f.read().decode().strip()
ct = base64.b64decode(ct).decode()

# Brute force n in [1..7] and key
import string
for n in range(1, 8):
    # c_val_list: each group of 8 values, each value in [0, 2^n)
    c_val_list = [list(get_nums(ct[i:i+n], n)) for i in range(0, len(ct), n)]
    # flatten
    c_vals = [v for grp in c_val_list for v in grp]
    # key length unknown; try key lengths 1..len(ct)
    for kl in range(1, len(ct)+1):
        # k_vals = enc(m_vals, c_vals) -> m_vals[i] = c_vals[i] - k_vals[i % len(k_vals)]
        # We need m_vals to be valid: each byte of plaintext in printable range
        # Try all possible keys of length kl over printable chars
        # Instead: derive key from first block
        # m_vals[i] = c_vals[i] - k_vals[i % kl] (mod 2^n)
        # k_vals[i % kl] = (c_vals[i] - m_vals[i]) mod 2^n
        # Try key = first kl chars; derive m_vals, check printable
        # Brute force key over printable set
        import itertools
        for key in itertools.product(string.printable, repeat=kl):
            key = ''.join(key)
            rep_k = key * (len(ct)//len(key)) + key[:len(ct)%len(key)]
            k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
            k_vals = [v for grp in k_val_list for v in grp]
            m_vals = [(c_vals[i] - k_vals[i % len(k_vals)]) % (1<<n) for i in range(len(c_vals))]
            # reconstruct plaintext
            m_val_list = [m_vals[i:i+8] for i in range(0, len(m_vals), 8)]
            m = ''.join(get_chrs(lst, n) for lst in m_val_list)
            if all(c in string.printable for c in m):
                print(m)
                raise SystemExit
