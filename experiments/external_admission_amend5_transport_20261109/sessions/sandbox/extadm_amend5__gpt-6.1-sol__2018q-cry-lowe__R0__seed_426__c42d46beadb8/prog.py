import base64
import re


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


def load_public_key():
    with open('pubkey.pem', 'r', encoding='ascii') as f:
        encoded = ''.join(line.strip() for line in f if not line.startswith('-----'))
    der = base64.b64decode(encoded)
    _, spki, _ = read_tlv(der)
    _, _, offset = read_tlv(spki)
    tag, bits, _ = read_tlv(spki, offset)
    if tag != 3 or bits[0] != 0:
        raise ValueError('Invalid public key')
    _, rsa, _ = read_tlv(bits[1:])
    _, modulus, offset = read_tlv(rsa)
    _, exponent, _ = read_tlv(rsa, offset)
    return int.from_bytes(modulus, 'big'), int.from_bytes(exponent, 'big')


def integer_cube_root(value):
    low = 0
    high = 1 << ((value.bit_length() + 2) // 3)
    while low + 1 < high:
        middle = (low + high) // 2
        if middle ** 3 <= value:
            low = middle
        else:
            high = middle
    return low


def main():
    modulus, exponent = load_public_key()
    if exponent != 3:
        raise ValueError('Expected RSA exponent 3')
    with open('key.enc', 'r', encoding='ascii') as f:
        encrypted_key = int(f.read().strip())
    with open('file.enc', 'rb') as f:
        ciphertext = base64.b64decode(f.read())

    target = encrypted_key + modulus
    key_number = integer_cube_root(target)
    if key_number ** 3 != target or pow(key_number, exponent, modulus) != encrypted_key:
        raise ValueError('RSA key recovery failed')

    key = key_number.to_bytes(64, 'big')
    if len(ciphertext) != len(key):
        raise ValueError('Unexpected ciphertext length')
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, key))

    match = re.search(rb'flag\{[^}\r\n]*\}', plaintext)
    answer = match.group(0) if match else plaintext.rstrip(b'\x00\r\n ')
    print(answer.decode('utf-8'))


if __name__ == '__main__':
    main()
