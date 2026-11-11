import base64
import sys


def read_tlv(data, offset=0):
    tag = data[offset]
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0:
            raise ValueError('Invalid DER length')
        length = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + length
    if end > len(data):
        raise ValueError('Truncated DER')
    return tag, data[offset:end], end


def integer_cube_root(value):
    lo = 0
    hi = 1 << ((value.bit_length() + 2) // 3)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** 3 <= value:
            lo = mid
        else:
            hi = mid
    return lo


def main():
    with open('pubkey.pem', 'rb') as f:
        pem = f.read()
    der = base64.b64decode(b''.join(
        line.strip() for line in pem.splitlines()
        if not line.startswith(b'-----')
    ))

    tag, spki, _ = read_tlv(der)
    assert tag == 0x30
    _, _, offset = read_tlv(spki)
    tag, bit_string, _ = read_tlv(spki, offset)
    assert tag == 0x03 and bit_string[0] == 0
    tag, rsa_key, _ = read_tlv(bit_string[1:])
    assert tag == 0x30
    tag, modulus_bytes, offset = read_tlv(rsa_key)
    assert tag == 0x02
    tag, exponent_bytes, _ = read_tlv(rsa_key, offset)
    assert tag == 0x02
    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')
    assert exponent == 3

    with open('key.enc', 'rt', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())
    assert len(ciphertext) == 64
    assert 0 <= encrypted_key < modulus

    # The specified range makes K^3 = Y + N exactly.
    cube = encrypted_key + modulus
    key = integer_cube_root(cube)
    if key ** 3 != cube:
        raise ValueError('Y + N is not a perfect cube')

    key_bytes = key.to_bytes(64, 'big')
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_bytes))
    sys.stdout.buffer.write(plaintext.rstrip(b'\x00\r\n') + b'\n')


if __name__ == '__main__':
    main()
