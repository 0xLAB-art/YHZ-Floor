import base64

with open("eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi", "rb") as f:
    data = f.read()

decoded = base64.b64decode(data)
print(decoded.decode("utf-8"))