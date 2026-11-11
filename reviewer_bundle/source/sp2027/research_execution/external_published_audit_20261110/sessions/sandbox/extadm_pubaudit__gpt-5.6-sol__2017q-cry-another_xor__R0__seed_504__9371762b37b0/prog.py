import re

with open("encrypted", "r", encoding="ascii") as f:
    ciphertext = bytes.fromhex(f.read())

key = b"A quart jar of oil mixed with zinc oxide makes a very bright paint."
plaintext = bytes(byte ^ key[i % len(key)] for i, byte in enumerate(ciphertext))

match = re.search(rb"flag\{[^}\r\n]+\}", plaintext)
if match is None:
    raise RuntimeError("flag not found")
print(match.group().decode("ascii"))