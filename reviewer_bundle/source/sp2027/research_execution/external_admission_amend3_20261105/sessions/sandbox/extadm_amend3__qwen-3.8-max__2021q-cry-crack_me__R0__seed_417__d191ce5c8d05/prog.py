import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

# Try common hash algorithms with lowercase alphanumeric passwords
algorithms = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "ripemd128", "ripemd160", "whirlpool", "tiger128", "tiger160", "tiger192",
    "md4", "md5_sha1", "shake_128", "shake_256",
]

def try_password(password):
    for algo in algorithms:
        try:
            h = hashlib.new(algo)
            h.update(password.encode())
            if h.hexdigest().lower() == hash_hex:
                return algo
        except (ValueError, AttributeError):
            pass
    return None

# First, try short lowercase alphanumeric passwords
chars = string.ascii_lowercase + string.digits
for length in range(1, 9):
    for combo in itertools.product(chars, repeat=length):
        password = "".join(combo)
        algo = try_password(password)
        if algo:
            print(f"flag{{{password}}}")
            raise SystemExit

# If not found, try with uppercase and mixed
chars_mixed = string.ascii_letters + string.digits
for length in range(1, 9):
    for combo in itertools.product(chars_mixed, repeat=length):
        password = "".join(combo)
        algo = try_password(password)
        if algo:
            print(f"flag{{{password}}}")
            raise SystemExit
