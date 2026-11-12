import base64
import sys


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


def read_public_key():
    with open('pubkey.pem', 'rb') as f:
        encoded = b''.join(line.strip() for line in f
                           if not line.startswith(b'-----'))
    der = base64.b64decode(encoded, validate=True)
    _, outer, _ = read_tlv(der)
    _, _, pos = read_tlv(outer)
    tag, bits, _ = read_tlv(outer, pos)
    if tag != 3 or not bits or bits[0] != 0:
        raise ValueError('Invalid public-key BIT STRING')
    _, rsa, _ = read_tlv(bits, 1)
    _, modulus, pos = read_tlv(rsa)
    _, exponent, _ = read_tlv(rsa, pos)
    return int.from_bytes(modulus, 'big'), int.from_bytes(exponent, 'big')


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
    modulus, exponent = read_public_key()
    if exponent != 3:
        raise ValueError('Expected RSA exponent 3')
    with open('key.enc', 'r', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    target = encrypted_key + modulus
    key = integer_cube_root(target)
    if key ** 3 != target:
        raise ValueError('Encrypted key plus modulus is not a perfect cube')
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read().strip(), validate=True)
    key_bytes = key.to_bytes(len(ciphertext), 'big')
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, key_bytes))
    sys.stdout.buffer.write(plaintext + b'\n')


if __name__ == '__main__':
    main()
