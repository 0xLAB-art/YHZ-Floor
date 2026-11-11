import re

with open("ciphertext") as f:
    ct = f.read().strip().replace("\n", "")

with open("almostxor.py") as f:
    src = f.read()

# Extract n from the source: find the call to encrypt(..., n) or the value of n used.
# The script uses a fixed n; inspect the source for the encrypt call.
match = re.search(r"encrypt\(([^)]+)\)", src)
if match:
    args = match.group(1).split(",")
    n = int(args[-1].strip())
else:
    n = 4  # fallback

# Brute force key length and key bytes
from itertools import product

key_len = 1
while True:
    found = False
    for key_bytes in product(range(256), repeat=key_len):
        key = bytes(key_bytes).decode("latin-1")
        try:
            # simulate encrypt
            rep_k = key * (len(ct) // len(key)) + key[:len(ct) % len(key)]
            m_val_list = [get_vals(x, n) for x in get_nums(ct, n)]
            k_val_list = [get_vals(x, n) for x in get_nums(rep_k, n)]
            m_vals, k_vals = [], []
            for lst in m_val_list: m_vals += lst
            for lst in k_val_list: k_vals += lst
            c_vals = [encr_vals(m_vals[i], k_vals[i % len(k_vals)], n) for i in range(len(m_vals))]
            c_val_list = [c_vals[i:i+8] for i in range(0, len(c_vals), 8)]
            dec = "".join([get_chrs(lst, n) for lst in c_val_list])
            if dec.startswith("flag"):
                print(dec)
                found = True
                break
        except Exception:
            pass
    if found:
        break
    key_len += 1
    if key_len > 8:
        break
