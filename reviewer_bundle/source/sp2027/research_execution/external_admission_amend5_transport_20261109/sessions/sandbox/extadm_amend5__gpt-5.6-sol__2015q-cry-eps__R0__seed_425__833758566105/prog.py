import re

filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    data = f.read()

bits = re.sub(rb"\s+", b"", data)
if not bits or len(bits) % 8 != 0 or re.search(rb"[^01]", bits):
    raise ValueError("Invalid binary data")

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
flags = re.findall(r"flag\{[^{}]*\}", plaintext)
if len(flags) != 1:
    raise ValueError("Expected exactly one flag")

print(flags[0])