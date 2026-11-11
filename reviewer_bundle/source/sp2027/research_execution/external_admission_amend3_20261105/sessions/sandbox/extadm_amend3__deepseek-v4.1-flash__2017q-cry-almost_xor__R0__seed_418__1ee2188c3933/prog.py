import json

with open("almostxor.py") as f:
    src = f.read()

ns = [1, 2, 3, 4, 5, 6, 7]

exec(src)

with open("ciphertext", "rb") as f:
    ct = f.read().strip()
ct = ct.decode("ascii")

for n in ns:
    for key_len in range(1, 13):
        for guess in range(256 ** key_len):
            k = guess.to_bytes(key_len, "big")
            try:
                m = encrypt(k, ct, n)
            except Exception:
                continue
            if m.startswith("flag") or b"CTF" in m.encode():
                print(n, k.hex(), m)
                break
        else:
            continue
        break
    else:
        continue
    break