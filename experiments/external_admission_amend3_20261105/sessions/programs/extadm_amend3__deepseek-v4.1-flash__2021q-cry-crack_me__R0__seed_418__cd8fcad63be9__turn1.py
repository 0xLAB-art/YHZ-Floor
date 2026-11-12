import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

alphanum = string.ascii_letters + string.digits

def try_password(password):
    for method in ["md5", "sha1", "sha256", "sha512", "sha224", "sha384", "sha512_224", "sha512_256", "blake2b", "blake2s", "ripemd160", "whirlpool", "shake_128", "shake_256", "md5_sha1", "sm3", "md4", "md2", "ripemd128", "ripemd160", "tiger", "gost", "sha3_224", "sha3_256", "sha3_384", "sha3_512", "keccak_224", "keccak_256", "keccak_384", "keccak_512", "shake128", "shake256"]:
        try:
            if method in ("shake_128", "shake_256", "shake128", "shake256"):
                h = hashlib.new(method, password.encode()).hexdigest()
            else:
                h = hashlib.new(method, password.encode()).hexdigest()
            if h.lower() == hash_hex.lower():
                return method, password
        except Exception:
            pass
    return None

for length in range(1, 9):
    for combo in itertools.product(alphanum, repeat=length):
        pwd = "".join(combo)
        result = try_password(pwd)
        if result:
            method, password = result
            print(f"flag{{{password}}}")
            break
    else:
        continue
    break
