import base64

data = base64.b64decode(open("encrypted").read().strip())

# XOR with repeating key "FLAG"
key = b"FLAG"
flag = bytes(b ^ key[i % 4] for i, b in enumerate(data))
print(flag.decode())