filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "r", encoding="ascii") as f:
    bits = "".join(c for c in f.read() if c in "01")

if len(bits) % 8 != 0:
    raise ValueError("Bit stream length is not byte-aligned")

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
print(plaintext)
