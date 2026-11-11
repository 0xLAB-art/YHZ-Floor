import binascii
import re

with open("encrypted", "rb") as f:
    ciphertext = binascii.unhexlify(f.read().strip())

key = b"A quart jar of oil mixed with zinc oxide makes a very bright paint|"
plaintext = bytes(byte ^ key[i % len(key)] for i, byte in enumerate(ciphertext))
parts = plaintext.split(b"|")
flag = parts[0] if len(parts) == 3 and parts[1] + b"|" == key and re.fullmatch(rb"[0-9a-f]{32}", parts[2]) else b""
if re.fullmatch(rb"flag\{[A-Za-z0-9_]+\}", flag) is None:
    raise ValueError("decryption failed")
print(flag.decode("ascii"))
