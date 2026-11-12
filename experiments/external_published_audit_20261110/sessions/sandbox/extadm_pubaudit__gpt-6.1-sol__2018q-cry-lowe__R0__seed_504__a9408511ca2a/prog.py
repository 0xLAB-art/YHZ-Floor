import base64


def read_tlv(data, offset=0):
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + length
    return tag, data[offset:end], end


def integer_cube_root(n):
    x = 1 << ((n.bit_length() + 2) // 3)
    while True:
        next_x = (2 * x + n // (x * x)) // 3
        if next_x >= x:
            return x
        x = next_x


def main():
    with open('pubkey.pem', 'rb') as f:
        pem = f.read()
    encoded = b''.join(line.strip() for line in pem.splitlines()
                       if not line.startswith(b'-----'))
    der = base64.b64decode(encoded)

    _, spki, _ = read_tlv(der)
    _, _, offset = read_tlv(spki)
    tag, bit_string, _ = read_tlv(spki, offset)
    if tag != 0x03 or bit_string[0] != 0:
        raise ValueError('Invalid public key encoding')
    _, rsa_key, _ = read_tlv(bit_string, 1)
    _, modulus_bytes, offset = read_tlv(rsa_key)
    _, exponent_bytes, _ = read_tlv(rsa_key, offset)
    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')
    if exponent != 3:
        raise ValueError('Expected RSA exponent 3')

    with open('key.enc', 'rb') as f:
        encrypted_key = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())

    # The promised range makes K^3 = encrypted_key + modulus.
    cube = encrypted_key + modulus
    key_number = integer_cube_root(cube)
    if key_number ** 3 != cube:
        raise ValueError('Encrypted key does not satisfy the cube condition')
    if len(ciphertext) != 64:
        raise ValueError('Expected a 64-byte ciphertext')

    key = key_number.to_bytes(64, 'big')
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))
    flag = plaintext.decode('utf-8').rstrip('\x00\r\n')
    if '\r' in flag or '\n' in flag:
        raise ValueError('Flag is not a single line')
    print(flag)


if __name__ == '__main__':
    main()
