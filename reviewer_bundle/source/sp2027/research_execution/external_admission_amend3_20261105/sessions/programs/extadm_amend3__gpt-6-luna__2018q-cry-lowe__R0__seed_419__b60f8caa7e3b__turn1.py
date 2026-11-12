import base64
import math

with open("pubkey.pem") as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith("-----")]
keydata = b"".join(base64.b64decode(l) for l in lines)
N = int.from_bytes(keydata, "big")

e = 3
Y = int(open("key.enc").read().strip())
C = base64.b64decode(open("file.enc").read().strip())

# Y + N is a perfect cube: K^3 = Y + N
val = Y + N
K = round(val ** (1/3))
while K**3 < val:
    K += 1
while K**3 > val:
    K -= 1
assert K**3 == val, "cube root failed"

Y_bytes = K.to_bytes(192, "big")
flag = bytes(a ^ b for a, b in zip(Y_bytes, C))
print(flag.decode())
