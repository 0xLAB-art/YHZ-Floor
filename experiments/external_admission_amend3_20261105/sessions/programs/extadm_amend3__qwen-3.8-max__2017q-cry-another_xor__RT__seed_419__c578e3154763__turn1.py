import base64

with open("encrypted", "rb") as f:
    data = base64.b64decode(f.read().strip())

flag = ""
for i in range(0, len(data), 2):
    a = data[i]
    b = data[i + 1]
    flag += chr(a ^ b)

print(flag)