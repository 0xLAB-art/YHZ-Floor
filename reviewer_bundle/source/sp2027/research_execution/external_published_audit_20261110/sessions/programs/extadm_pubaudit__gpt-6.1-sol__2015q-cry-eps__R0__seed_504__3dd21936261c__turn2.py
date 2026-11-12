import re

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r', encoding='ascii') as f:
    bits = ''.join(f.read().split())

if len(bits) % 8 or any(c not in '01' for c in bits):
    raise ValueError('Invalid binary encoding')

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
flags = re.findall(r'flag\{[^{}\r\n]*\}', plaintext)
if len(flags) != 1:
    raise ValueError('Expected exactly one flag')
print(flags[0])
