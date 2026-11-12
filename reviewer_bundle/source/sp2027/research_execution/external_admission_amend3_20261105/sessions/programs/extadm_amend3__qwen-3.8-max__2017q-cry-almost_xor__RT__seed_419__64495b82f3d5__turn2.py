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
with open('ciphertext', 'rb') as f:
    ct_bytes = f.read()
ciphertext = ct_bytes.decode('latin-1').strip()

# Try all n from 1 to 7
for n in range(1, 8):
    # Decode base64
    try:
        ct_decoded = base64.b64decode(ciphertext).decode('latin-1')
    except Exception:
        continue
    
    # Reconstruct: ciphertext is concatenation of get_chrs blocks
    # Each block of 8 vals -> n bytes. Total length must be divisible by n
    if len(ct_decoded) % n != 0:
        continue
    
    num_blocks = len(ct_decoded) // n
    # Each block has 8 values, so total values = 8 * num_blocks
    # m_vals length = 8 * num_blocks
    # k_vals length = 8 * len(rep_k) where rep_k = k * (len(m)//len(k)) + k[:len(m)%len(k)]
    
    # Try to brute force key: key length 1..len(m), key chars 0..255
    # m length = 8 * num_blocks
    m_len = 8 * num_blocks
    
    # For each possible key length
    for k_len in range(1, min(m_len, 32) + 1):
        rep_len = m_len  # rep_k has length m_len
        k_vals_len = 8 * rep_len
        
        # c_vals[i] = (m_vals[i] + k_vals[i % k_vals_len]) & mask
        # k_vals derived from key: get_vals of each byte of rep_k
        
        # We need to find key such that decrypted m is printable ASCII / flag-like
        # Brute force key of length k_len: 256^k_len too big for k_len > 4
        # But we can use known structure: try k_len small
        
        if k_len > 4:
            continue
        
        mask = (1 << n) - 1
        
        # Build c_val_list
        c_val_list = [list(ct_decoded[i*n:(i+1)*n]) for i in range(num_blocks)]
        c_vals = []
        for block in c_val_list:
            x = 0
            for ch in block:
                x = (x << n) + ord(ch)
            c_vals.append(x)
        # c_vals is list of 8-val numbers; flatten
        flat_c = []
        for x in c_vals:
            flat_c.extend(get_vals(x, n))
        
        # Now brute force key
        from itertools import product
        for key_tuple in product(range(256), repeat=k_len):
            key = ''.join(chr(b) for b in key_tuple)
            rep_k = key * (m_len // k_len) + key[:m_len % k_len]
            k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
            k_vals = []
            for lst in k_val_list:
                k_vals += lst
            
            m_vals = []
            for i in range(len(flat_c)):
                m_vals.append((flat_c[i] - k_vals[i % len(k_vals)]) & mask)
            
            # Reconstruct message
            m_val_list = [m_vals[i:i+8] for i in range(0, len(m_vals), 8)]
            m = ""
            for lst in m_val_list:
                m += get_chrs(lst, n)
            
            # Check if printable
            if all(32 <= ord(c) < 127 for c in m):
                print(f"n={n}, key={key!r}, m={m!r}")
                with open('solution.py', 'w') as f:
                    f.write('''import base64

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

def decrypt(n, key, ciphertext):
    ct_decoded = base64.b64decode(ciphertext).decode('latin-1').strip()
    mask = (1 << n) - 1
    num_blocks = len(ct_decoded) // n
    m_len = 8 * num_blocks
    k_len = len(key)
    rep_k = key * (m_len // k_len) + key[:m_len % k_len]
    k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
    k_vals = []
    for lst in k_val_list:
        k_vals += lst
    c_val_list = [list(ct_decoded[i*n:(i+1)*n]) for i in range(num_blocks)]
    flat_c = []
    for block in c_val_list:
        x = 0
        for ch in block:
            x = (x << n) + ord(ch)
        flat_c.extend(get_vals(x, n))
    m_vals = []
    for i in range(len(flat_c)):
        m_vals.append((flat_c[i] - k_vals[i % len(k_vals)]) & mask)
    m_val_list = [m_vals[i:i+8] for i in range(0, len(m_vals), 8)]
    m = ""
    for lst in m_val_list:
        m += get_chrs(lst, n)
    return m

if __name__ == "__main__":
    key = ''' + repr(key) + '''
    n = ''' + str(n) + '''
    with open('ciphertext', 'rb') as f:
        ct = f.read()
    print(decrypt(n, key, ct.decode('latin-1')))
''')
                break
        else:
            continue
        break
    else:
        continue
    break
