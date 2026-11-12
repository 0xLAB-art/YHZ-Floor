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
    if (n >= 8):
        raise ValueError("n is too high!")
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

def decrypt(c, k, n):
    if (n >= 8):
        raise ValueError("n is too high!")
    rep_k = k * (len(c) // len(k)) + k[:len(c) % len(k)]
    c_val_list = [get_vals(x, n) for x in get_nums(c, n)]
    k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
    c_vals = []
    for lst in c_val_list: c_vals += lst
    k_vals = []
    for lst in k_val_list: k_vals += lst
    m_vals = [(c_vals[i] - k_vals[i % len(k_vals)]) & ((1 << n) - 1)
              for i in range(0, len(c_vals))]
    m_val_list = [m_vals[i:i+8] for i in range(0, len(m_vals), 8)]
    return "".join([get_chrs(lst, n) for lst in m_val_list])

cipher = base64.b64decode(open("ciphertext", "rb").read()).decode()
for n in range(1, 8):
    for k in ["flag", "ctf", "xor", "key", "secret", "password", "admin", "test", "qwen", "alibaba", "model", "answer", "solution", "decode", "decrypt", "almost", "almostxor", "cryptanalysis", "agent", "offline", "benchmark", "metadata", "provided", "artifact", "file", "base64", "python", "source", "solve", "flag{", "}"]:
        try:
            res = decrypt(cipher, k, n)
            if res.startswith("flag") or "flag{" in res:
                print(res)
        except Exception:
            pass
