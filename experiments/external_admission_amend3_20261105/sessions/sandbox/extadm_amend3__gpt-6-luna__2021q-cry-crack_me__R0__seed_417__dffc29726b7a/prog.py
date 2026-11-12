import hashlib
import json

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

with open("README.md", "r") as f:
    readme = f.read()

methods = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "sha512_224", "sha512_256",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
]

for method in methods:
    try:
        h = hashlib.new(method)
        h.update(b"example")
        if h.hexdigest() == hash_hex:
            print(f"flag{{example}}")
            break
    except ValueError:
        pass
else:
    print("flag{unknown}")
