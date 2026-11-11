import base64


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0:
            raise ValueError('Invalid DER length')
        length = int.from_bytes(data[pos:pos + count], 'big')
        pos += count
    end = pos + length
    if end > len(data):
        raise ValueError('Truncated DER')
    return tag, data[pos:end], end


def exact_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while high - low > 1:
        mid = (low + high) // 2
        if mid ** 3 <= value:
            low = mid
        else:
            high = mid
    if low ** 3 != value:
        raise ValueError('Expected a perfect cube')
    return low


with open('pubkey.pem', 'rb') as f:
    pem_lines = f.read().splitlines()
der = base64.b64decode(b''.join(
    line.strip() for line in pem_lines if not line.startswith(b'-----')
))

_, spki, _ = read_tlv(der)
_, _, pos = read_tlv(spki)
tag, bit_string, _ = read_tlv(spki, pos)
if tag != 3 or bit_string[0] != 0:
    raise ValueError('Invalid public-key BIT STRING')
_, rsa_key, _ = read_tlv(bit_string, 1)
_, modulus_bytes, pos = read_tlv(rsa_key)
_, exponent_bytes, _ = read_tlv(rsa_key, pos)
N = int.from_bytes(modulus_bytes, 'big')
e = int.from_bytes(exponent_bytes, 'big')
if e != 3:
    raise ValueError('Expected exponent 3')

with open('key.enc', 'r', encoding='ascii') as f:
    Y = int(f.read().strip())

# N < K^3 < 2*N, so the RSA reduction subtracts exactly one N.
K = exact_cube_root(Y + N)
if pow(K, e, N) != Y:
    raise ValueError('RSA verification failed')

with open('file.enc', 'rb') as f:
    ciphertext = base64.b64decode(f.read())
if len(ciphertext) != 64:
    raise ValueError('Expected a 64-byte ciphertext')

xor_key = K.to_bytes(64, 'big')
plaintext = bytes(c ^ k for c, k in zip(ciphertext, xor_key))
print(plaintext.decode('utf-8').rstrip('\x00\r\n'))
