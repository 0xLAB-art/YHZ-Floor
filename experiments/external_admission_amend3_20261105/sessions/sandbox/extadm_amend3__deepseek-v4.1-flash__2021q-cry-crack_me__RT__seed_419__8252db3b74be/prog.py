import base64
import hashlib
import json

with open("README.md", "rb") as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
    text = decoded.decode("utf-8")
except Exception:
    text = raw.decode("utf-8")

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

methods = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "sha512_224", "sha512_256",
    "ripemd128", "ripemd160", "whirlpool", "tiger", "md4",
]

for m in methods:
    try:
        h = hashlib.new(m)
    except ValueError:
        continue
    h.update(b"example")
    if h.hexdigest() == hash_hex:
        print(f"flag{{{m}}}")
        break
else:
    print("flag{}")
