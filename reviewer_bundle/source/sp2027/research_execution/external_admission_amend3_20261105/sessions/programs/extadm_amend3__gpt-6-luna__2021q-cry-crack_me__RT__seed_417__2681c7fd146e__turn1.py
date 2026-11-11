import base64
import hashlib
import json

with open("README.md", "rb") as f:
    raw = f.read()

with open("README.md", "w", encoding="utf-8") as f:
    f.write(base64.b64decode(raw).decode("utf-8"))

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

hash_target = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

methods = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "md4", "md5-sha1",
    "ripemd128", "ripemd160", "ripemd256", "ripemd320",
    "whirlpool", "tiger", "sha512_224", "sha512_256",
    "sha3_256", "shake_128", "shake_256",
]

for method in methods:
    try:
        h = hashlib.new(method)
    except ValueError:
        continue
    h.update(b"example")
    if h.hexdigest() == hash_target:
        print(f"flag{{{{{method}}}}}")
        break
else:
    print("flag{}")