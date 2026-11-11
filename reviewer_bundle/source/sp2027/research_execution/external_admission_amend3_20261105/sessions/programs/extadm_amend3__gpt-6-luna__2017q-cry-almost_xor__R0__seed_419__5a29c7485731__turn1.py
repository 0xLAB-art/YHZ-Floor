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
    if (n >= 8):
        raise ValueError("n is too high!")
    rep_k = k * (len(m) // len(k)) + k[:len(m) % len(k)]
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
        for key in (b"flag", b"CTF", b"key", b"secret", b"password", b"test", b"abc", b"xor", b"crypto", b"flag{", b"{", b"\x00" * key_len):
            try:
                res = encrypt(key.decode("latin-1"), "A" * len(ct_bytes), n)
                if res == ct:
                    print(key.decode("latin-1"))
                    break
            except Exception:
                pass
        else:
            continue
        break
    else:
        continue
    break

# Brute force key bytes given n and key length via known plaintext 'A'
for n in range(1, 8):
    for key_len in range(1, 17):
        target = ct
        # derive key from known plaintext 'A' * len
        key = ""
        ok = True
        for i in range(key_len):
            # compute what key byte would produce target byte at position i
            # encrypt('A', 'A'*L, n) and compare
            pass
        # simpler: brute force each key byte independently
        key = ""
        for i in range(key_len):
            found = False
            for kb in range(256):
                k = key + chr(kb)
                try:
                    res = encrypt(k, "A" * len(target), n)
                except Exception:
                    continue
                if res == target:
                    key = k
                    found = True
                    break
            if not found:
                ok = False
                break
        if ok:
            print(key)
            sys.exit(0)
