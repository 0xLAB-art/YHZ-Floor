import base64

with open("eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg", "rb") as f:
    data = f.read().strip()

b64 = base64.b64decode(data).decode("ascii").replace("\n", "")
bits = b64.replace(" ", "")
byte = int(bits, 2)
flag = byte.to_bytes((byte.bit_length() + 7) // 8, "big")
print(flag.decode("utf-8"))
