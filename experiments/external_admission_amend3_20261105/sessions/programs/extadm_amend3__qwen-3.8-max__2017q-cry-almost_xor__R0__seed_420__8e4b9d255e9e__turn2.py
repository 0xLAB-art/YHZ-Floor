import json

with open("ciphertext") as f:
    ct = f.read().strip().replace("\n", "")

with open("almostxor.py") as f:
    src = f.read()

ns = [1, 2, 3, 4, 5, 6, 7]

for n in ns:
    try:
        nslice = len(ct) // 8 * 8
        ct8 = ct[:nslice]
        vals = []
        for i in range(0, len(ct8), 8):
            chunk = ct8[i:i+8]
            x = 0
            for ch in chunk:
                x = (x << n) | int(ch, 16)
            vals.append(x)
        for key_len in range(1, 32):
            for k_int in range(1 << (key_len * n)):
                rep = ""
                for j in range(len(vals)):
                    kch = (k_int >> ((j % key_len) * n)) & ((1 << n) - 1)
                    mch = (vals[j] - kch) & ((1 << n) - 1)
                    rep += chr(mch)
                try:
                    text = rep.encode().decode("utf-8")
                    if "flag" in text.lower():
                        print(n, key_len, k_int, text)
                except Exception:
                    pass
    except Exception as e:
        pass
