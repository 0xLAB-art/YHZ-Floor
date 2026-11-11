import re

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r') as f:
    data = f.read().strip()

binary = re.sub(r'[^01]', '', data)
flag = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
print(flag)