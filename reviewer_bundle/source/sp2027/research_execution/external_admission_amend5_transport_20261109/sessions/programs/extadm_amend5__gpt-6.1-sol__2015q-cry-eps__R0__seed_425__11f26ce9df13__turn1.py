with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r', encoding='ascii') as f:
    bits = ''.join(f.read().split())

if not bits or len(bits) % 8 or any(c not in '01' for c in bits):
    raise ValueError('Invalid binary artifact')

answer = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
print(answer)
