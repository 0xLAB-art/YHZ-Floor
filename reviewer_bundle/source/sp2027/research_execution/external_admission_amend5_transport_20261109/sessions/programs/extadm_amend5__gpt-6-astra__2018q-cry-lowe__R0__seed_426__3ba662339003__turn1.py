import base64
import sys


def read_tlv(data, pos=0):
    if pos + 2 > len(data):
        raise ValueError('Truncated DER')
    tag = data[pos]
    length = data[pos + 1]
    pos += 2
    if length & 0x80:
        count = length & 0x7f
        if count == 0 or pos + count > len(data):
            raise ValueError('Invalid DER length')
        length = int.from_bytes(data[pos:pos + count], 'big')
        pos += count
    end = pos + length
    if end > len(data):
        raise ValueError('Truncated DER value')
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
        lines = f.read().splitlines()
    der = base64.b64decode(b''.join(
        line.strip() for line in lines
        if not line.strip().startswith(b'-----')
    ))
    tag, spki, _ = read_tlv(der)
    if tag != 0x30:
        raise ValueError('Invalid public key')
    _, _, pos = read_tlv(spki)
    tag, bits, _ = read_tlv(spki, pos)
    if tag != 0x03 or not bits or bits[0] != 0:
        raise ValueError('Invalid public-key bit string')
    tag, rsa, _ = read_tlv(bits[1:])
    if tag != 0x30:
        raise ValueError('Invalid RSA key')
    tag, modulus_bytes, pos = read_tlv(rsa)
    if tag != 0x02:
        raise ValueError('Missing modulus')
    tag, exponent_bytes, _ = read_tlv(rsa, pos)
    if tag != 0x02:
        raise ValueError('Missing exponent')
    modulus = int.from_bytes(modulus_bytes, 'big')
    exponent = int.from_bytes(exponent_bytes, 'big')

    with open('key.enc', 'r', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    if exponent != 3 or not 0 <= encrypted_key < modulus:
        raise ValueError('Unexpected RSA parameters')

    target = encrypted_key + modulus
    key_number = integer_cube_root(target)
    if key_number ** 3 != target:
        raise ValueError('Encrypted key plus modulus is not a perfect cube')
    key = key_number.to_bytes(64, 'big')

    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())
    if len(ciphertext) != len(key):
        raise ValueError('Unexpected ciphertext length')
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, key))
    sys.stdout.buffer.write(plaintext + b'\n')


if __name__ == '__main__':
    main()
