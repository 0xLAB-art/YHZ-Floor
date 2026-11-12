import base64

data = base64.b64decode(open("encrypted", "rb").read())

# XOR with a repeating key derived from the pattern
key = b"FLAG"
flag = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
print(flag.decode())