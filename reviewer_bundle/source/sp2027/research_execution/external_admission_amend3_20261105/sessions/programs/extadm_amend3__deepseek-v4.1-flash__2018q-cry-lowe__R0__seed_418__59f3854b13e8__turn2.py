import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if l.strip() and '-----' not in l]
mod_b64 = ''.join(lines)
N = int.from_bytes(base64.b64decode(mod_b64), 'big')

with open('key.enc') as f:
    Y = int(f.read().strip(), 10)

with open('file.enc') as f:
    C_b64 = f.read().strip()
C = base64.b64decode(C_b64)

K = round((Y + N) ** (1 / 3))
while K ** 3 < Y + N:
    K += 1
while (K - 1) ** 3 >= Y + N:
    K -= 1
assert K ** 3 == Y + N

Y_bytes = K.to_bytes((Y.bit_length() + 7) // 8, 'big')
if len(Y_bytes) < len(C):
    Y_bytes = b'\x00' * (len(C) - len(Y_bytes)) + Y_bytes

S = bytes(a ^ b for a, b in zip(Y_bytes, C))
print(S.decode('utf-8', errors='replace'))
