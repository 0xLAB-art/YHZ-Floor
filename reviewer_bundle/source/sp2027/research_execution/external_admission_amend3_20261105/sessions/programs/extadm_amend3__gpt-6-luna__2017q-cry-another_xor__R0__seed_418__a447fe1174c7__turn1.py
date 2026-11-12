import base64

data = open("encrypted", "rb").read().strip()
raw = base64.b64decode(data)

# XOR with repeating key "FLAG"
key = b"FLAG"
flag = bytes(b ^ key[i % 4] for i, b in enumerate(raw))
print(flag.decode())
