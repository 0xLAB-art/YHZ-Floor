with open("encrypted", "r", encoding="ascii") as f:
    ciphertext = bytes.fromhex(f.read())

crib = b"A quart jar of oil mixed with zinc ox"
flag = bytes(c ^ p for c, p in zip(ciphertext, crib)).decode("ascii")

if not (flag.startswith("flag{") and flag.endswith("}")):
    raise ValueError("Failed to recover flag")

print(flag)