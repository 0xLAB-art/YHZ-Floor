import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

# Try common hash algorithms with lowercase letters as candidate plaintext
algorithms = [
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
    "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "blake2b", "blake2s", "ripemd128", "ripemd160", "whirlpool",
    "shake_128", "shake_256",
]

def try_plain(plain):
    for algo in algorithms:
        try:
            h = hashlib.new(algo)
            h.update(plain.encode())
            if h.hexdigest().lower() == hash_hex:
                return algo
        except (ValueError, AttributeError):
            pass
    return None

# Try single lowercase letters first
for c in string.ascii_lowercase:
    algo = try_plain(c)
    if algo:
        print(f"flag{{{c}}}")
        break
else:
    # Try two-letter combinations
    found = False
    for combo in itertools.product(string.ascii_lowercase, repeat=2):
        plain = "".join(combo)
        algo = try_plain(plain)
        if algo:
            print(f"flag{{{plain}}}")
            found = True
            break
    if not found:
        # Try three-letter combinations
        for combo in itertools.product(string.ascii_lowercase, repeat=3):
            plain = "".join(combo)
            algo = try_plain(plain)
            if algo:
                print(f"flag{{{plain}}}")
                break
