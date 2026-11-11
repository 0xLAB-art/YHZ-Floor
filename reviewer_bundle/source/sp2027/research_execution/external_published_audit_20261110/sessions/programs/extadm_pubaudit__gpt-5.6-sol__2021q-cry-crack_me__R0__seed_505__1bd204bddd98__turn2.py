import hashlib
import re

with open("README.md", "r", encoding="utf-8") as f:
    text = f.read()

target = re.search(r"(?i)\b[0-9a-f]{64}\b", text).group(0).lower()
word = "password"
salt = "sha256"

assert hashlib.sha256((word + salt).encode()).hexdigest() == target
print(f"flag{{{word}}}")
