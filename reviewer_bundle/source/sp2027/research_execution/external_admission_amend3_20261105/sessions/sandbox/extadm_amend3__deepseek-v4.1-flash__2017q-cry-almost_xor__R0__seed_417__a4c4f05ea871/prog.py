import json

with open("almostxor.py") as f:
    src = f.read()
ns = {}
exec(src, ns)
to_num, get_nums, get_vals, get_chrs, encr_vals, encrypt = ns["to_num"], ns["get_nums"], ns["get_vals"], ns["get_chrs"], ns["encr_vals"], ns["encrypt"]

c = open("ciphertext").read().strip().replace("\n", "")
c_bytes = bytes.fromhex(c)

# brute force n in 1..7 and key length in 1..8
for n in range(1, 8):
    for kl in range(1, 9):
        # split ciphertext into blocks of kl bytes
        blocks = [c_bytes[i:i+kl] for i in range(0, len(c_bytes), kl)]
        # for each block, try all key bytes
        key = []
        ok = True
        for b in blocks:
            if len(b) < kl:
                b = b + b"\x00" * (kl - len(b))
            # recover key byte from first block (assume plaintext starts with '{')
            if not key:
                first = b[0]
                for kb in range(256):
                    m = encr_vals(ord("{") if len(b) == kl else ord("a"), kb, n)
                    if m == first:
                        key.append(kb)
                        break
                else:
                    ok = False
                    break
            else:
                kb = key[0]
                m = encr_vals(ord("{") if len(b) == kl else ord("a"), kb, n)
                if m != b[0]:
                    ok = False
                    break
        if not ok:
            continue
        # decrypt
        rep_k = bytes(key) * (len(c_bytes) // kl) + bytes(key)[:len(c_bytes) % kl]
        m_vals = [get_vals(x, n) for x in get_nums(c_bytes, kl)]
        k_vals = [get_vals(x, n) for x in get_nums(rep_k, kl)]
        m_vals_flat, k_vals_flat = [], []
        for lst in m_vals: m_vals_flat += lst
        for lst in k_vals: k_vals_flat += lst
        c_vals = [encr_vals(m_vals_flat[i], k_vals_flat[i % len(k_vals_flat)], n)
                  for i in range(0, len(m_vals_flat))]
        c_val_list = [c_vals[i:i+8] for i in range(0, len(c_vals), 8)]
        flag = "".join([get_chrs(lst, n) for lst in c_val_list])
        if flag.startswith("CTF{"):
            print(flag)
            break
    else:
        continue
    break
