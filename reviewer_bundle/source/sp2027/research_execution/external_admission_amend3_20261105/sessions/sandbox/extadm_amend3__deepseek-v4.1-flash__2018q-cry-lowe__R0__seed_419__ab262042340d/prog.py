import base64
import math

with open('pubkey.pem') as f:
    pem = f.read()
lines = [l for l in pem.splitlines() if not l.startswith('-----')]
der = base64.b64decode(''.join(lines))

def read_int(b, off):
    (n,) = struct.unpack('>I', b[off:off+4])
    off += 4
    if n == 0:
        return 0, off
    (v,) = struct.unpack('>I', b[off:off+4])
    off += 4
    return (1 << 24) | v, off

off = 0
tag, off = read_int(der, off)
assert tag == 0x30
n_len, off = read_int(der, off)
modulus, off = read_int(der, off)
assert modulus == n_len
e, off = read_int(der, off)
assert e == 3
N = modulus

def i2osp(x, n):
    r = bytearray()
    while n:
        r.append(x & 0xff)
        x >>= 8
        n -= 1
    return bytes(reversed(r))

with open('key.enc') as f:
    Y = int(f.read().strip())
with open('file.enc') as f:
    C = base64.b64decode(f.read().strip())

Y_bytes = i2osp(Y, 192)
S = bytes(a ^ b for a, b in zip(Y_bytes, C))
print(S.decode())
