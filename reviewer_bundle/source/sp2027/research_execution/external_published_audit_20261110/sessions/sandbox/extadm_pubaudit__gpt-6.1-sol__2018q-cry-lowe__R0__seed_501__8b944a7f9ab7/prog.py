import base64


def read_tlv(data, pos=0):
    tag = data[pos]
    pos += 1
    length = data[pos]
    pos += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0:
            raise ValueError('Indefinite DER length')
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
        middle = (low + high) // 2
        if middle ** 3 <= value:
            low = middle
        else:
            high = middle
    if low ** 3 != value:
        raise ValueError('Y + N is not a perfect cube')
    return low


def main():
    with open('pubkey.pem', 'rb') as f:
        lines = [line.strip() for line in f.read().splitlines()]
    der = base64.b64decode(b''.join(line for line in lines if line and not line.startswith(b'-----')))

    tag, outer, _ = read_tlv(der)
    assert tag == 0x30
    _, _, pos = read_tlv(outer)
    tag, bits, _ = read_tlv(outer, pos)
    assert tag == 0x03 and bits[0] == 0
    tag, rsa, _ = read_tlv(bits[1:])
    assert tag == 0x30
    tag, modulus_bytes, pos = read_tlv(rsa)
    assert tag == 0x02
    tag, exponent_bytes, _ = read_tlv(rsa, pos)
    assert tag == 0x02
    N = int.from_bytes(modulus_bytes, 'big')
    e = int.from_bytes(exponent_bytes, 'big')
    assert e == 3

    with open('key.enc', 'r', encoding='ascii') as f:
        Y = int(f.read().strip())
    assert 0 <= Y < N
    K = exact_cube_root(Y + N)
    assert pow(K, e, N) == Y
    symmetric_key = K.to_bytes(64, 'big')

    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())
    assert len(ciphertext) == 64
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, symmetric_key))
    print(plaintext.decode('utf-8'))


if __name__ == '__main__':
    main()
