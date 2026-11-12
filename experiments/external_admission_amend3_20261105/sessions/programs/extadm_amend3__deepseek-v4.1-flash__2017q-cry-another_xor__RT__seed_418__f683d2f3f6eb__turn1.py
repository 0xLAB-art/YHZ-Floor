import base64

with open("encrypted", "rb") as f:
    data = base64.b64decode(f.read().strip())

key = b"FLAG"
flag = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
print(flag.decode())