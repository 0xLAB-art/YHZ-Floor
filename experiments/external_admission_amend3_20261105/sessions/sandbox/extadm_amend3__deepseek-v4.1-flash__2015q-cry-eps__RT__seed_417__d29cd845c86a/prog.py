import base64

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r') as f:
    data = f.read().replace('\n', '')

bits = base64.b64decode(data).decode('ascii')

result = ''
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) == 8:
        result += chr(int(byte, 2))

print(result)
