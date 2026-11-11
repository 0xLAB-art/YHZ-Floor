import base64
import sys


def read_tlv(data, offset, expected_tag):
    if data[offset] != expected_tag:
        raise ValueError('Unexpected DER tag')
    offset += 1
    length = data[offset]
    offset += 1
    if length & 0x80:
        count = length & 0x7f
        if count == 0:
            raise ValueError('Indefinite DER length')
        length = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + length
    if end > len(data):
        raise ValueError('Truncated DER')
    return data[offset:end], end


def cube_root(n):
    low = 0
    high = 1 << ((n.bit_length() + 2) // 3)
    while high - low > 1:
        middle = (low + high) // 2
        if middle ** 3 <= n:
            low = middle
        else:
            high = middle
    return low


def main():
    with open('pubkey.pem', 'rb') as f:
        encoded = b''.join(line.strip() for line in f
                           if not line.startswith(b'-----'))
    der = base64.b64decode(encoded, validate=True)
    outer, _ = read_tlv(der, 0, 0x30)
    _, position = read_tlv(outer, 0, 0x30)
    bit_string, _ = read_tlv(outer, position, 0x03)
    if bit_string[0] != 0:
        raise ValueError('Unexpected unused bits')
    rsa, _ = read_tlv(bit_string, 1, 0x30)
    modulus, position = read_tlv(rsa, 0, 0x02)
    exponent, _ = read_tlv(rsa, position, 0x02)
    n = int.from_bytes(modulus, 'big')
    e = int.from_bytes(exponent, 'big')
    if e != 3:
        raise ValueError('Expected public exponent 3')

    with open('key.enc', 'rb') as f:
        y = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())

    k = cube_root(y + n)
    if k ** 3 != y + n or pow(k, e, n) != y:
        raise ValueError('RSA cube recovery failed')
    if len(ciphertext) != 64:
        raise ValueError('Expected a 64-byte ciphertext')

    key = k.to_bytes(64, 'big')
    plaintext = bytes(c ^ b for c, b in zip(ciphertext, key))
    sys.stdout.buffer.write(plaintext + b'\n')


if __name__ == '__main__':
    main()
