import base64


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 128:
        count = length & 127
        length = int.from_bytes(data[pos:pos + count], 'big')
        pos += count
    end = pos + length
    return tag, data[pos:end], end


def cube_root(value):
    lo = 0
    hi = 1 << ((value.bit_length() + 2) // 3)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** 3 <= value:
            lo = mid
        else:
            hi = mid
    return lo


with open('pubkey.pem', 'rb') as f:
    pem = f.read()
body = b''.join(line.strip() for line in pem.splitlines()
                if not line.startswith(b'-----'))
der = base64.b64decode(body, validate=True)

_, spki, _ = read_tlv(der)
_, _, pos = read_tlv(spki)
tag, bits, _ = read_tlv(spki, pos)
if tag != 3 or bits[0] != 0:
    raise ValueError('Invalid public key')
_, rsa, _ = read_tlv(bits[1:])
_, modulus_bytes, pos = read_tlv(rsa)
_, exponent_bytes, _ = read_tlv(rsa, pos)
n = int.from_bytes(modulus_bytes, 'big')
e = int.from_bytes(exponent_bytes, 'big')
if e != 3:
    raise ValueError('Expected RSA exponent 3')

with open('key.enc', 'r') as f:
    y = int(f.read().strip())
with open('file.enc', 'rb') as f:
    ciphertext = base64.b64decode(f.read().strip(), validate=True)

# The chosen key satisfies N < K^3 < 2N, so K^3 = Y + N.
target = y + n
k = cube_root(target)
if k ** 3 != target or pow(k, e, n) != y:
    raise ValueError('RSA ciphertext does not yield an exact cube')

key = k.to_bytes(len(ciphertext), 'big')
plaintext = bytes(c ^ b for c, b in zip(ciphertext, key))
answer = plaintext.decode('utf-8').rstrip('\x00\r\n')
print(answer)
