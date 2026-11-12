import re

filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    bits = re.sub(rb"[^01]", b"", f.read())

if not bits or len(bits) % 8:
    raise ValueError("Invalid binary data")

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
flag = re.search(r"flag\{[^{}]*\}", plaintext)
if flag is None:
    raise ValueError("Flag not found")

print(flag.group(0))