with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r', encoding='ascii') as f:
    bits = ''.join(f.read().split())

if len(bits) % 8 or set(bits) - {'0', '1'}:
    raise ValueError('Invalid binary encoding')

text = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
start = text.index('flag{')
end = text.index('}', start) + 1
print(text[start:end])
