import base64


def read_tlv(data, offset=0):
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        width = length & 0x7f
        assert width > 0
        length = int.from_bytes(data[offset:offset + width], 'big')
        offset += width
    end = offset + length
    assert end <= len(data)
    return tag, data[offset:end], end


def integer_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while high - low > 1:
        middle = (low + high) // 2
        if middle ** 3 <= value:
            low = middle
        else:
            high = middle
    return low


with open('pubkey.pem', 'rb') as f:
    pem = f.read()
der = base64.b64decode(b''.join(
    line.strip() for line in pem.splitlines()
    if not line.startswith(b'-----')
))

tag, outer, _ = read_tlv(der)
assert tag == 0x30
_, _, position = read_tlv(outer)
tag, bit_string, _ = read_tlv(outer, position)
assert tag == 0x03 and bit_string[0] == 0

tag, rsa, _ = read_tlv(bit_string, 1)
assert tag == 0x30
tag, modulus, position = read_tlv(rsa)
assert tag == 0x02
N = int.from_bytes(modulus, 'big')
tag, exponent, _ = read_tlv(rsa, position)
assert tag == 0x02 and int.from_bytes(exponent, 'big') == 3

with open('key.enc', 'r', encoding='ascii') as f:
    Y = int(f.read().strip())
with open('file.enc', 'rb') as f:
    ciphertext = base64.b64decode(f.read())

K = integer_cube_root(Y + N)
assert K ** 3 == Y + N
assert len(ciphertext) == 64
key = K.to_bytes(64, 'big')
plaintext = bytes(c ^ k for c, k in zip(ciphertext, key))
print(plaintext.decode('utf-8'))
