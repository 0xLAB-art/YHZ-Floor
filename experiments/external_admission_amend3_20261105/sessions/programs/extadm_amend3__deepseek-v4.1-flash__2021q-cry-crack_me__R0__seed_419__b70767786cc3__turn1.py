import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

alphanumeric = string.ascii_letters + string.digits

def try_password(password):
    for method in ["md5", "sha1", "sha256", "sha512", "sha224", "sha384", "sha3_256", "sha3_512", "sha3_224", "sha3_384", "blake2b", "blake2s", "ripemd128", "ripemd160", "whirlpool", "tiger", "md4", "md5-sha1", "gost", "gost-crypto", "sm3", "shake_128", "shake_256"]:
        try:
            h = hashlib.new(method)
            h.update(password.encode())
            if h.hexdigest().lower() == hash_hex:
                return method
        except (ValueError, AttributeError):
            pass
    return None

found = None
for length in range(1, 10):
    for combo in itertools.product(alphanumeric, repeat=length):
        pwd = "".join(combo)
        method = try_password(pwd)
        if method:
            found = (pwd, method)
            break
    if found:
        break

if found:
    password, method = found
    print(f"flag{{{password}}}")
else:
    print("flag{unknown}")
