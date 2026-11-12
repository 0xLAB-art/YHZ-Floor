import base64
import math

with open('pubkey.pem', 'rb') as f:
    pem = f.read()
lines = [l for l in pem.split(b'\n') if l and not l.startswith(b'-----')]
der = base64.b64decode(b''.join(lines))
# SubjectPublicKeyInfo: SEQUENCE { SEQUENCE { OID, NULL }, BIT STRING }
assert der[0] == 0x30
_, rest = _decode_seq(der, 1)
assert rest[0] == 0x30
_, pkalg = _decode_seq(rest, 1)
assert pkalg[:8] == b'\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01'
assert rest[2] == 0x03
_, bitstr = _decode_bitstring(rest, 3)
# RSAPublicKey: SEQUENCE { modulus, publicExponent }
assert bitstr[0] == 0x30
_, rsa = _decode_seq(bitstr, 1)
assert rsa[0] == 0x02
n, _ = _decode_int(rsa, 1)
assert rsa[1] == 0x02
e, _ = _decode_int(rsa, 2)
assert e == 3

with open('key.enc', 'rb') as f:
    y = int.from_bytes(base64.b64decode(f.read()), 'big')
with open('file.enc', 'rb') as f:
    c = base64.b64decode(f.read())

# Y + N is a perfect cube: K^3 = Y + N
root = round((y + n) ** (1/3))
while root**3 < y + n:
    root += 1
while root**3 > y + n:
    root -= 1
assert root**3 == y + n
k = root

# Y = K^e mod N, but K < (2N)^(1/3) so K^3 < 8N; Y = K^3 - mN for small m
# Actually Y = K^3 mod N, and K^3 = Y + N (m=1 per construction)
# Recover Y from K: Y = K^3 mod N
Y = pow(k, e, n)

key = Y.to_bytes((Y.bit_length() + 7) // 8, 'big')
flag = bytes(a ^ b for a, b in zip(c, key * ((len(c) // len(key)) + 1)))[:len(c)]
print(flag.decode('latin-1'))

def _decode_seq(data, pos):
    assert data[pos] == 0x30
    length = _decode_length(data, pos + 1)
    return length, pos + 1 + length

def _decode_length(data, pos):
    b = data[pos]
    if b < 0x80:
        return b, pos + 1
    n = b & 0x7f
    length = int.from_bytes(data[pos + 1:pos + 1 + n], 'big')
    return length, pos + 1 + n

def _decode_bitstring(data, pos):
    assert data[pos] == 0x03
    length, pos = _decode_length(data, pos + 1)
    return length, pos + length

def _decode_int(data, pos):
    assert data[pos] == 0x02
    length, pos = _decode_length(data, pos + 1)
    value = int.from_bytes(data[pos:pos + length], 'big')
    return value, pos + length