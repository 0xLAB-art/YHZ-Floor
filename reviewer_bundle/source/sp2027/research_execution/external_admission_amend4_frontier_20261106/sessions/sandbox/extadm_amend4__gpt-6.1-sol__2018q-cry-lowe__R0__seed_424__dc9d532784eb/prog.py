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
    x = 1 << ((value.bit_length() + 2) // 3)
    while True:
        next_x = (2 * x + value // (x * x)) // 3
        if next_x >= x:
            return x
        x = next_x


def main():
    with open('pubkey.pem', 'rb') as f:
        pem = f.read()
    encoded = b''.join(line.strip() for line in pem.splitlines()
                       if not line.startswith(b'-----'))
    der = base64.b64decode(encoded)

    tag, outer, end = read_tlv(der)
    assert tag == 0x30 and end == len(der)
    _, _, offset = read_tlv(outer)
    tag, bit_string, _ = read_tlv(outer, offset)
    assert tag == 0x03 and bit_string[0] == 0
    tag, rsa, _ = read_tlv(bit_string[1:])
    assert tag == 0x30
    tag, modulus_bytes, offset = read_tlv(rsa)
    assert tag == 0x02
    tag, exponent_bytes, _ = read_tlv(rsa, offset)
    assert tag == 0x02
    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')
    assert exponent == 3

    with open('key.enc', 'r', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    cube = encrypted_key + modulus
    key_integer = integer_cube_root(cube)
    assert key_integer ** 3 == cube
    key = key_integer.to_bytes(64, 'big')

    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())
    assert len(ciphertext) == 64
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, key))
    sys.stdout.buffer.write(plaintext + b'\n')


if __name__ == '__main__':
    main()
