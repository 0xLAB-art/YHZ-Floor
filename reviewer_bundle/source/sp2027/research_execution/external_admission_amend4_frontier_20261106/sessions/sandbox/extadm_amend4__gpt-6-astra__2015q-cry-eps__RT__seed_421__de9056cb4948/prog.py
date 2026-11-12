import base64

filename = 'eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg'
with open(filename, 'rb') as f:
    data = f.read()

bits = b''.join(data.split())
if any(c not in b'01' for c in bits):
    bits = b''.join(base64.b64decode(data).split())

if not bits or len(bits) % 8 or any(c not in b'01' for c in bits):
    raise ValueError('Invalid binary encoding')

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
print(plaintext.decode('utf-8').rstrip('\r\n'))
