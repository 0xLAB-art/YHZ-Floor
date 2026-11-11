import re

filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
data = open(filename, "rb").read()
bits = "".join(chr(b) for b in data if b in (48, 49))
plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("ascii")
match = re.search(r"flag\{[^}]*\}", plaintext)
if match is None:
    raise ValueError("flag not found")
print(match.group(0))
