import base64

with open("encrypted", "rb") as f:
    data = base64.b64decode(f.read().strip())

flag = ""
for i in range(0, len(data), 2):
    b0 = data[i]
    b1 = data[i + 1] if i + 1 < len(data) else 0
    flag += chr(b0 ^ b1)

print(flag)
