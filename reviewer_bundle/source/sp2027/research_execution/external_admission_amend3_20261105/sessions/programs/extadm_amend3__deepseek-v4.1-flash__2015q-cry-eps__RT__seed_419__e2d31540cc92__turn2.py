import base64

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg', 'r') as f:
    b64 = f.read().replace('\n', '')

raw = base64.b64decode(b64)
bits = raw.decode('ascii').strip()

# The file is a sequence of '0' and '1' characters.
# Group into 8-bit bytes, convert to characters.
flag = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

print(flag)
