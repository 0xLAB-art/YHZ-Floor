filename = 'eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg'
with open(filename, 'rb') as f:
    bits = b''.join(f.read().split())
if len(bits) % 8 or any(b not in (48, 49) for b in bits):
    raise ValueError('Invalid binary encoding')
plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
print(plaintext.decode('utf-8'))
