import base64

with open("eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi", "rb") as f:
    data = f.read()

# The file contains base64-encoded text with newlines
b64 = data.decode("ascii").replace("\n", "").replace("\r", "")
decoded = base64.b64decode(b64)

# Extract the flag from the decoded message
import re
match = re.search(r'flag\{[^}]+\}', decoded.decode("utf-8"))
print(match.group(0))