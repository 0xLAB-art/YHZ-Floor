import base64

data = base64.b64decode(open('encrypted').read().strip())

# XOR with repeating key derived from known plaintext "FLAG"
key = b'FLAG'
result = bytearray()
for i, b in enumerate(data):
    result.append(b ^ key[i % len(key)])

print(result.decode('utf-8', errors='replace'))