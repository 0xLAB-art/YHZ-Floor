import base64, hashlib, json, os

with open("README.md", "rb") as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
except Exception:
    decoded = raw

content = decoded.decode("utf-8", errors="replace")

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

methods = [
    "md5",
    "sha1",
    "sha224",
    "sha256",
    "sha384",
    "sha512",
    "sha3_224",
    "sha3_256",
    "sha3_384",
    "sha3_512",
    "blake2b",
    "blake2s",
    "ripemd128",
    "ripemd160",
    "whirlpool",
    "shake_128",
    "shake_256",
]

for method in methods:
    try:
        h = hashlib.new(method)
    except ValueError:
        continue
    try:
        h.update(b"example")
        digest = h.hexdigest()
    except Exception:
        continue
    if digest.lower() == hash_hex.lower():
        print(f"flag{{{method}}}")
        break
else:
    print("flag{}")
