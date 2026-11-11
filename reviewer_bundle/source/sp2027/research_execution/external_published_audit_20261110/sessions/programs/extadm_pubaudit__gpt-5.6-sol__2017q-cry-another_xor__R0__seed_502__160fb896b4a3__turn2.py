import re

with open("encrypted", "r", encoding="ascii") as f:
    ciphertext = bytes.fromhex(f.read().strip())

crib = b"A quart jar of oil mixed with zinc oxide makes a very bright paint."
recovered = bytes(c ^ p for c, p in zip(ciphertext, crib))
match = re.match(rb"flag[{][A-Za-z0-9_]+[}]", recovered)
if match is None:
    raise RuntimeError("flag not recovered")
print(match.group(0).decode("ascii"))
