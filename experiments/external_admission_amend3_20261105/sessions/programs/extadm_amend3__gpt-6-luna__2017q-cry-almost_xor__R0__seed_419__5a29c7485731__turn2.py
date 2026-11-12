import re

with open("almostxor.py") as f:
    src = f.read()

ns = re.findall(r"n is too high!\"\n\trep_k = k \* \(len\(m\) \/\/ len\(k\)\) \+ k\[:len\(m\) % len\(k\)\] # repeated key\n\tm_val_list = \[get_vals\(x, (\d+)\) for x in get_nums\(m, \1\)\]",
                 src)
n = int(ns[0])

with open("ciphertext") as f:
    ct = f.read().replace("\n", "").replace(" ", "")

ct_bytes = bytes.fromhex(ct)

key_len = 1
while True:
    key = b""
    ok = True
    for i in range(0, len(ct_bytes), 8):
        block = ct_bytes[i:i+8]
        if len(block) < 8:
            ok = False
            break
        for j in range(8):
            c = block[j]
            k = c ^ ord(key[j % key_len])
            if not (0 <= k <= 127):
                ok = False
                break
        if not ok:
            break
    if ok:
        break
    key_len += 1

print(key.decode())
