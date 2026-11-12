import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

hash_algos = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "md4", "ripemd128", "ripemd160",
    "whirlpool", "tiger", "shake_128", "shake_256",
]

def try_hash(algo, candidate):
    try:
        h = hashlib.new(algo)
        h.update(candidate.encode())
        return h.hexdigest().lower() == hash_hex
    except (ValueError, AttributeError):
        return False

charset = string.ascii_lowercase + string.ascii_uppercase + string.digits

for length in range(1, 10):
    for combo in itertools.product(charset, repeat=length):
        candidate = "".join(combo)
        for algo in hash_algos:
            if try_hash(algo, candidate):
                print(f"flag{{{candidate}}}")
                raise SystemExit

print("flag{not_found}")