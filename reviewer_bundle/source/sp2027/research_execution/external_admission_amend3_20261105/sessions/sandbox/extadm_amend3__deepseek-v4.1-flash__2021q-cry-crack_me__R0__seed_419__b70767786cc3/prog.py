import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

# Try common hash algorithms with lowercase word candidates
algorithms = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "ripemd128", "ripemd160", "whirlpool",
    "shake_128", "shake_256",
]

# Try lowercase words first, then simple patterns
words = list(string.ascii_lowercase)
words += [w + c for w in string.ascii_lowercase for c in string.ascii_lowercase]
words += [w + str(i) for w in string.ascii_lowercase for i in range(10)]
words += [str(i) for i in range(100)]

for algo in algorithms:
    for word in words:
        try:
            h = hashlib.new(algo)
            h.update(word.encode())
            digest = h.hexdigest()
            if digest.lower() == hash_hex.lower():
                print(f"flag{{{word}}}")
                raise SystemExit
        except Exception:
            pass

# Try uppercase and mixed
for algo in algorithms:
    for word in [w.upper() for w in words]:
        try:
            h = hashlib.new(algo)
            h.update(word.encode())
            digest = h.hexdigest()
            if digest.lower() == hash_hex.lower():
                print(f"flag{{{word}}}")
                raise SystemExit
        except Exception:
            pass
