import base64
import math

with open("pubkey.pem", "rb") as f:
    pem = f.read()
lines = [l for l in pem.split(b"\n") if l and not l.startswith(b"-")]
der = base64.b64decode(b"".join(lines))
mod = int.from_bytes(der, "big")

with open("key.enc", "rb") as f:
    y = int.from_bytes(f.read(), "big")

with open("file.enc", "rb") as f:
    c = base64.b64decode(f.read())

k = round((y + mod) ** (1/3))
while k**3 < y + mod:
    k += 1
while k**3 > y + mod:
    k -= 1
assert k**3 == y + mod

y_bytes = k.to_bytes((y.bit_length() + 7) // 8, "big")
flag = bytes(a ^ b for a, b in zip(c, y_bytes))
print(flag.decode())
