import re

with open("encrypted", "rb") as f:
    encoded = b"".join(f.read().split())

ciphertext = bytes.fromhex(encoded.decode("ascii"))
pad = b"A quart jar of oil mixed with zinc oxide makes a very bright paint"
plaintext = bytes(c ^ k for c, k in zip(ciphertext, pad))

match = re.match(rb"flag\{[A-Za-z0-9_]+\}", plaintext)
if match is None:
    raise RuntimeError("flag was not recovered")

flag = match.group(0)
tail_start = len(flag) + 1
if (plaintext[len(flag):tail_start] != b"|" or
        plaintext[tail_start:] != pad[:len(plaintext) - tail_start]):
    raise RuntimeError("decryption consistency check failed")

print(flag.decode("ascii"))
