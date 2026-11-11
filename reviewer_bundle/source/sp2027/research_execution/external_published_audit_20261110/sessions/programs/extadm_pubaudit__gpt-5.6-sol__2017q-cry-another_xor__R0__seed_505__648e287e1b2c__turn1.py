import binascii
import re

with open("encrypted", "rb") as f:
    encoded = b"".join(f.read().split())

ciphertext = binascii.unhexlify(encoded)
crib = b"A quart jar of oil mixed with zinc oxide makes a very bright paint."
recovered = bytes(c ^ p for c, p in zip(ciphertext, crib))
match = re.match(rb"flag\{[A-Za-z0-9_]+\}", recovered)
if match is None:
    raise RuntimeError("flag not recovered")
print(match.group().decode("ascii"))