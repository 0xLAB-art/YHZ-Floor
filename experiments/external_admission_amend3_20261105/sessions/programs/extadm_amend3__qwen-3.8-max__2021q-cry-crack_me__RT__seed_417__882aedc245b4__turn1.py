import hashlib
import base64

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

with open("README.md", "rb") as f:
    readme = f.read()

salt = base64.b64decode(readme).decode("utf-8")

for method in ["md5", "sha1", "sha256", "sha512", "ripemd128", "ripemd160", "sha3_256", "sha3_512", "blake2b", "blake2s", "whirlpool", "tiger", "md4", "md2", "sha384", "sha224", "sha512_224", "sha512_256", "shake_128", "shake_256"]:
    try:
        h = hashlib.new(method)
        h.update(salt.encode("utf-8"))
        if h.digest_size == 32:
            if h.hexdigest() == hash_hex:
                print(f"flag{{{salt}}}")
                break
    except ValueError:
        pass
