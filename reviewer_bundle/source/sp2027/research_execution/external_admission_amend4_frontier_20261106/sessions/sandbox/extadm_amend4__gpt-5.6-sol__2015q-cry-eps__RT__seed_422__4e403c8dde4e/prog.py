import sys

filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    data = f.read()

bits = bytes(b for b in data if b in (48, 49))
if len(bits) % 8 != 0:
    raise ValueError("Binary data length is not divisible by 8")

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
sys.stdout.write(plaintext.rstrip("\r\n") + "\n")
