import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

hashes = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
    "sha224": hashlib.sha224,
    "sha384": hashlib.sha384,
    "sha3_224": hashlib.sha3_224,
    "sha3_256": hashlib.sha3_256,
    "sha3_384": hashlib.sha3_512,
    "sha3_512": hashlib.sha3_512,
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
    "ripemd128": None,
    "ripemd160": None,
    "whirlpool": None,
    "tiger": None,
    "shake_128": hashlib.shake_128,
    "shake_256": hashlib.shake_256,
}

chars = string.ascii_letters + string.digits

def check(name, h, candidate):
    try:
        if name in ("shake_128", "shake_256"):
            digest = h(candidate.encode()).hexdigest()[:64]
        else:
            digest = h(candidate.encode()).hexdigest()
        return digest == hash_hex
    except Exception:
        return False

for name, h in hashes.items():
    if h is None:
        continue
    for length in range(1, 9):
        for combo in itertools.product(chars, repeat=length):
            cand = "".join(combo)
            if check(name, h, cand):
                print(f"flag{{{cand}}}")
                raise SystemExit
    print(f"flag{{{name}}}")
    raise SystemExit