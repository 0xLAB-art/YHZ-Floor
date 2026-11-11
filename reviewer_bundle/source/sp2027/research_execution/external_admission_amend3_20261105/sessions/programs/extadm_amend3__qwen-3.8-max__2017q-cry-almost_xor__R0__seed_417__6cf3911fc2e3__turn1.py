import json

with open("ciphertext") as f:
    ct = "".join(f.read().split())

# The cipher: n-bit addition modulo 2^n with a repeated key.
# n is small (n < 8). We brute-force n and the key.
# ct is hex-encoded; each byte of ct corresponds to n-bit chunks.

for n in range(1, 8):
    mask = (1 << n) - 1
    # ct length in bytes must be divisible by 8/n (each output char holds 8/n n-bit values)
    if len(ct) % (8 // n) != 0:
        continue
    # Try key lengths 1..16
    for kl in range(1, 17):
        # brute force key bytes
        import itertools
        for key_bytes in itertools.product(range(256), repeat=kl):
            key = bytes(key_bytes)
            rep_k = key * (len(ct) // len(key)) + key[:len(ct) % len(key)]
            # decrypt: m = (c - k) mod 2^n per n-bit chunk
            ok = True
            m_vals = []
            for i in range(len(ct)):
                c_byte = int(ct[i], 16)
                k_byte = rep_k[i % len(rep_k)]
                m_byte = (c_byte - k_byte) & mask
                m_vals.append(m_byte)
            # reconstruct bytes: every 8/n values form one byte
            per = 8 // n
            if len(m_vals) % per != 0:
                continue
            m_bytes = []
            for j in range(0, len(m_vals), per):
                b = 0
                for v in m_vals[j:j+per]:
                    b = (b << n) | v
                m_bytes.append(b)
            try:
                m = bytes(m_bytes).decode("ascii")
            except Exception:
                continue
            if m.startswith("flag") or "CTF" in m or all(32 <= b < 127 for b in m_bytes):
                print(m)
                raise SystemExit
