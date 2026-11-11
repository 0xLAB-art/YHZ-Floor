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


def integer_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while high - low > 1:
        mid = (low + high) // 2
        if mid ** 3 <= value:
            low = mid
        else:
            high = mid
    return low


def main():
    with open('pubkey.pem', 'rb') as f:
        pem = f.read()
    der = base64.b64decode(b''.join(
        line for line in pem.splitlines()
        if not line.startswith(b'-----')
    ))

    _, outer, _ = read_tlv(der)
    _, _, cursor = read_tlv(outer)
    tag, bitstring, _ = read_tlv(outer, cursor)
    assert tag == 3 and bitstring[0] == 0
    _, rsa, _ = read_tlv(bitstring[1:])
    _, modulus_bytes, cursor = read_tlv(rsa)
    _, exponent_bytes, _ = read_tlv(rsa, cursor)
    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')
    assert exponent == 3

    with open('key.enc', 'r', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())
    assert len(ciphertext) == 64

    cube = encrypted_key + modulus
    key_integer = integer_cube_root(cube)
    assert key_integer ** 3 == cube
    assert pow(key_integer, exponent, modulus) == encrypted_key

    key = key_integer.to_bytes(64, 'big')
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))
    print(plaintext.decode('utf-8'))


if __name__ == '__main__':
    main()
