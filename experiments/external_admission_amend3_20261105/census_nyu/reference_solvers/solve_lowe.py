#!/usr/bin/env python3
"""Reference solver — lowe (CSAW 2018 Quals, crypto).

Criterion-5 verification artifact for Amendment 3.  Stdlib-only; reads exactly
the declared handout files ('pubkey.pem', 'key.enc', 'file.enc') by bare name.

Attack (the construction is stated in the task's own description and
recoverable from the artifact sizes): the 64-byte secret S is XORed with
Y = K^3 mod N where K is a 512-bit integer chosen in (N^(1/3), (2N)^(1/3)).
Hence K^3 = Y + N exactly, so an integer cube root of (Y + N) recovers K with
no factoring; S = file.enc xor K.  The PEM key is parsed with a minimal DER
TLV reader to obtain N.  No answer material is embedded.

No pinned-answer bytes are embedded in this source.
"""

import base64


def tlv(data, offset):
    tag = data[offset]
    offset += 1
    size = data[offset]
    offset += 1
    if size & 0x80:
        count = size & 0x7F
        size = int.from_bytes(data[offset:offset + count], "big")
        offset += count
    return tag, data[offset:offset + size], offset + size


def cube_root(value):
    high = 1 << ((value.bit_length() + 2) // 3)
    low = 0
    while low < high:
        mid = (low + high + 1) // 2
        if mid ** 3 <= value:
            low = mid
        else:
            high = mid - 1
    return low


def main():
    pem = open("pubkey.pem", "rb").read()
    body = b"".join(line for line in pem.splitlines()
                    if not line.strip().startswith(b"-----"))
    der = base64.b64decode(body)
    _, top, _ = tlv(der, 0)
    _, _, offset = tlv(top, 0)          # AlgorithmIdentifier
    _, bitstring, _ = tlv(top, offset)  # subjectPublicKey BIT STRING
    _, rsa, _ = tlv(bitstring[1:], 0)   # RSAPublicKey SEQUENCE
    _, modulus, pos = tlv(rsa, 0)
    _, exponent, _ = tlv(rsa, pos)
    n = int.from_bytes(modulus, "big")
    assert int.from_bytes(exponent, "big") == 3

    y = int(open("key.enc").read().strip())
    k = cube_root(y + n)
    assert k ** 3 == y + n
    key = k.to_bytes(64, "big")

    cipher = base64.b64decode(open("file.enc", "rb").read().strip())
    secret = bytes(c ^ k_byte for c, k_byte in zip(cipher, key))
    print(secret.decode().strip())


if __name__ == "__main__":
    main()
