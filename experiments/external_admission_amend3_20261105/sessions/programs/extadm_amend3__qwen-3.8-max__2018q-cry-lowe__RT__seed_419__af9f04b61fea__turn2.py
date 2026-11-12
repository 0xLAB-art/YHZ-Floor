import base64

with open('pubkey.pem', 'rb') as f:
    pem = f.read()
lines = [l for l in pem.split(b'\n') if l and not l.startswith(b'-----')]
der = base64.b64decode(b''.join(lines))
# SubjectPublicKeyInfo: SEQUENCE { SEQUENCE { OID, NULL }, BIT STRING }
assert der[:1] == b'\x30'
_, rest = _decode_seq(der)
_, rest = _decode_seq(rest)  # algorithm
_, rest = _decode_bitstring(rest)
der = rest

N, der = _decode_int(der)
e, der = _decode_int(der)

with open('key.enc', 'rb') as f:
    y = int(f.read().strip())
with open('file.enc', 'rb') as f:
    c = base64.b64decode(f.read().strip())

# Y + N is a perfect cube: K^3 = Y + N
val = y + N
K = int(round(val ** (1/3)))
while K**3 < val:
    K += 1
while K**3 > val:
    K -= 1
assert K**3 == val, 'cube root failed'

Y = K.to_bytes((Y.bit_length() + 7) // 8, 'big')
key = bytes(a ^ b for a, b in zip(Y, c))
print(key.decode('utf-8', errors='replace'))

def _decode_seq(data):
    assert data[0] == 0x30
    length, rest = _decode_length(data[1:])
    return data[1:1+length], rest[length:]

def _decode_length(data):
    b = data[0]
    if b < 0x80:
        return b, data[1:]
    n = b & 0x7f
    return int.from_bytes(data[1:1+n], 'big'), data[1+n:]

def _decode_int(data):
    assert data[0] == 0x02
    length, rest = _decode_length(data[1:])
    return int.from_bytes(rest[:length], 'big'), rest[length:]

def _decode_bitstring(data):
    assert data[0] == 0x03
    length, rest = _decode_length(data[1:])
    return rest[1:length], rest[length:]
