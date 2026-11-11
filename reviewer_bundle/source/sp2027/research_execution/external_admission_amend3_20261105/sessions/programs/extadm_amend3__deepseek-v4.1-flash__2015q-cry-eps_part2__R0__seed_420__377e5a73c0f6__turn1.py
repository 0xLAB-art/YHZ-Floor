import base64

with open("eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi", "rb") as f:
    data = f.read()

b64 = data.decode("ascii").replace("\n", "")
decoded = base64.b64decode(b64)
print(decoded.decode("ascii"))