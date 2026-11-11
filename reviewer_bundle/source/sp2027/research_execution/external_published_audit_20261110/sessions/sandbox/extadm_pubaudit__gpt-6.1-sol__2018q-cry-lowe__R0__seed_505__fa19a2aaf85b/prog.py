import base64
import sys


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


def main():
    with open('pubkey.pem', 'r', encoding='ascii') as f:
        pem = f.read()
    der = base64.b64decode(''.join(
        line.strip() for line in pem.splitlines()
        if not line.strip().startswith('-----')
    ))

    _, spki, _ = read_tlv(der)
    _, _, offset = read_tlv(spki)
    tag, bit_string, _ = read_tlv(spki, offset)
    if tag != 3 or bit_string[0] != 0:
        raise ValueError('Invalid RSA public key')
    _, rsa_public_key, _ = read_tlv(bit_string[1:])
    _, modulus_bytes, offset = read_tlv(rsa_public_key)
    _, exponent_bytes, _ = read_tlv(rsa_public_key, offset)
    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')
    if exponent != 3:
        raise ValueError('Expected exponent 3')

    with open('key.enc', 'r', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())

    cube = modulus + encrypted_key
    key_integer = integer_cube_root(cube)
    if key_integer ** 3 != cube:
        raise ValueError('N + Y is not a perfect cube')
    if len(ciphertext) != 64:
        raise ValueError('Expected a 64-byte ciphertext')

    key = key_integer.to_bytes(64, 'big')
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, key))
    sys.stdout.write(plaintext.decode('ascii') + '\n')


if __name__ == '__main__':
    main()
