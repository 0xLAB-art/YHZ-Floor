import base64

with open("eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi", "rb") as f:
    b64 = f.read().decode().replace("\n", "")
data = base64.b64decode(b64)
print(data.decode())