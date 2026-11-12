import base64
import hashlib
import json

with open("README.md", "rb") as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
except Exception:
    decoded = raw

content = decoded.decode("utf-8", errors="replace")

hash_hex = None
for line in content.splitlines():
    line = line.strip()
    if line.startswith("Your hash:"):
        hash_hex = line.split(":", 1)[1].strip()
        break

if not hash_hex or len(hash_hex) != 64:
    raise SystemExit("Could not extract 64-char hash")

hash_hex = hash_hex.lower()

candidates = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "ripemd128", "ripemd160", "whirlpool", "tiger", "md4",
]

for alg in candidates:
    try:
        h = hashlib.new(alg)
    except ValueError:
        continue
    h.update(hash_hex.encode("utf-8"))
    if h.hexdigest() == hash_hex:
        print(f"flag{{{alg}}}")
        break
else:
    raise SystemExit("No matching hash algorithm found")
