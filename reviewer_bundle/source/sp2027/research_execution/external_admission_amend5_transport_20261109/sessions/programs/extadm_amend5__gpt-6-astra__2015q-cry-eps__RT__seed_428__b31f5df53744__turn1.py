with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'rb') as f:
    bits = b''.join(f.read().split())

if not bits or len(bits) % 8 or any(c not in b'01' for c in bits):
    raise ValueError('Invalid binary text')

answer = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
print(answer)
