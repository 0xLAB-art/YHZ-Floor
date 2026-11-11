import base64
import hashlib
import json

with open("README.md", "rb") as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
except Exception:
    decoded = raw

text = decoded.decode("utf-8", errors="replace")

hash_line = None
salt_line = None
for line in text.splitlines():
    line = line.strip()
    if line.startswith("Your hash:"):
        hash_line = line
    elif line.startswith("Your salt:"):
        salt_line = line

assert hash_line is not None, "hash line not found"
assert salt_line is not None, "salt line not found"

hash_value = hash_line.split(":", 1)[1].strip()
salt_desc = salt_line.split(":", 1)[1].strip()

hashes = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
    "sha224": hashlib.sha224,
    "sha384": hashlib.sha384,
    "sha3_224": lambda x: hashlib.sha3_224(x),
    "sha3_256": lambda x: hashlib.sha3_256(x),
    "sha3_384": lambda x: hashlib.sha3_384(x),
    "sha3_512": lambda x: hashlib.sha3_512(x),
    "blake2b": lambda x: hashlib.blake2b(x),
    "blake2s": lambda x: hashlib.blake2s(x),
    "ripemd128": lambda x: hashlib.new("ripemd128", x),
    "ripemd160": lambda x: hashlib.new("ripemd160", x),
    "ripemd256": lambda x: hashlib.new("ripemd256", x),
    "ripemd320": lambda x: hashlib.new("ripemd320", x),
    "whirlpool": lambda x: hashlib.new("whirlpool", x),
    "shake_128": lambda x: hashlib.shake_128(x).digest(32),
    "shake_256": lambda x: hashlib.shake_256(x).digest(32),
}

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

for name, func in hashes.items():
    for length in range(1, 9):
        for combo in __import__("itertools").product(chars, repeat=length):
            candidate = "".join(combo)
            try:
                h = func(candidate.encode("utf-8")).hexdigest()
            except Exception:
                continue
            if h == hash_value:
                print(f"flag{{{candidate}}}")
                raise SystemExit(0)

print("not found")
