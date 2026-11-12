import re

with open("ciphertext") as f:
    ct = "".join(f.read().split())

n = 4
block = 8

# Recover key by brute force over all 4-bit nibbles
for key in range(256):
    key_bytes = [key >> 4, key & 0xf]
    key_hex = "".join(f"{b:02x}" for b in key_bytes)
    m = ""
    for i in range(0, len(ct), 16):
        chunk = ct[i:i+16]
        c_vals = [int(chunk[j:j+2], 16) for j in range(0, 16, 2)]
        for b in range(8):
            k = key_bytes[b % 2]
            m += chr((c_vals[b] - k) & 0xf)
    try:
        flag = bytes.fromhex(m).decode("utf-8")
        if flag.startswith("flag"):
            print(flag)
            break
    except Exception:
        pass
