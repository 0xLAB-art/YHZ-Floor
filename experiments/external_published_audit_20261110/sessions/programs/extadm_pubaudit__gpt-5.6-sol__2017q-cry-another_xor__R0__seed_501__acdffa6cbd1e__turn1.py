import re

with open("encrypted", "r", encoding="ascii") as f:
    ciphertext = bytes.fromhex(f.read())

key = b"A quart jar of oil mixed with zinc oxide makes a very bright paint|"
plaintext = bytes(byte ^ key[i % len(key)] for i, byte in enumerate(ciphertext))
parts = plaintext.split(b"|")

if (len(parts) != 3 or parts[1] != key[:-1] or
        re.fullmatch(rb"[0-9a-f]{32}", parts[2]) is None or
        re.fullmatch(rb"flag\{[^}]+\}", parts[0]) is None):
    raise ValueError("decryption failed")

print(parts[0].decode("ascii"))
