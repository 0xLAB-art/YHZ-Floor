import base64


def read_tlv(data, offset=0):
    tag = data[offset]
    length = data[offset + 1]
    offset += 2
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + length
    return tag, data[offset:end], end


def cube_root(n):
    low = 0
    high = 1 << ((n.bit_length() + 2) // 3)
    while low + 1 < high:
        mid = (low + high) // 2
        if mid * mid * mid <= n:
            low = mid
        else:
            high = mid
    return low


with open('pubkey.pem', 'r', encoding='ascii') as f:
    pem = f.read()
der = base64.b64decode(''.join(
    line.strip() for line in pem.splitlines()
    if not line.startswith('-----')
))

_, spki, _ = read_tlv(der)
_, _, offset = read_tlv(spki)
tag, bit_string, _ = read_tlv(spki, offset)
assert tag == 3 and bit_string[0] == 0
_, rsa_key, _ = read_tlv(bit_string[1:])
_, modulus_bytes, offset = read_tlv(rsa_key)
_, exponent_bytes, _ = read_tlv(rsa_key, offset)
n = int.from_bytes(modulus_bytes, 'big')
e = int.from_bytes(exponent_bytes, 'big')
assert e == 3

with open('key.enc', 'r', encoding='ascii') as f:
    y = int(f.read().strip())

# The RSA reduction subtracted exactly one modulus.
target = y + n
k = cube_root(target)
assert k * k * k == target

with open('file.enc', 'rb') as f:
    ciphertext = base64.b64decode(f.read())
assert len(ciphertext) == 64
key = k.to_bytes(64, 'big')
plaintext = bytes(c ^ b for c, b in zip(ciphertext, key))
print(plaintext.decode('utf-8'))
