import base64

with open("eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi", "rb") as f:
    data = f.read()

text = data.decode("ascii").replace("\n", "")
decoded = base64.b64decode(text).decode("utf-8")

import re
flag = re.search(r"flag\{[^}]+\}", decoded).group(0)
print(flag)