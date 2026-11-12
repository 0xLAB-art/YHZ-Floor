import base64
import math

with open('pubkey.pem', 'rb') as f:
    pem = f.read()
lines = [l for l in pem.split(b'\n') if l and not l.startswith(b'-----')]
der = base64.b64decode(b''.join(lines))
from binascii import unhexlify
der = unhexlify(der)

i = 0
def read_len():
    global i
    b = der[i]
    i += 1
    if b < 0x80:
        return b
    n = b & 0x7f
    return int.from_bytes(der[i:i+n], 'big'), i + n

def read_elem():
    global i
    tag = der[i]; i += 1
    length, i = read_len()
    return tag, der[i:i+length], i

# Sequence
read_elem()
# RSAPublicKey sequence
read_elem()
# modulus
tag, mod, i = read_elem()
# exponent
tag, exp, i = read_elem()
N = int.from_bytes(mod, 'big')
e = int.from_bytes(exp, 'big')

with open('key.enc', 'rb') as f:
    y = int(f.read().strip())
with open('file.enc', 'rb') as f:
    C = base64.b64decode(f.read().strip())

# Y + N is a perfect cube: K^3 = Y + N
val = y + N
K = round(val ** (1/3))
while K**3 < val:
    K += 1
while K**3 > val:
    K -= 1
assert K**3 == val, 'cube root failed'

Y = K.to_bytes((y.bit_length() + 7) // 8, 'big')
Y = Y.rjust(192, b'\x00')

S = bytes(a ^ b for a, b in zip(Y, C))
print(S.decode('utf-8', errors='replace'))
