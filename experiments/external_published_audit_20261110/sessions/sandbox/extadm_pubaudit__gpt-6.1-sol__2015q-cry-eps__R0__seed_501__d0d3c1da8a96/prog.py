import re

filename = 'eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg'
with open(filename, 'rb') as f:
    bits = b''.join(f.read().split())

if len(bits) % 8 or any(c not in b'01' for c in bits):
    raise ValueError('Invalid binary encoding')

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
flags = re.findall(r'flag\{[^{}]*\}', plaintext)
if len(flags) != 1:
    raise ValueError('Expected one explicitly delimited flag')
print(flags[0])
