filename = 'eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg'
with open(filename, 'rb') as f:
    bits = b''.join(f.read().split())

if not bits or len(bits) % 8 or set(bits) - {48, 49}:
    raise ValueError('Invalid binary-encoded artifact')

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
# The flag is the complete decoded text, including text outside the braces.
print(plaintext.rstrip('\r\n'))
