import base64

b64 = open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r').read()
data = base64.b64decode(b64)
bits = ''.join(format(b, '08b') for b in data)
flag = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))
print(flag)
