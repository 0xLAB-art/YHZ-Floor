import base64
import math

with open('pubkey.pem', 'rb') as f:
    pem = f.read()
lines = [l for l in pem.split(b'\n') if l and not l.startswith(b'-----')]
mod_b64 = b''.join(lines)
N = int(base64.b64decode(mod_b64).hex(), 16)

with open('key.enc', 'rb') as f:
    Y = int.from_bytes(base64.b64decode(f.read()), 'big')

with open('file.enc', 'rb') as f:
    C = base64.b64decode(f.read())

K = round((Y + N) ** (1 / 3))
while K ** 3 < Y + N:
    K += 1
while K ** 3 > Y + N:
    K -= 1
assert K ** 3 == Y + N

Y_bytes = K.to_bytes((Y.bit_length() + 7) // 8, 'big')
flag = bytes(a ^ b for a, b in zip(C, Y_bytes))
print(flag.decode())