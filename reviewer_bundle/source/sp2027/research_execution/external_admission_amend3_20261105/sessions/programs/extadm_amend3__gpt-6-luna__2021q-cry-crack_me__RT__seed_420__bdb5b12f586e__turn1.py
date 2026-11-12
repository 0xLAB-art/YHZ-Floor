import base64
import hashlib
import json
import os
import re

with open("README.md", "rb") as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw).decode("utf-8")
except Exception:
    decoded = raw.decode("utf-8")

hash_hex = None
for line in decoded.splitlines():
    m = re.search(r"Your hash:\s*([0-9a-fA-F]{64})", line)
    if m:
        hash_hex = m.group(1).lower()
        break

if not hash_hex:
    raise SystemExit("hash not found")

methods = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "sha512_224", "sha512_256",
    "ripemd128", "ripemd160", "whirlpool", "tiger", "md4",
]

for method in methods:
    try:
        h = hashlib.new(method)
    except ValueError:
        continue
    h.update(hash_hex.encode("utf-8"))
    if h.hexdigest() == hash_hex:
        print(f"flag{{{method}}}")
        break
else:
    raise SystemExit("no match")
