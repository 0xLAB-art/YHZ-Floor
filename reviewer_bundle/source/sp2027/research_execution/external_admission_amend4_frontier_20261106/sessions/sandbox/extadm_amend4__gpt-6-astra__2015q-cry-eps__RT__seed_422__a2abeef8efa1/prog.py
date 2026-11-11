filename = 'eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg'
with open(filename, 'rb') as artifact:
    bits = b''.join(artifact.read().split())

assert bits and set(bits) <= {48, 49} and len(bits) % 8 == 0
plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode('ascii')
print(plaintext)
