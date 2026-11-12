filename = "eps1.1_ones-and-zer0es_c4368e65e1883044f3917485ec928173.mpeg"
with open(filename, "rb") as f:
    bits = b"".join(f.read().split())

if not bits or len(bits) % 8 != 0 or any(bit not in b"01" for bit in bits):
    raise ValueError("Artifact is not a valid binary-encoded byte stream")

plaintext = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)).decode("utf-8")
print(plaintext)
