import re

with open('eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg') as f:
    data = f.read().strip()

# Remove the file extension marker and any non-binary characters
binary = re.sub(r'[^01]', '', data)

# Split into 8-bit chunks and convert to characters
flag = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

print(flag)
