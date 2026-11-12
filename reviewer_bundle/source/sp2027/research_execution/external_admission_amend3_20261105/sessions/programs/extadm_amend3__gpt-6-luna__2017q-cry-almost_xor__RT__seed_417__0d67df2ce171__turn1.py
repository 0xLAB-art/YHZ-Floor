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

# Brute force n from 1 to 7
for n in range(1, 8):
    # Each 8-char block of ciphertext corresponds to 8 values of n bits
    # c_vals[i] = (m_vals[i] + k_vals[i % len(k_vals)]) & mask
    # We need to find key k such that decrypting gives valid ASCII
    mask = (1 << n) - 1
    # Reconstruct c_vals from ciphertext
    c_vals = []
    for block in ct:
        x = 0
        for ch in block:
            x = (x << n) | ord(ch)
        c_vals.append(x)
    # c_vals has len(m_vals) = 8 * len(get_nums(m, n))
    # k_vals repeats every len(k) chars, each key char gives 8 values
    # Try all possible keys (small)
    import itertools
    for key_len in range(1, 6):
        for key_chars in itertools.product(range(256), repeat=key_len):
            rep_k = key_chars * (len(c_vals) // (8*key_len)) + key_chars[:len(c_vals) % (8*key_len)]
            k_vals = []
            for kc in rep_k:
                for i in range(8):
                    k_vals.append((kc >> (n*i)) & mask)
            # Actually k_vals order: get_vals gives LSB first then reversed
            # get_vals(x,n): appends x&mask, x>>=n, then reverses -> MSB first
            # So k_vals[i] for key char kc: [ (kc >> (n*(7-i))) & mask for i in range(8) ]
            k_vals = []
            for kc in rep_k:
                for i in range(8):
                    k_vals.append((kc >> (n*(7-i))) & mask)
            m_vals = []
            valid = True
            for i, c in enumerate(c_vals):
                m = (c - k_vals[i % len(k_vals)]) & mask
                if m < 0 or m > 255:
                    valid = False
                    break
                m_vals.append(m)
            if not valid:
                continue
            # Reconstruct message
            # m_vals grouped: each original char -> 8 values (MSB first)
            # m_val_list = [get_vals(x,n) for x in get_nums(m,n)]
            # get_nums splits m into n-byte chunks, each chunk -> 8 values
            # So m_vals[i] for i in range(8) is one byte
            msg = []
            for i in range(0, len(m_vals), 8):
                byte = 0
                for j in range(8):
                    byte = (byte << n) | m_vals[i+j]
                msg.append(byte)
            try:
                decoded = bytes(msg).decode('ascii')
                if decoded.isprintable() or all(32 <= b < 127 or b in (10,13) for b in msg):
                    print(f"n={n}, key={bytes(key_chars)}, flag={decoded}")
            except:
                pass
