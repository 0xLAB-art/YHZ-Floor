import base64

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r') as f:
    b64 = f.read().replace('\n', '')

raw = base64.b64decode(b64)
print(raw.decode())
