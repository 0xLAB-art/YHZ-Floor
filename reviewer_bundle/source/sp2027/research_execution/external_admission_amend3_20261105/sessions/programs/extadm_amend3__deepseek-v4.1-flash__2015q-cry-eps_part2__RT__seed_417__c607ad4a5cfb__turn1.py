import base64
import re

with open("eps1.9_zer0-day_b7604a922c8feef666a957933751a074.avi", "rb") as f:
    data = f.read()

try:
    decoded = base64.b64decode(data)
except Exception:
    decoded = base64.b64decode(data.decode("utf-8", errors="ignore"))

# The decoded content is base64-encoded text of the original file bytes.
# Decode again.
try:
    decoded2 = base64.b64decode(decoded)
except Exception:
    decoded2 = base64.b64decode(decoded.decode("utf-8", errors="ignore"))

# The result is ROT13-encoded text (looks like malformed CTF challenge text).
import codecs
flag = codecs.decode(decoded2, "rot_13")

# Extract the flag-like string
match = re.search(r"CTF\{[^}]*\}", flag)
if match:
    print(match.group(0))
else:
    print(flag.strip())