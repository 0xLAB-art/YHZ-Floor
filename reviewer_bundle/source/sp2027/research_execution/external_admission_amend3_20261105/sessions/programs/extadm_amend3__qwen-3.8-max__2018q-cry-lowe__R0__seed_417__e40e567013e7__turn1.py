import base64
import math

with open("pubkey.pem") as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith("-----")]
keydata = b"".join(base64.b64decode(l) for l in lines)

n = int.from_bytes(keydata, "big")
e = 3

with open("key.enc") as f:
    y = int(f.read().strip())

with open("file.enc") as f:
    c = base64.b64decode(f.read().strip())

k = round(y ** (1 / 3))
while k ** 3 < y:
    k += 1
while k ** 3 > y:
    k -= 1
assert k ** 3 == y

y_bytes = k.to_bytes((y.bit_length() + 7) // 8, "big")
flag = bytes(a ^ b for a, b in zip(c, y_bytes))
print(flag.decode())