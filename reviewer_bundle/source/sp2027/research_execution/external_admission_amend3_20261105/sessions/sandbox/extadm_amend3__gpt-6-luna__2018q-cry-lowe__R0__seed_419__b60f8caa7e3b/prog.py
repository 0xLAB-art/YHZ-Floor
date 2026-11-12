import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if not l.startswith('-----')]
modulus = int(''.join(lines), 16)

def integer_nth_root(n, k):
    if n < 0:
        raise ValueError('negative')
    if n == 0:
        return 0
    x = 1 << ((n.bit_length() + k - 1) // k)
    while True:
        y = (k - 1) * x + n // x**(k - 1)
        y //= k
        if y >= x:
            return x
        x = y

with open('key.enc') as f:
    Y = int(f.read().strip())
with open('file.enc') as f:
    C = base64.b64decode(f.read().strip())

K = integer_nth_root(Y + modulus, 3)
Y_bytes = K.to_bytes(192, 'big')
flag = bytes(a ^ b for a, b in zip(Y_bytes, C))
print(flag.decode())
