import re

filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    bits = re.sub(rb"[^01]", b"", f.read())

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("ascii")
flag = re.search(r"flag\{[^}]*\}", plaintext)
if flag is None:
    raise ValueError("No flag found")
print(flag.group(0))
