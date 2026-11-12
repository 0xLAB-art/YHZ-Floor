import re

filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "r", encoding="ascii") as f:
    raw = f.read()

bits = "".join(re.findall(r"[01]", raw))
if len(bits) % 8 != 0:
    raise ValueError("Bitstream length is not byte-aligned")

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
match = re.search(r"flag\{[^}\r\n]*\}", plaintext)
if match is None:
    raise ValueError("No flag found in decrypted data")

print(match.group(0))
