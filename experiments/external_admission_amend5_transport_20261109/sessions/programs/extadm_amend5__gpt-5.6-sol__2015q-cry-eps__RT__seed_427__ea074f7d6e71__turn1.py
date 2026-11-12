filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    raw = f.read()

bits = bytes(c for c in raw if c in (48, 49))
if len(bits) % 8 != 0:
    raise ValueError("Bit stream length is not divisible by 8")

flag = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
print(flag.decode("utf-8").strip())
