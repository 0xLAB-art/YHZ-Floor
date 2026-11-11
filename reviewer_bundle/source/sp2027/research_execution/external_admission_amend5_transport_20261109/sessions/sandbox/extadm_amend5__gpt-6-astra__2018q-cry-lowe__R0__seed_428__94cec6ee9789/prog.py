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
    return tag, data[pos:end], end


def integer_cube_root(n):
    low = 0
    high = 1 << ((n.bit_length() + 2) // 3)
    while high - low > 1:
        mid = (low + high) // 2
        if mid ** 3 <= n:
            low = mid
        else:
            high = mid
    return low


def main():
    with open('pubkey.pem', 'rb') as f:
        pem = f.read()
    encoded = b''.join(line.strip() for line in pem.splitlines()
                       if not line.startswith(b'-----'))
    der = base64.b64decode(encoded)

    tag, spki, _ = read_tlv(der)
    assert tag == 0x30
    _, _, pos = read_tlv(spki)
    tag, bit_string, _ = read_tlv(spki, pos)
    assert tag == 0x03 and bit_string[0] == 0
    tag, rsa_key, _ = read_tlv(bit_string, 1)
    assert tag == 0x30
    tag, modulus_bytes, pos = read_tlv(rsa_key)
    assert tag == 0x02
    tag, exponent_bytes, _ = read_tlv(rsa_key, pos)
    assert tag == 0x02
    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')
    assert exponent == 3

    with open('key.enc', 'r', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())

    # The prescribed range gives K^3 = encrypted_key + modulus.
    cube = encrypted_key + modulus
    key_integer = integer_cube_root(cube)
    assert key_integer ** 3 == cube
    assert len(ciphertext) == 64
    key = key_integer.to_bytes(64, 'big')
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, key))
    print(plaintext.decode('utf-8'))


if __name__ == '__main__':
    main()
