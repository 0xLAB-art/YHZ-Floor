filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    raw = f.read()

bits = bytes(b for b in raw if b in (48, 49)).decode("ascii")
if not bits or len(bits) % 8 != 0:
    raise ValueError("Invalid binary ciphertext")

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
print(plaintext)
