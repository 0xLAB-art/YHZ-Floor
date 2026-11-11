import base64

with open("eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg", "rb") as f:
    data = f.read()

b64 = data.decode("ascii").replace("\n", "").replace(" ", "")
bits = base64.b64decode(b64).decode("ascii")
flag = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
print(flag)
