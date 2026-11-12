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
    C = base64.b64decode(f.read().strip())

K = round((Y + N) ** (1/3))
while K**3 < Y + N:
    K += 1
while K**3 > Y + N:
    K -= 1
assert K**3 == Y + N

Y_bytes = Y.to_bytes((Y.bit_length() + 7) // 8, 'big')
S = bytes(a ^ b for a, b in zip(C, Y_bytes))
print(S.decode('utf-8', errors='replace'))