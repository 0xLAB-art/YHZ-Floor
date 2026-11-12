import base64

with open("encrypted", "rb") as f:
    data = base64.b64decode(f.read().strip())

flag = ""
for i in range(0, len(data), 2):
    b = data[i]
    if b == 0x00:
        flag += " "
    elif b == 0x0A:
        flag += "\n"
    elif b == 0x0D:
        flag += "\r"
    elif b == 0x09:
        flag += "\t"
    elif 0x20 <= b <= 0x7E:
        flag += chr(b)
    else:
        flag += chr(b ^ 0x20)

print(flag)
