import base64

data = base64.b64decode(open('encrypted').read().strip())

# XOR with repeating key derived from the first bytes
key = b'FLAG'
flag = ''.join(chr(b ^ key[i % len(key)]) for i, b in enumerate(data))
print(flag)
