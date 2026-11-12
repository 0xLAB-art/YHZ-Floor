import base64

with open("encrypted") as f:
    data = base64.b64decode(f.read().strip())

flag = ""
for i in range(0, len(data), 2):
    hi = data[i]
    lo = data[i+1] if i+1 < len(data) else 0
    flag += chr(hi ^ lo)

print(flag)