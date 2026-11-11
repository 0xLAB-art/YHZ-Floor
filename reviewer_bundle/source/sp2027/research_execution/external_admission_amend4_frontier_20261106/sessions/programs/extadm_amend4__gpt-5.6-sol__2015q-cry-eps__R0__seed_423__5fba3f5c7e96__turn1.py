filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    bits = b"".join(f.read().split())

if not bits or any(c not in b"01" for c in bits) or len(bits) % 8 != 0:
    raise ValueError("Invalid binary-encoded artifact")

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
print(plaintext)
