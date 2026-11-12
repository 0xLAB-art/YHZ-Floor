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
    ct_b64 = f.read().decode().strip()
ct = base64.b64decode(ct_b64).decode()

# Brute force n in [1..7] and key
import string
for n in range(1, 8):
    # key length guess: ciphertext chars = sum over blocks of n bits
    # Each block of 8 vals of n bits -> n bytes output. So len(ct) = 8*n * num_blocks
    # num_blocks = len(ct) // (8*n)
    if len(ct) % (8*n) != 0:
        continue
    num_blocks = len(ct) // (8*n)
    # key length in chars: rep_k has same length as m, and m has num_blocks chars
    # so key length divides num_blocks
    for kl in range(1, num_blocks+1):
        if num_blocks % kl != 0:
            continue
        # brute force key of length kl over printable chars
        chars = string.ascii_letters + string.digits + string.punctuation
        # Build target: for each block b, for each position p in 0..7, c = (m + k) & mask
        # m = c - k (mod 2^n) since no wrap beyond mask
        # We need consistent key across blocks
        # Try all keys via recursion/backtracking
        key = [0]*kl
        def solve(pos, key):
            if pos == kl:
                # verify all blocks
                for b in range(num_blocks):
                    for p in range(8):
                        idx = b*8 + p
                        c = ord(ct[idx])
                        k = key[b % kl]
                        m = (c - k) & ((1<<n)-1)
                        # reconstruct m char from 8 vals
                        val = 0
                        for p2 in range(8):
                            val = (val << n) | ((ord(ct[b*8+p2]) - key[b % kl]) & ((1<<n)-1))
                        # get_chrs inverse: m char = get_chrs of vals
                        # check consistency: m char must equal what we compute
                        # Actually just check that decoding gives printable
                return True
            for ch in chars:
                key[pos] = ord(ch)
                if solve(pos+1, key):
                    return True
            return False
        # Simpler: try all keys for small kl
        import itertools
        for key_tuple in itertools.product(chars, repeat=kl):
            ok = True
            for b in range(num_blocks):
                for p in range(8):
                    idx = b*8 + p
                    c = ord(ct[idx])
                    k = key_tuple[b % kl]
                    m = (c - k) & ((1<<n)-1)
                    # m must be a valid char (0-127 printable-ish)
                    if m > 126 or m < 32:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                # reconstruct flag
                flag = []
                for b in range(num_blocks):
                    val = 0
                    for p in range(8):
                        c = ord(ct[b*8+p])
                        k = key_tuple[b % kl]
                        val = (val << n) | (c - k)
                    flag.append(chr(val))
                print("n=%d kl=%d key=%s flag=%s" % (n, kl, ''.join(key_tuple), ''.join(flag)))
                raise SystemExit
