import re

data = open("encrypted", "rb").read().strip()
assert all(c in b"0123456789abcdefABCDEF" for c in data)

hex_str = data.decode("ascii")
bytes_data = bytes.fromhex(hex_str)

# The ciphertext is a sequence of length-prefixed records.
# Each record: [len_byte][payload...]
# The payload is a length-prefixed string: [len_byte][chars...]

records = []
i = 0
while i < len(bytes_data):
    length = bytes_data[i]
    i += 1
    records.append(bytes_data[i : i + length])
    i += length

flag = ""
for rec in records:
    if len(rec) == 0:
        continue
    s_len = rec[0]
    s_bytes = rec[1 : 1 + s_len]
    s = s_bytes.decode("ascii", errors="replace")
    flag += s

print(flag)
