import base64

with open("eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg", "r") as f:
    b64 = f.read().replace("\n", "").replace(" ", "")

raw = base64.b64decode(b64)
bits = raw.decode("ascii").strip()

byte_list = [bits[i:i+8] for i in range(0, len(bits), 8)]
flag = "".join(chr(int(b, 2)) for b in byte_list)

print(flag)
