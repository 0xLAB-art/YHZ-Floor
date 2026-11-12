import base64

with open("eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg", "rb") as f:
    data = f.read()

decoded = base64.b64decode(data).decode("ascii").strip()
flag = bytes.fromhex(decoded).decode("utf-8")
print(flag)
