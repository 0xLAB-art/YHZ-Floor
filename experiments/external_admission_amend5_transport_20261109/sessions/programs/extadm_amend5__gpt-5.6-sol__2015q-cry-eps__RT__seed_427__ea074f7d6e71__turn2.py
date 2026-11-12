import re
import sys

filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    raw = f.read()

bits = re.sub(rb"\s+", b"", raw)
if not bits or re.fullmatch(rb"[01]+", bits) is None or len(bits) % 8 != 0:
    raise ValueError("Artifact is not a byte-aligned binary string")

plaintext = bytes(
    int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)
).decode("ascii")

match = re.search(r"flag\{[^{}\r\n]*\}", plaintext)
if match is None:
    raise ValueError("No flag found in decoded artifact")

sys.stdout.write(match.group(0) + "\n")
