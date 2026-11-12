def combine(a, b, n, sign):
    bits = 8 * len(a)
    if len(a) != len(b) or bits % n:
        raise ValueError("Invalid block lengths")
    x = int.from_bytes(a, "big")
    y = int.from_bytes(b, "big")
    mask = (1 << n) - 1
    out = 0
    for shift in range(bits - n, -1, -n):
        u = (x >> shift) & mask
        v = (y >> shift) & mask
        out = (out << n) | ((u + sign * v) & mask)
    return out.to_bytes(len(a), "big")

with open("ciphertext", "r", encoding="ascii") as f:
    ciphertext = bytes.fromhex(f.read())

# Exhaustively recover short periodic keys using the flag-format crib.
prefix = b"flag{"
span = len(prefix) + 1
flags = set()
for n in range(1, 8):
    if len(ciphertext) % n or (8 * span) % n:
        continue
    for unknown in range(256):
        probe = prefix + bytes([unknown])
        key_sample = combine(ciphertext[:span], probe, n, -1)
        for period in range(1, span + 1):
            key = key_sample[:period]
            if any(key_sample[i] != key[i % period] for i in range(span)):
                continue
            repeated = (key * ((len(ciphertext) + period - 1) // period))[:len(ciphertext)]
            plaintext = combine(ciphertext, repeated, n, -1)
            if not (plaintext.startswith(prefix) and plaintext.endswith(b"}")):
                continue
            if not all(32 <= c <= 126 for c in plaintext):
                continue
            if combine(plaintext, repeated, n, 1) == ciphertext:
                flags.add(plaintext)

if len(flags) != 1:
    raise RuntimeError("Cryptanalysis did not yield a unique verified flag")
print(next(iter(flags)).decode("ascii"))