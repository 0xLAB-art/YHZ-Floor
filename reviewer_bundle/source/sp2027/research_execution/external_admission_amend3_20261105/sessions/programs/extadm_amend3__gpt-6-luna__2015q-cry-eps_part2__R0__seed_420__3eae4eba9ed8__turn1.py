import base64

with open("eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi") as f:
    data = f.read()

data = data.replace("\n", "")
decoded = base64.b64decode(data).decode("utf-8")

print(decoded)
