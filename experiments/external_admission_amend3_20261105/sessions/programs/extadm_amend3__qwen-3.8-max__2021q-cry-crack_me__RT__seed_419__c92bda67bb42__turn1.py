import base64, hashlib

with open("README.md") as f:
    data = f.read().strip()

raw = base64.b64decode(data).decode("utf-8")

import re
m = re.search(r"Your hash:\s*([A-Fa-f0-9]+)", raw)
hash_hex = m.group(1)

hashes = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
    "sha224": hashlib.sha224,
    "sha384": hashlib.sha384,
    "ripemd128": hashlib.new("ripemd128"),
    "ripemd160": hashlib.new("ripemd160"),
    "whirlpool": hashlib.new("whirlpool"),
    "tiger": hashlib.new("tiger"),
    "gost": hashlib.new("gost"),
    "blake2b": hashlib.new("blake2b"),
    "blake2s": hashlib.new("blake2s"),
    "sha3_224": hashlib.sha3_224,
    "sha3_256": hashlib.sha3_256,
    "sha3_384": hashlib.sha3_256,
    "sha3_512": hashlib.sha3_512,
    "shake_128": hashlib.shake_128,
    "shake_256": hashlib.shake_256,
}

chars = string.ascii_lowercase + string.digits

for name, func in hashes.items():
    for length in range(1, 9):
        for combo in itertools.product(chars, repeat=length):
            word = "".join(combo)
            h = func(word.encode())
            if name.startswith("shake"):
                digest = h.digest(32).hex()
            else:
                digest = h.hexdigest()
            if digest == hash_hex:
                print(f"flag{{{word}}}")
                raise SystemExit
