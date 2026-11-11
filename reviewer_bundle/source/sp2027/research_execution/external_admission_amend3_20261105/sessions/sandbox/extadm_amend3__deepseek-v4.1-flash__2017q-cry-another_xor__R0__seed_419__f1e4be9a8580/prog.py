import re

data = open('encrypted').read().strip()

# Split into (length_byte, data) pairs
pairs = []
i = 0
while i < len(data):
    n = int(data[i:i+2], 16)
    i += 2
    pairs.append(data[i:i+n*2])
    i += n*2

result = []
for chunk in pairs:
    # XOR each byte with the previous byte (first byte XORed with 0x00)
    out = []
    prev = 0
    for j in range(0, len(chunk), 2):
        b = int(chunk[j:j+2], 16)
        out.append(b ^ prev)
        prev = b
    result.append(bytes(out))

flag = b''.join(result).decode('utf-8', errors='replace')
print(flag)
