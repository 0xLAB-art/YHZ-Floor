import base64
import re

filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
raw = open(filename, "rb").read()
bits = re.sub(rb"\s+", b"", raw)

if re.fullmatch(rb"[01]+", bits) is None:
    bits = re.sub(rb"\s+", b"", base64.b64decode(raw))

plaintext = bytes(
    int(bits[i:i + 8], 2)
    for i in range(0, len(bits) - 7, 8)
).decode("utf-8")

flag = re.search(r"flag\{[^}]+\}", plaintext)
if flag is None:
    raise ValueError("No flag found")
print(flag.group(0))
