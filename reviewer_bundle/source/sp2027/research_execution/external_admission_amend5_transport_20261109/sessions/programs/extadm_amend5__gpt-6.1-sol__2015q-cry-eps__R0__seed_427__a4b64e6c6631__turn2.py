import re

filename = 'eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg'
with open(filename, 'r', encoding='ascii') as f:
    bits = ''.join(f.read().split())

if not bits or len(bits) % 8 or re.fullmatch(r'[01]+', bits) is None:
    raise ValueError('Invalid binary artifact')

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
flags = re.findall(r'flag\{[^{}\r\n]*\}', plaintext)
if len(flags) != 1:
    raise ValueError('Expected exactly one explicitly delimited flag')
print(flags[0])