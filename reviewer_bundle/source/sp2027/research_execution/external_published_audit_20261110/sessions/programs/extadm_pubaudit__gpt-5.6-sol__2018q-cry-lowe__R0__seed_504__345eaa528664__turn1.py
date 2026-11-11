import base64
import sys


def read_tlv(data, offset):
    if offset >= len(data):
        raise ValueError('Truncated DER data')
    tag = data[offset]
    offset += 1
    if offset >= len(data):
        raise ValueError('Missing DER length')
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0 or offset + count > len(data):
            raise ValueError('Invalid DER length')
        length = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + length
    if end > len(data):
        raise ValueError('Truncated DER value')
    return tag, data[offset:end], end


def parse_public_key(pem):
    body = ''.join(
        line.strip()
        for line in pem.splitlines()
        if line.strip() and not line.strip().startswith('-----')
    )
    der = base64.b64decode(body)
    tag, spki, end = read_tlv(der, 0)
    if tag != 0x30 or end != len(der):
        raise ValueError('Invalid public key')

    algorithm_tag, _, offset = read_tlv(spki, 0)
    if algorithm_tag != 0x30:
        raise ValueError('Invalid algorithm identifier')
    tag, bit_string, offset = read_tlv(spki, offset)
    if tag != 0x03 or offset != len(spki) or not bit_string or bit_string[0] != 0:
        raise ValueError('Invalid RSA key bit string')

    tag, rsa_key, end = read_tlv(bit_string, 1)
    if tag != 0x30 or end != len(bit_string):
        raise ValueError('Invalid RSA public key')
    tag, modulus_bytes, offset = read_tlv(rsa_key, 0)
    if tag != 0x02:
        raise ValueError('Missing RSA modulus')
    tag, exponent_bytes, offset = read_tlv(rsa_key, offset)
    if tag != 0x02 or offset != len(rsa_key):
        raise ValueError('Missing RSA exponent')

    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')
    return exponent, modulus


def exact_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while low < high:
        middle = (low + high) // 2
        cube = middle * middle * middle
        if cube < value:
            low = middle + 1
        else:
            high = middle
    if low * low * low != value:
        raise ValueError('Value is not a perfect cube')
    return low


def main():
    with open('pubkey.pem', 'r', encoding='ascii') as handle:
        exponent, modulus = parse_public_key(handle.read())
    if exponent != 3:
        raise ValueError('Unexpected RSA exponent')

    with open('key.enc', 'r', encoding='ascii') as handle:
        encrypted_key = int(handle.read().strip())
    key = exact_cube_root(encrypted_key + modulus)

    with open('file.enc', 'rb') as handle:
        ciphertext = base64.b64decode(handle.read())
    key_bytes = key.to_bytes(len(ciphertext), 'big')
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes))
    sys.stdout.buffer.write(plaintext + b'\n')


if __name__ == '__main__':
    main()
