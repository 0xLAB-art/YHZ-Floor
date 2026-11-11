import base64

with open("eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg", "rb") as f:
    data = f.read()

b64 = data.decode("ascii").replace("\n", "").replace(" ", "")
raw = base64.b64decode(b64)

ones = raw.count(b"1")
zeros = raw.count(b"0")

if ones > zeros:
    flag = raw.replace(b"1", b"0").replace(b"0", b"1")
else:
    flag = raw

print(flag.decode("ascii"))