import base64


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[pos:pos + count], 'big')
        pos += count
    end = pos + length
    if end > len(data):
        raise ValueError('Truncated DER')
    return tag, data[pos:end], end


def cube_root(value):
    lo = 0
    hi = 1 << ((value.bit_length() + 2) // 3)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid ** 3 <= value:
            lo = mid
        else:
            hi = mid
    return lo


with open('pubkey.pem', 'rb') as f:
    pem = f.read()
der = base64.b64decode(b''.join(
    line.strip() for line in pem.splitlines()
    if not line.startswith(b'-----')
))
_, spki, _ = read_tlv(der)
_, _, pos = read_tlv(spki)
_, bit_string, _ = read_tlv(spki, pos)
assert bit_string[0] == 0
_, rsa_key, _ = read_tlv(bit_string[1:])
_, modulus_bytes, pos = read_tlv(rsa_key)
_, exponent_bytes, _ = read_tlv(rsa_key, pos)
n = int.from_bytes(modulus_bytes, 'big')
e = int.from_bytes(exponent_bytes, 'big')
assert e == 3

with open('key.enc', 'r') as f:
    y = int(f.read().strip())
with open('file.enc', 'rb') as f:
    ciphertext = base64.b64decode(f.read())

k = cube_root(n + y)
assert k ** 3 == n + y
assert pow(k, e, n) == y
assert len(ciphertext) == 64
key = k.to_bytes(64, 'big')
plaintext = bytes(c ^ b for c, b in zip(ciphertext, key))
print(plaintext.decode('utf-8'))
