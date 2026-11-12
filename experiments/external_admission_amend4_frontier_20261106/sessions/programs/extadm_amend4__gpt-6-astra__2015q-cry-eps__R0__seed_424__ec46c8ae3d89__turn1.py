with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'rb') as f:
    bits = b''.join(f.read().split())
assert bits and len(bits) % 8 == 0 and all(c in b'01' for c in bits)
plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
print(plaintext)
