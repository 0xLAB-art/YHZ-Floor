import sys

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r') as f:
    data = f.read().strip()

flag = ''.join(chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8))
print(flag)