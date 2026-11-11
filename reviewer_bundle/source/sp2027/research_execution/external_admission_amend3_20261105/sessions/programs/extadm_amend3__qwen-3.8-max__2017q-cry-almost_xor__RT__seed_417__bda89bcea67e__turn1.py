import base64

with open("almostxor.py", "rb") as f:
    src = base64.b64decode(f.read()).decode()
exec(src)

with open("ciphertext", "rb") as f:
    ct = base64.b64decode(f.read()).decode().strip()

# Brute force n in [1,7] and key length in [1, len(ct)]
for n in range(1, 8):
    for klen in range(1, len(ct) + 1):
        # Try all possible keys of length klen
        # Key repeats to match message length
        # We can recover key by trying all 256^klen possibilities only if small
        # Instead, use known structure: key is printable-ish
        pass

# Better approach: since key repeats, and we know ciphertext, brute force key
# Key length is likely small. Try all keys of length up to 8 with printable chars
import string

for n in range(1, 8):
    for klen in range(1, 9):
        # Generate candidate keys
        if klen <= 4:
            chars = string.printable.replace(" ", "")
            from itertools import product
            for key in product(chars, repeat=klen):
                key = "".join(key)
                try:
                    dec = encrypt(key, ct, n)
                    if dec.isprintable() and all(c in string.printable for c in dec):
                        print(key, dec)
                except:
                    pass
