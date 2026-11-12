import json

with open('almostxor.py') as f:
    src = f.read()
ns = {}
exec(src, ns)
encr_vals = ns['encr_vals']
get_chrs = ns['get_chrs']
get_nums = ns['get_nums']
get_vals = ns['get_vals']

c = open('ciphertext').read().replace('\n', '').replace(' ', '')
c_bytes = bytes.fromhex(c)

for n in range(1, 8):
    for key_len in range(1, 33):
        for k in range(256 ** min(key_len, 4)):
            key = k.to_bytes(key_len, 'big')
            rep_k = key * (len(c_bytes) // len(key)) + key[:len(c_bytes) % len(key)]
            m_vals = [get_vals(x, n) for x in get_nums(c_bytes, n)]
            k_vals = [get_vals(x, n) for x in get_nums(rep_k, n)]
            m_vals_flat = []
            for lst in m_vals: m_vals_flat += lst
            k_vals_flat = []
            for lst in k_vals: k_vals_flat += lst
            m_flat = [encr_vals(m_vals_flat[i], k_vals_flat[i % len(k_vals_flat)], n) for i in range(len(m_vals_flat))]
            c_val_list = [m_flat[i:i+8] for i in range(0, len(m_flat), 8)]
            try:
                cand = ''.join([get_chrs(lst, n) for lst in c_val_list])
                if cand.isprintable() and all(32 <= ord(ch) <= 126 for ch in cand):
                    print(cand)
                    break
            except Exception:
                pass
        else:
            continue
        break
    else:
        continue
    break
