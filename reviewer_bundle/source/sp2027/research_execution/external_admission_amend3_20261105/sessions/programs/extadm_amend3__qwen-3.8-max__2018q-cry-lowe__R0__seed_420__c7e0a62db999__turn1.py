import base64
import json
import math

with open("pubkey.pem") as f:
    pem = f.read()
lines = pem.strip().split("\n")
der = "".join(lines[1:-1])
N = int.from_bytes(base64.b64decode(der), "big")

with open("key.enc") as f:
    Y = int(f.read().strip())

with open("file.enc") as f:
    C = base64.b64decode(f.read().strip())

K = round(Y ** (1/3))
while K**3 < Y:
    K += 1
while K**3 > Y:
    K -= 1
assert K**3 == Y

Y_bytes = K.to_bytes(192, "big")
S = bytes(a ^ b for a, b in zip(Y_bytes, C))
print(S.decode())
