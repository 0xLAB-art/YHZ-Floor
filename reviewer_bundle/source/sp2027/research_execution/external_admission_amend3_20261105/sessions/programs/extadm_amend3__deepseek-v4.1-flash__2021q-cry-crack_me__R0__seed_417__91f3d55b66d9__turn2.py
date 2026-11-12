import hashlib
import string
import itertools

hash_hex = "a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c"

# Try common short passwords with the hash algorithm as salt
algorithms = [
    "md5", "sha1", "sha256", "sha512", "sha224", "sha384",
    "blake2b", "blake2s", "ripemd128", "ripemd160", "whirlpool", "tiger",
    "md4", "md5-sha1", "sha3_224", "sha3_256", "sha3_384", "sha3_512",
    "shake_128", "shake_256", "sm3", "gost", "sm4", "des", "des3", "cast5",
    "blowfish", "aes", "rc4", "arc4", "ecb", "cbc", "cfb", "ofb", "ctr",
    "base64", "hex", "rot13", "utf8", "utf-8", "ascii", "latin1",
    "plain", "text", "string", "password", "secret", "key", "token",
    "flag", "ctf", "challenge", "crackme", "crack",
]

# Try salt = algorithm name, password = short words
chars = string.ascii_lowercase + string.digits
found = None

for algo in algorithms:
    for length in range(1, 6):
        for combo in itertools.product(chars, repeat=length):
            pwd = "".join(combo)
            h = hashlib.new(algo)
            h.update(pwd.encode())
            if h.hexdigest() == hash_hex:
                found = pwd
                break
        if found:
            break
    if found:
        break

if found:
    print(f"flag{{{found}}}")
else:
    print("flag{}")
