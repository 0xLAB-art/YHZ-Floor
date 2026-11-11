import base64
import hashlib

hash_b64 = "QTYwNDU4ZDIxODAyNThkNDdkN2Y3YmVmNTIzNmIzM2U4NjcxMWFjOTI2NTE4Y2E0NTQ1ZWJmMjRjZGMwYjc2Yw=="
hash_hex = base64.b64decode(hash_b64).decode().split("\n")[1].strip()

methods = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "sha512_224", "sha512_256", "sha384_256", "sha384_224",
    "ripemd128", "ripemd160", "ripemd256", "ripemd320",
    "whirlpool", "tiger", "sm3",
]

for m in methods:
    try:
        h = hashlib.new(m)
    except ValueError:
        continue
    for word in ["ripemd128", "ripemd160", "ripemd256", "ripemd320", "md5", "sha1", "sha256", "sha512", "blake2b", "blake2s", "whirlpool", "sm3", "tiger", "sha3_256", "sha3_512", "sha224", "sha384", "sha512_224", "sha512_256", "sha384_256", "sha384_224", "sha3_224", "sha3_384"]:
        h.update(word.encode())
        if h.hexdigest() == hash_hex:
            print(f"flag{{{word}}}")
            break
    else:
        continue
    break
