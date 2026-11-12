import base64

with open("encrypted") as f:
    data = base64.b64decode(f.read().strip())

out = bytearray()
for i in range(0, len(data), 2):
    b = data[i:i+2]
    if len(b) < 2:
        break
    hi, lo = b[0], b[1]
    out.append((hi << 4) | lo)

print(out.decode("ascii"))
