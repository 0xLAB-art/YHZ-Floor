import hashlib
import re

with open("README.md", "r", encoding="utf-8") as file:
    text = file.read()

target_match = re.search(r"(?i)\b[0-9a-f]{64}\b", text)
if target_match is None:
    raise RuntimeError("Hash not found")

target = target_match.group(0).lower()
method = "sha256"
candidate = "password"

computed = hashlib.new(method, (candidate + method).encode("ascii")).hexdigest()
if computed != target:
    raise RuntimeError("Preimage verification failed")

print(f"flag{{{candidate}}}")
