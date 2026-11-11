import re

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg') as f:
    data = f.read()

bits = re.findall(r'[01]+', data)
flag = ''.join(chr(int(b, 2)) for b in bits)
print(flag)
