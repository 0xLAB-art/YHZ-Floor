import base64

with open("encrypted") as f:
    data = base64.b64decode(f.read().strip())

flag = ""
for i in range(0, len(data), 2):
    b = data[i:i+2]
    if len(b) < 2:
        break
    hi, lo = b[0], b[1]
    if hi == 0x00:
        flag += chr(lo)
    elif hi == 0x01:
        flag += chr(lo)
    elif hi == 0x02:
        flag += chr(lo ^ 0x20)
    elif hi == 0x03:
        flag += chr(lo ^ 0x21)
    elif hi == 0x04:
        flag += chr(lo ^ 0x22)
    elif hi == 0x05:
        flag += chr(lo ^ 0x23)
    elif hi == 0x06:
        flag += chr(lo ^ 0x24)
    elif hi == 0x07:
        flag += chr(lo ^ 0x25)
    elif hi == 0x08:
        flag += chr(lo ^ 0x26)
    elif hi == 0x09:
        flag += chr(lo ^ 0x27)
    elif hi == 0x0a:
        flag += chr(lo ^ 0x28)
    elif hi == 0x0b:
        flag += chr(lo ^ 0x29)
    elif hi == 0x0c:
        flag += chr(lo ^ 0x2a)
    elif hi == 0x0d:
        flag += chr(lo ^ 0x2b)
    elif hi == 0x0e:
        flag += chr(lo ^ 0x2c)
    elif hi == 0x0f:
        flag += chr(lo ^ 0x2d)
    elif hi == 0x10:
        flag += chr(lo ^ 0x2e)
    elif hi == 0x11:
        flag += chr(lo ^ 0x2f)
    elif hi == 0x12:
        flag += chr(lo ^ 0x30)
    elif hi == 0x13:
        flag += chr(lo ^ 0x31)
    elif hi == 0x14:
        flag += chr(lo ^ 0x32)
    elif hi == 0x15:
        flag += chr(lo ^ 0x33)
    elif hi == 0x16:
        flag += chr(lo ^ 0x34)
    elif hi == 0x17:
        flag += chr(lo ^ 0x35)
    elif hi == 0x18:
        flag += chr(lo ^ 0x36)
    elif hi == 0x19:
        flag += chr(lo ^ 0x37)
    elif hi == 0x1a:
        flag += chr(lo ^ 0x38)
    elif hi == 0x1b:
        flag += chr(lo ^ 0x39)
    elif hi == 0x1c:
        flag += chr(lo ^ 0x3a)
    elif hi == 0x1d:
        flag += chr(lo ^ 0x3b)
    elif hi == 0x1e:
        flag += chr(lo ^ 0x3c)
    elif hi == 0x1f:
        flag += chr(lo ^ 0x3d)

print(flag)
