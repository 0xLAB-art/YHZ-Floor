import sys

data = open("encrypted", "rb").read().strip()
buf = bytes.fromhex(data.decode())

# The ciphertext is a sequence of length-prefixed records.
# Each record: [len_byte][payload]
records = []
i = 0
while i < len(buf):
    length = buf[i]
    i += 1
    if i + length > len(buf):
        break
    records.append(buf[i:i+length])
    i += length

flag = ""
for rec in records:
    # XOR each byte with the record index (0-based) to recover plaintext
    plain = bytes(b ^ (idx % 256) for idx, b in enumerate(rec))
    flag += plain.decode("latin-1")

print(flag)
