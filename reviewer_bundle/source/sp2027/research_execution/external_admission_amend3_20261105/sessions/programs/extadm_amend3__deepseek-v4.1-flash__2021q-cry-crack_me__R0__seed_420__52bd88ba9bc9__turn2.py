import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

# Try common hash algorithms with lowercase letters as candidates
algorithms = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "sha512_224", "sha512_256",
    "ripemd128", "ripemd160", "whirlpool", "tiger", "md4",
]

def try_password(password, alg):
    try:
        h = hashlib.new(alg)
        h.update(password.encode())
        return h.hexdigest().lower() == hash_hex.lower()
    except (ValueError, AttributeError):
        return False

# First try single lowercase words
for alg in algorithms:
    for length in range(1, 9):
        for combo in itertools.product(string.ascii_lowercase, repeat=length):
            pw = "".join(combo)
            if try_password(pw, alg):
                print(f"flag{{{pw}}}")
                raise SystemExit

# If not found, try uppercase too
for alg in algorithms:
    for length in range(1, 9):
        for combo in itertools.product(string.ascii_lowercase + string.ascii_uppercase, repeat=length):
            pw = "".join(combo)
            if try_password(pw, alg):
                print(f"flag{{{pw}}}")
                raise SystemExit
