with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'rb') as f:
    bits = b''.join(f.read().split())

if len(bits) % 8 or set(bits) - {48, 49}:
    raise ValueError('Invalid binary bitstream')

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
print(plaintext.decode('ascii'))