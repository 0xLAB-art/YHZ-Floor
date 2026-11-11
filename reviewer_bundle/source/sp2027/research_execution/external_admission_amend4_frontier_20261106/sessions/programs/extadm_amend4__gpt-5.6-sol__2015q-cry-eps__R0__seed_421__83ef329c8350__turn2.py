filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    data = f.read()
bits = bytes(c for c in data if c in b"01")
if len(bits) % 8:
    raise ValueError("Bitstream length is not byte-aligned")
plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
print(plaintext)
