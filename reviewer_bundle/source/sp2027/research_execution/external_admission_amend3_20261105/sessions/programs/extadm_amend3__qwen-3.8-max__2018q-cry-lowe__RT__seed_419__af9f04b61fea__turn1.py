import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and not l.startswith('-----')]
mod_b64 = ''.join(lines)
N = int(mod_b64, 16)

with open('key.enc') as f:
    y_b64 = f.read().strip()
Y = int.from_bytes(base64.b64decode(y_b64), 'big')

with open('file.enc') as f:
    c_b64 = f.read().strip()
C = base64.b64decode(c_b64)

K = round((Y + N) ** (1/3))
while K**3 < Y + N:
    K += 1
while K**3 > Y + N:
    K -= 1
assert K**3 == Y + N

S = (Y % N).to_bytes(192, 'big')
S = S[:64]
flag = bytes(a ^ b for a, b in zip(S, C))
print(flag.decode())
