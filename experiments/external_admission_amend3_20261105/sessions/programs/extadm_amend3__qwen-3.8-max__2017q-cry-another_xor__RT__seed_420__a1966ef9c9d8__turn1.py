import base64

with open("encrypted", "rb") as f:
    data = base64.b64decode(f.read().strip())

flag = ""
for i in range(0, len(data), 2):
    b = data[i]
    if i + 1 < len(data):
        b ^= data[i + 1]
    flag += chr(b)

print(flag)
