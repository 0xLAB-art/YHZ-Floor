import base64

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'rb') as f:
    data = f.read()

b64 = base64.b64decode(data).decode('ascii').replace('\n', '')
bits = ''.join(str(int(b)) for b in b64)

out = ''
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) == 8:
        out += chr(int(byte, 2))

print(out)
